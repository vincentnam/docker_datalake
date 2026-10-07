#!/bin/bash
# Local disk backed by an image file, for the local static provisioner :
#   image (fallocate) → loop (direct-io) → XFS → mounted on DISKS_ROOT/STORAGE_CLASS/<name>-<uuid>
# The provisioner sees the mount point and creates the PersistentVolume by itself.
#
# Dev, or degraded production on a single machine. With a real block device
# (disk, partition, LVM), use the device script instead.
set -euo pipefail

# ==================== CONFIGURATION ====================
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONF_FILE="$SCRIPT_DIR/disks.env"

if [ ! -f "$CONF_FILE" ]; then
  echo "Error: $CONF_FILE not found."
  exit 1
fi
export $(grep -v '^#' "$CONF_FILE" | sed 's/\r$//' | xargs)

for var in STORAGE_CLASS DISK_NAME DISK_SIZE IMG_DIR DISKS_ROOT; do
  if [ -z "${!var:-}" ]; then
    echo "Set $var in $CONF_FILE."
    exit 1
  fi
done
DISK_OWNER="${DISK_OWNER:-}"

# Every step is idempotent : an interrupted run is simply run again
trap 'echo ""; echo "Interrupted. Run the same command again : every step is idempotent."; exit 1' SIGINT SIGTERM

# ==================== HELP ====================
help_message() {
  echo "Usage: $0 [OPTIONS]"
  echo "Local disk backed by a fallocate image (loop + XFS), discovered by the local static provisioner."
  echo ""
  echo "Options:"
  echo "  -c, --create       Create the disk : fallocate + XFS + mount (again at every boot, before k3s)"
  echo "  -g, --grow         Grow an existing disk to --size, online (XFS can only grow)"
  echo "  -i, --info         Show the disks of the storage class"
  echo "  --remove           Delete the disk and ALL its data (asks for confirmation)"
  echo "  -n, --name NAME    Disk name (default: $DISK_NAME)"
  echo "  -s, --size SIZE    Disk size, fallocate syntax (default: $DISK_SIZE)"
  echo "  -h, --help         Show this help"
  echo ""
  echo "Defaults are read from $CONF_FILE"
  echo ""
  echo "Examples:"
  echo "  $0 -c                  # Create d1 with the default size"
  echo "  $0 -c -n d2 -s 50G     # Create d2 of 50G"
  echo "  $0 -g -s 20G           # Grow d1 to 20G"
  echo "  $0 -ci                 # Create + show the disks"
  echo "  $0 --remove -n d2      # Delete d2"
}

# No args → help
if [ $# -eq 0 ]; then
  help_message
  exit 0
fi

# Parse arguments
if ! command -v getopt >/dev/null 2>&1; then
  echo "Error: getopt is not installed."
  exit 1
fi

if ! PARSED=$(getopt -o cgin:s:h -l create,grow,info,remove,name:,size:,help --name "$0" -- "$@"); then
  echo "Error: Invalid arguments."
  exit 1
fi

eval set -- "$PARSED"

CREATE=false
GROW=false
INFO=false
REMOVE=false
NAME="$DISK_NAME"
SIZE="$DISK_SIZE"

while true; do
  case "$1" in
    -c|--create) CREATE=true; shift ;;
    -g|--grow)   GROW=true;   shift ;;
    -i|--info)   INFO=true;   shift ;;
    --remove)    REMOVE=true; shift ;;
    -n|--name)   NAME="$2";   shift 2 ;;
    -s|--size)   SIZE="$2";   shift 2 ;;
    -h|--help) help_message; exit 0 ;;
    --) shift; break ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# At least one action
if [ "$CREATE" = false ] && [ "$GROW" = false ] && [ "$INFO" = false ] && [ "$REMOVE" = false ]; then
  echo "Error: You must specify at least one action (-c, -g, -i, --remove)"
  help_message
  exit 1
fi

if [ "$REMOVE" = true ] && { [ "$CREATE" = true ] || [ "$GROW" = true ] || [ "$INFO" = true ]; }; then
  echo "Error: --remove cannot be combined with another action."
  exit 1
fi

# ==================== PATHS ====================
IMG="$IMG_DIR/$STORAGE_CLASS/$NAME.img"
DISCOVERY_DIR="$DISKS_ROOT/$STORAGE_CLASS"     # = hostDir of the class in local_static_provisioner.yml
UNIT="local-disk-$STORAGE_CLASS-$NAME.service"

# ==================== CHECKS ====================
if [ "$EUID" -eq 0 ]; then
  echo "Error: run the script as your user, it calls sudo itself."
  exit 1
fi

if [ "$(ps -p 1 -o comm=)" != systemd ]; then
  echo "Error: systemd is not running (WSL : [boot] systemd=true in /etc/wsl.conf, then wsl --shutdown)."
  exit 1
fi

for cmd in fallocate losetup blkid findmnt mountpoint numfmt; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Error: $cmd is not installed (sudo apt install util-linux coreutils)."
    exit 1
  fi
done
for cmd in mkfs.xfs xfs_growfs; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Error: $cmd is not installed (sudo apt install xfsprogs)."
    exit 1
  fi
done

NAME_REGEX='^[a-z0-9]([a-z0-9-]*[a-z0-9])?$'
if ! [[ $NAME =~ $NAME_REGEX ]] || ! [[ $STORAGE_CLASS =~ $NAME_REGEX ]]; then
  echo "Error: disk name and storage class : lowercase letters, digits and '-' only."
  exit 1
fi

if [ -n "$DISK_OWNER" ] && ! [[ $DISK_OWNER =~ ^[0-9]+:[0-9]+$ ]]; then
  echo "Error: DISK_OWNER must be uid:gid (numeric)."
  exit 1
fi

if [[ $IMG_DIR$DISKS_ROOT == *[[:space:]]* ]]; then
  echo "Error: IMG_DIR and DISKS_ROOT must not contain spaces."
  exit 1
fi

case "$IMG_DIR/" in
  "$DISKS_ROOT"/*)
    echo "Error: IMG_DIR must not be under $DISKS_ROOT : only mount points belong there."
    exit 1 ;;
esac

# The image must live on a local Linux filesystem (not /mnt/c, /mnt/h, NFS...)
dir="$IMG_DIR"
while [ ! -e "$dir" ]; do dir=$(dirname "$dir"); done
fstype=$(findmnt -no FSTYPE -T "$dir")
if [ "$fstype" != ext4 ] && [ "$fstype" != xfs ]; then
  echo "Error: $IMG_DIR is on « $fstype » : a local ext4 or xfs is required (not a Windows or network drive)."
  exit 1
fi

# ==================== FUNCTIONS ====================
# Sets UUID and MNT : the UUID is part of the mount path (provisioner best practice)
resolve_mount() {
  UUID=$(sudo blkid -p -o value -s UUID "$IMG" || true)
  if [ -z "$UUID" ]; then
    echo "Error: no filesystem UUID found on $IMG"
    exit 1
  fi
  MNT="$DISCOVERY_DIR/$NAME-$UUID"
}

loop_device() {
  sudo losetup -j "$1" | cut -d: -f1 | head -n1
}

write_unit() {
  echo "Writing systemd unit $UNIT (mount replayed at every boot, before k3s)..."
  # \$\$ becomes $$ in the file, which systemd hands to the shell as a plain $
  sudo tee "/etc/systemd/system/$UNIT" >/dev/null <<EOF
[Unit]
Description=Local disk $NAME ($STORAGE_CLASS) : $IMG
After=local-fs.target
Before=k3s.service k3s-agent.service
ConditionPathExists=$IMG

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStartPre=/bin/sh -c 'mkdir -p $MNT'
# 1. attach the image to a loop device (unless already attached)
ExecStart=/bin/sh -c 'losetup -j $IMG | grep -q . || losetup --find $IMG'
# 2. direct-io avoids caching the data twice ; a failure is not blocking (- prefix)
ExecStart=-/bin/sh -c 'losetup --direct-io=on \$\$(losetup -j $IMG | cut -d: -f1 | head -n1)'
# 3. mount
ExecStart=/bin/sh -c 'mountpoint -q $MNT || mount -o noatime \$\$(losetup -j $IMG | cut -d: -f1 | head -n1) $MNT'
ExecStop=-/bin/sh -c 'umount $MNT'
ExecStopPost=-/bin/sh -c 'losetup -j $IMG | cut -d: -f1 | xargs -r losetup -d'

[Install]
WantedBy=multi-user.target
EOF
  sudo systemctl daemon-reload
  sudo systemctl enable "$UNIT" >/dev/null 2>&1
}

create_disk() {
  if grep -qi microsoft /proc/version; then
    echo "WARNING : WSL : the space is reserved inside Linux, but the Windows .vhdx underneath grows on demand."
  fi

  # Image : fallocate really reserves the blocks (truncate would reserve nothing)
  if sudo test -e "$IMG"; then
    echo "Image already exists : $IMG ($(numfmt --to=iec "$(sudo stat -c %s "$IMG")")), no fallocate."
  else
    echo "Reserving $SIZE : $IMG"
    sudo mkdir -p "$(dirname "$IMG")"
    sudo fallocate -l "$SIZE" "$IMG"
    sudo chmod 600 "$IMG"
  fi

  # Filesystem : never reformat an existing one
  local fs
  fs=$(sudo blkid -p -o value -s TYPE "$IMG" || true)
  case "$fs" in
    "")  echo "Formatting XFS..."
         sudo mkfs.xfs -q -L "${NAME:0:12}" "$IMG" ;;
    xfs) echo "Already formatted in XFS." ;;
    *)   echo "Error: $IMG already holds a « $fs » filesystem : refusing to reformat it."
         exit 1 ;;
  esac
  resolve_mount

  local old
  for old in "$DISCOVERY_DIR/$NAME"-*; do
    if [ -e "$old" ] && [ "$old" != "$MNT" ]; then
      echo "WARNING : old mount point for « $NAME » : $old (check it is no longer used)"
    fi
  done

  # Mount, through the systemd unit
  write_unit
  if mountpoint -q "$MNT"; then
    echo "Already mounted : $MNT"
  else
    sudo systemctl restart "$UNIT"    # restart = start when the unit is inactive
  fi
  if ! mountpoint -q "$MNT"; then
    echo "Error: $MNT is not mounted, see : journalctl -u $UNIT"
    exit 1
  fi

  # Owner of the disk root : once, never a chown -R at startup
  if [ -n "$DISK_OWNER" ]; then
    sudo chown "$DISK_OWNER" "$MNT"
    echo "Disk root owned by $DISK_OWNER"
  fi

  echo "Disk ready : $MNT"
  echo "The provisioner creates the PV within a few seconds : kubectl get pv"
  echo "WARNING : a PVC only binds if its request is <= the PV capacity : request a bit less than $SIZE (e.g. 9Gi for 10G)."
}

grow_disk() {
  if ! sudo test -e "$IMG"; then
    echo "Error: $IMG does not exist (create it with -c)."
    exit 1
  fi
  resolve_mount
  if ! mountpoint -q "$MNT"; then
    echo "Error: $MNT is not mounted (sudo systemctl start $UNIT)."
    exit 1
  fi

  local before after loopdev
  before=$(sudo stat -c %s "$IMG")
  sudo fallocate -l "$SIZE" "$IMG"      # a smaller size changes nothing : fallocate never shrinks
  after=$(sudo stat -c %s "$IMG")
  if [ "$after" -le "$before" ]; then
    echo "Nothing to grow : $NAME is already $(numfmt --to=iec "$before") (>= $SIZE). XFS can only grow."
    return
  fi

  loopdev=$(loop_device "$IMG")
  sudo losetup -c "$loopdev"            # the loop device re-reads the size of its image
  sudo xfs_growfs "$MNT" >/dev/null     # XFS grows while mounted
  echo "Disk $NAME grown : $(numfmt --to=iec "$before") -> $(numfmt --to=iec "$after")"
  echo "The PV still shows its old capacity : display only, not a limit."
  echo "Several Swift devices ? Update the weight of this device in the rings, then rebalance."
}

info_disks() {
  echo "Disks of class $STORAGE_CLASS ($IMG_DIR/$STORAGE_CLASS) :"
  shopt -s nullglob
  local imgs=("$IMG_DIR/$STORAGE_CLASS"/*.img)
  shopt -u nullglob
  if [ ${#imgs[@]} -eq 0 ]; then
    echo "  (none)"
    return
  fi

  local img name uuid mnt image fs used dio loopdev
  printf '  %-10s %-8s %-8s %-8s %-4s %s\n' NAME IMAGE FS USED DIO MOUNT
  for img in "${imgs[@]}"; do
    name=$(basename "$img" .img)
    image=$(numfmt --to=iec "$(sudo stat -c %s "$img")")
    uuid=$(sudo blkid -p -o value -s UUID "$img" || true)
    mnt="$DISCOVERY_DIR/$name-$uuid"
    if [ -n "$uuid" ] && mountpoint -q "$mnt"; then
      read -r fs used < <(df -B1 --output=size,used "$mnt" | tail -n1)
      fs=$(numfmt --to=iec "$fs")
      used=$(numfmt --to=iec "$used")
      loopdev=$(loop_device "$img")
      dio=$(sudo losetup -n -l -O DIO "$loopdev" | tr -d ' ')
      [ "$dio" = 1 ] && dio=on || dio=off
    else
      fs=-; used=-; dio=-; mnt="(not mounted)"
    fi
    printf '  %-10s %-8s %-8s %-8s %-4s %s\n' "$name" "$image" "$fs" "$used" "$dio" "$mnt"
  done
  echo ""
  echo "PersistentVolumes : kubectl get pv"
}

remove_disk() {
  if ! sudo test -e "$IMG"; then
    echo "Error: $IMG does not exist."
    exit 1
  fi
  resolve_mount

  echo "WARNING : this deletes $IMG and ALL the data of disk $NAME (irreversible)."
  local answer
  read -r -p "Type the disk name to confirm : " answer
  if [ "$answer" != "$NAME" ]; then
    echo "Aborted."
    exit 1
  fi

  if mountpoint -q "$MNT" && ! sudo umount "$MNT"; then
    echo "Error: $MNT is in use (a Pod still uses it). Delete the Pod / PVC first."
    exit 1
  fi
  sudo systemctl disable --now "$UNIT" >/dev/null 2>&1 || true
  sudo rm -f "/etc/systemd/system/$UNIT"
  sudo systemctl daemon-reload
  sudo losetup -j "$IMG" | cut -d: -f1 | xargs -r sudo losetup -d
  sudo rm -f "$IMG"
  sudo rmdir "$MNT" 2>/dev/null || true

  echo "Disk $NAME removed."
  echo "Delete its PersistentVolume if it still exists : kubectl get pv, then kubectl delete pv <name>"
}

# ==================== REMOVE ====================
if [ "$REMOVE" = true ]; then
  remove_disk
fi

# ==================== CREATE ====================
if [ "$CREATE" = true ]; then
  create_disk
fi

# ==================== GROW ====================
if [ "$GROW" = true ]; then
  grow_disk
fi

# ==================== INFO ====================
if [ "$INFO" = true ]; then
  info_disks
fi

echo "Script completed successfully."
