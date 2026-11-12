#!/bin/bash
set -euo pipefail

# ==================== CONFIGURATION PATHS ====================
DISK_CONFIG_PATH="./kubernetes/kubernetes_config"

if [ ! -f "$DISK_CONFIG_PATH/disks.env" ]; then
  echo "Error: $DISK_CONFIG_PATH/disks.env not found. Run the script from the repository root, after copying disks.env.example."
  exit 1
fi
export $(grep -v '^#' $DISK_CONFIG_PATH/disks.env | sed 's/\r$//' | xargs)

if [ -z "$STORAGE_CLASS" ]; then
  echo "Set the storage class in disks.env file."
  exit 1
fi

if [ -z "$DISK_NAME" ]; then
  echo "Set the default disk name in disks.env file."
  exit 1
fi

if [ -z "$DISK_SIZE" ]; then
  echo "Set the default disk size in disks.env file."
  exit 1
fi

if [ -z "$DISK_FS" ]; then
  echo "Set the default filesystem in disks.env file."
  exit 1
fi

if [ -z "$IMG_DIR" ]; then
  echo "Set the image folder in disks.env file."
  exit 1
fi

if [ -z "$DISKS_ROOT" ]; then
  echo "Set the disks root folder in disks.env file."
  exit 1
fi

# Every step can be run again : an interrupted run is simply started again
trap 'echo ""; echo "Interrupted. Run the same command again."; exit 1' SIGINT SIGTERM

# ==================== HELP ====================
help_message() {
  echo "Usage: $0 [OPTIONS]"
  echo "Local disk backed by an image file (fallocate + loop + XFS/ext4), found by the local static provisioner."
  echo "Dev, or degraded production on a single machine."
  echo ""
  echo "Options:"
  echo "  -c, --create         Create the disk : fallocate + format + mount (mounted again at every boot, before k3s)"
  echo "  -g, --grow           Grow an existing disk to --size, online (never shrinks)"
  echo "  -a, --apply          Apply the StorageClass + provisioner, then wait for the PV of the disk"
  echo "  -i, --info           Show the disks of the storage class"
  echo "  --remove             Delete the disk and ALL its data (asks for confirmation)"
  echo "  -n, --name NAME      Disk name (default: $DISK_NAME)"
  echo "  -s, --size SIZE      Disk size, fallocate syntax (default: $DISK_SIZE)"
  echo "  -f, --filetype FS    Filesystem used by --create : xfs or ext4 (default: $DISK_FS)"
  echo "  -h, --help           Show this help"
  echo ""
  echo "Examples:"
  echo "  $0 -c                  # Create d1 with the default size"
  echo "  $0 -c -n d2 -s 50G     # Create d2 of 50G"
  echo "  $0 -c -f ext4          # Create d1 formatted in ext4"
  echo "  $0 -g -s 20G           # Grow d1 to 20G"
  echo "  $0 -cai -n test -s 1G  # Create test + get its PV + show the disks"
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

PARSED=$(getopt -o cgain:s:f:h -l create,grow,apply,info,remove,name:,size:,filetype:,help --name "$0" -- "$@")
if [ $? -ne 0 ]; then
  echo "Error: Invalid arguments."
  exit 1
fi

eval set -- "$PARSED"

CREATE=false
GROW=false
APPLY=false
INFO=false
REMOVE=false
NAME="$DISK_NAME"
SIZE="$DISK_SIZE"
FS_TYPE="$DISK_FS"

while true; do
  case "$1" in
    -c|--create) CREATE=true; shift ;;
    -g|--grow)   GROW=true;   shift ;;
    -a|--apply)  APPLY=true;  shift ;;
    -i|--info)   INFO=true;   shift ;;
    --remove)    REMOVE=true; shift ;;
    -n|--name)   NAME="$2";   shift 2 ;;
    -s|--size)   SIZE="$2";   shift 2 ;;
    -f|--filetype) FS_TYPE="$2"; shift 2 ;;
    -h|--help) help_message; exit 0 ;;
    --) shift; break ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# At least one action
if [ "$CREATE" = false ] && [ "$GROW" = false ] && [ "$APPLY" = false ] && [ "$INFO" = false ] && [ "$REMOVE" = false ]; then
  echo "Error: You must specify at least one action (-c, -g, -a, -i, --remove)"
  help_message
  exit 1
fi

if [ "$REMOVE" = true ]; then
  if [ "$CREATE" = true ] || [ "$GROW" = true ] || [ "$APPLY" = true ] || [ "$INFO" = true ]; then
    echo "Error: --remove cannot be used with another action."
    exit 1
  fi
fi

if [ "$FS_TYPE" != "xfs" ] && [ "$FS_TYPE" != "ext4" ]; then
  echo "Error: unknown filetype « $FS_TYPE » (xfs OR ext4)"
  exit 1
fi

# ==================== DISK PATHS ====================
# DISCOVERY_DIR is the hostDir of the class in local_static_provisioner.yml
IMG="$IMG_DIR/$STORAGE_CLASS/$NAME.img"
DISCOVERY_DIR="$DISKS_ROOT/$STORAGE_CLASS"
UNIT="local-disk-$STORAGE_CLASS-$NAME.service"

# ==================== CHECKS ====================
if [ "$EUID" -eq 0 ]; then
  echo "Error: run the script with your user, it calls sudo itself."
  exit 1
fi

if [ "$(ps -p 1 -o comm=)" != "systemd" ]; then
  echo "Error: systemd is not running (WSL : [boot] systemd=true in /etc/wsl.conf, then wsl --shutdown)."
  exit 1
fi

for cmd in fallocate losetup blkid findmnt mountpoint numfmt; do
  if ! command -v $cmd >/dev/null 2>&1; then
    echo "Error: $cmd is not installed (sudo apt install util-linux coreutils)."
    exit 1
  fi
done

NAME_REGEX='^[a-z0-9]([a-z0-9-]*[a-z0-9])?$'
if ! [[ $NAME =~ $NAME_REGEX ]]; then
  echo "Error: disk name : lowercase letters, digits and '-' only."
  exit 1
fi

if ! [[ $STORAGE_CLASS =~ $NAME_REGEX ]]; then
  echo "Error: storage class : lowercase letters, digits and '-' only."
  exit 1
fi

if [ -n "${DISK_OWNER:-}" ]; then
  if ! [[ $DISK_OWNER =~ ^[0-9]+:[0-9]+$ ]]; then
    echo "Error: DISK_OWNER must be uid:gid (numbers)."
    exit 1
  fi
fi

if [[ $IMG_DIR$DISKS_ROOT == *[[:space:]]* ]]; then
  echo "Error: IMG_DIR and DISKS_ROOT must not contain spaces."
  exit 1
fi

# Only mount points belong under DISKS_ROOT
case "$IMG_DIR/" in
  "$DISKS_ROOT"/*)
    echo "Error: IMG_DIR must not be under $DISKS_ROOT."
    exit 1 ;;
esac

# The image must be on a local Linux filesystem (not /mnt/c, /mnt/h, NFS...)
EXISTING_DIR="$IMG_DIR"
while [ ! -e "$EXISTING_DIR" ]; do
  EXISTING_DIR=$(dirname "$EXISTING_DIR")
done
IMG_DIR_FS=$(findmnt -no FSTYPE -T "$EXISTING_DIR")
if [ "$IMG_DIR_FS" != "ext4" ] && [ "$IMG_DIR_FS" != "xfs" ]; then
  echo "Error: $IMG_DIR is on « $IMG_DIR_FS » : a local ext4 or xfs is needed (not a Windows or network drive)."
  exit 1
fi

# ==================== REMOVE ====================
if [ "$REMOVE" = true ]; then
  if ! sudo test -e "$IMG"; then
    echo "Error: $IMG does not exist."
    exit 1
  fi

  UUID=$(sudo blkid -p -o value -s UUID "$IMG" || true)
  if [ -z "$UUID" ]; then
    echo "Error: no filesystem UUID found on $IMG"
    exit 1
  fi
  MNT="$DISCOVERY_DIR/$NAME-$UUID"

  echo "WARNING : this deletes $IMG and ALL the data of disk $NAME (cannot be undone)."
  read -r -p "Type the disk name to confirm : " ANSWER
  if [ "$ANSWER" != "$NAME" ]; then
    echo "Aborted."
    exit 1
  fi

  if mountpoint -q "$MNT"; then
    if ! sudo umount "$MNT"; then
      echo "Error: $MNT is in use (a Pod still uses it). Delete the Pod / PVC first."
      exit 1
    fi
  fi
  sudo systemctl disable --now "$UNIT" >/dev/null 2>&1 || true
  sudo rm -f "/etc/systemd/system/$UNIT"
  sudo systemctl daemon-reload
  sudo losetup -j "$IMG" | cut -d: -f1 | xargs -r sudo losetup -d
  sudo rm -f "$IMG"
  sudo rmdir "$MNT" 2>/dev/null || true

  echo "Disk $NAME removed."
  echo "Delete its PersistentVolume if it still exists : kubectl get pv, then kubectl delete pv <name>"
fi

# ==================== CREATE ====================
if [ "$CREATE" = true ]; then
  if grep -qi microsoft /proc/version; then
    echo "WARNING : WSL : the space is reserved inside Linux, but the Windows .vhdx underneath grows on demand."
  fi

  # fallocate really reserves the blocks (truncate reserves nothing)
  if sudo test -e "$IMG"; then
    echo "Image already exists : $IMG, no fallocate."
  else
    echo "Reserving $SIZE : $IMG"
    sudo mkdir -p "$IMG_DIR/$STORAGE_CLASS"
    sudo fallocate -l "$SIZE" "$IMG"
    sudo chmod 600 "$IMG"
  fi

  # An existing filesystem is never formatted again
  CURRENT_FS=$(sudo blkid -p -o value -s TYPE "$IMG" || true)
  if [ -z "$CURRENT_FS" ]; then
    echo "Formatting $FS_TYPE..."
    if [ "$FS_TYPE" = "xfs" ]; then
      if ! command -v mkfs.xfs >/dev/null 2>&1; then
        echo "Error: mkfs.xfs is not installed (sudo apt install xfsprogs)."
        exit 1
      fi
      sudo mkfs.xfs -q -L "${NAME:0:12}" "$IMG"
    fi
    if [ "$FS_TYPE" = "ext4" ]; then
      if ! command -v mkfs.ext4 >/dev/null 2>&1; then
        echo "Error: mkfs.ext4 is not installed (sudo apt install e2fsprogs)."
        exit 1
      fi
      # -m 0 : no blocks kept for root on a data disk
      sudo mkfs.ext4 -q -F -m 0 -L "${NAME:0:12}" "$IMG"
    fi
  elif [ "$CURRENT_FS" = "$FS_TYPE" ]; then
    echo "Already formatted in $CURRENT_FS."
  else
    echo "Error: $IMG already holds a « $CURRENT_FS » filesystem (asked : $FS_TYPE)."
    echo "       Remove the disk first (--remove) to create it again in $FS_TYPE."
    exit 1
  fi

  if [ "$FS_TYPE" = "ext4" ]; then
    echo "WARNING : ext4 limits Swift object metadata (~4 KB of xattrs per object) : XFS is recommended in production."
  fi

  # The UUID is part of the mount path : the provisioner names the PV from it
  UUID=$(sudo blkid -p -o value -s UUID "$IMG" || true)
  if [ -z "$UUID" ]; then
    echo "Error: no filesystem UUID found on $IMG"
    exit 1
  fi
  MNT="$DISCOVERY_DIR/$NAME-$UUID"

  for OLD_MNT in "$DISCOVERY_DIR/$NAME"-*; do
    if [ -e "$OLD_MNT" ] && [ "$OLD_MNT" != "$MNT" ]; then
      echo "WARNING : old mount point for « $NAME » : $OLD_MNT (check it is no longer used)"
    fi
  done

  # systemd unit : attaches the image to a loop device and mounts it, at every boot, before k3s.
  # direct-io avoids caching the data twice ; it may fail without blocking the mount (- prefix).
  # \$\$ becomes $$ in the file, which systemd gives to the shell as a plain $
  echo "Writing systemd unit $UNIT..."
  sudo tee "/etc/systemd/system/$UNIT" >/dev/null << EOF
[Unit]
Description=Local disk $NAME ($STORAGE_CLASS) : $IMG
After=local-fs.target
Before=k3s.service k3s-agent.service
ConditionPathExists=$IMG

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStartPre=/bin/sh -c 'mkdir -p $MNT'
ExecStart=/bin/sh -c 'losetup -j $IMG | grep -q . || losetup --find $IMG'
ExecStart=-/bin/sh -c 'losetup --direct-io=on \$\$(losetup -j $IMG | cut -d: -f1 | head -n1)'
ExecStart=/bin/sh -c 'mountpoint -q $MNT || mount -o noatime \$\$(losetup -j $IMG | cut -d: -f1 | head -n1) $MNT'
ExecStop=-/bin/sh -c 'umount $MNT'
ExecStopPost=-/bin/sh -c 'losetup -j $IMG | cut -d: -f1 | xargs -r losetup -d'

[Install]
WantedBy=multi-user.target
EOF
  sudo systemctl daemon-reload
  sudo systemctl enable "$UNIT" >/dev/null 2>&1

  if mountpoint -q "$MNT"; then
    echo "Already mounted : $MNT"
  else
    sudo systemctl restart "$UNIT"
  fi
  if ! mountpoint -q "$MNT"; then
    echo "Error: $MNT is not mounted, see : journalctl -u $UNIT"
    exit 1
  fi

  # Owner of the disk root, set once : no chown -R when the pods start
  if [ -n "${DISK_OWNER:-}" ]; then
    sudo chown "$DISK_OWNER" "$MNT"
    echo "Disk root owned by $DISK_OWNER"
  fi

  echo "Disk ready : $MNT"
  echo "WARNING : a PVC only binds if its request is <= the PV capacity : request a bit less than $SIZE (e.g. 9Gi for 10G)."
fi

# ==================== GROW ====================
if [ "$GROW" = true ]; then
  if ! sudo test -e "$IMG"; then
    echo "Error: $IMG does not exist (create it with -c)."
    exit 1
  fi

  UUID=$(sudo blkid -p -o value -s UUID "$IMG" || true)
  if [ -z "$UUID" ]; then
    echo "Error: no filesystem UUID found on $IMG"
    exit 1
  fi
  MNT="$DISCOVERY_DIR/$NAME-$UUID"

  if ! mountpoint -q "$MNT"; then
    echo "Error: $MNT is not mounted (sudo systemctl start $UNIT)."
    exit 1
  fi

  # The existing filesystem decides, not --filetype
  CURRENT_FS=$(sudo blkid -p -o value -s TYPE "$IMG" || true)
  if [ "$CURRENT_FS" = "xfs" ]; then
    if ! command -v xfs_growfs >/dev/null 2>&1; then
      echo "Error: xfs_growfs is not installed (sudo apt install xfsprogs)."
      exit 1
    fi
  fi
  if [ "$CURRENT_FS" = "ext4" ]; then
    if ! command -v resize2fs >/dev/null 2>&1; then
      echo "Error: resize2fs is not installed (sudo apt install e2fsprogs)."
      exit 1
    fi
  fi

  # fallocate never shrinks : a smaller size changes nothing
  SIZE_BEFORE=$(sudo stat -c %s "$IMG")
  sudo fallocate -l "$SIZE" "$IMG"
  SIZE_AFTER=$(sudo stat -c %s "$IMG")

  if [ "$SIZE_AFTER" -le "$SIZE_BEFORE" ]; then
    echo "Nothing to grow : $NAME is already $(numfmt --to=iec "$SIZE_BEFORE") (>= $SIZE)."
  else
    # The loop device reads the new size of its image, then the filesystem grows while mounted
    LOOP_DEV=$(sudo losetup -j "$IMG" | cut -d: -f1 | head -n1)
    sudo losetup -c "$LOOP_DEV"
    if [ "$CURRENT_FS" = "xfs" ]; then
      sudo xfs_growfs "$MNT" >/dev/null
    fi
    if [ "$CURRENT_FS" = "ext4" ]; then
      sudo resize2fs "$LOOP_DEV" >/dev/null
    fi
    echo "Disk $NAME ($CURRENT_FS) grown : $(numfmt --to=iec "$SIZE_BEFORE") -> $(numfmt --to=iec "$SIZE_AFTER")"
    echo "The PV still shows its old capacity : display only, not a limit."
    echo "Several Swift devices ? Update the weight of this device in the rings, then rebalance."
  fi
fi

# ==================== APPLY ====================
if [ "$APPLY" = true ]; then
  if ! command -v kubectl >/dev/null 2>&1; then
    echo "Error: kubectl is not installed."
    exit 1
  fi

  if ! kubectl get nodes >/dev/null 2>&1; then
    echo "Error: no reachable cluster with KUBECONFIG=${KUBECONFIG:-}"
    exit 1
  fi

  echo "Applying the StorageClass and the local static provisioner..."
  kubectl apply -f $DISK_CONFIG_PATH/storage_class_swift_disk.yml
  kubectl apply -f $DISK_CONFIG_PATH/local_static_provisioner.yml
  kubectl -n kube-system rollout status daemonset/local-static-provisioner --timeout=180s

  if ! sudo test -e "$IMG"; then
    echo "No disk $NAME yet : its PV will appear once the disk is created (-c)."
  else
    UUID=$(sudo blkid -p -o value -s UUID "$IMG" || true)
    if [ -z "$UUID" ]; then
      echo "Error: no filesystem UUID found on $IMG"
      exit 1
    fi
    MNT="$DISCOVERY_DIR/$NAME-$UUID"

    if ! mountpoint -q "$MNT"; then
      echo "Error: $MNT is not mounted (sudo systemctl start $UNIT) : no PV can be created."
      exit 1
    fi

    # The provisioner creates the PV by itself, a few seconds after the mount
    echo "Waiting for the PV of disk $NAME ($MNT)..."
    PV=""
    WAIT_END=$((SECONDS + 90))
    while [ -z "$PV" ]; do
      PV=$(kubectl get pv -o jsonpath='{range .items[*]}{.metadata.name}{" "}{.spec.local.path}{"\n"}{end}' | awk -v p="$MNT" '$2 == p {print $1}' || true)
      if [ -z "$PV" ]; then
        if [ "$SECONDS" -ge "$WAIT_END" ]; then
          echo "Error: no PV after 90 s. Check that « $STORAGE_CLASS » is in storageClassMap of local_static_provisioner.yml,"
          echo "       then : kubectl -n kube-system logs daemonset/local-static-provisioner"
          exit 1
        fi
        sleep 5
      fi
    done
    kubectl get pv "$PV"
  fi
fi

# ==================== INFO ====================
if [ "$INFO" = true ]; then
  echo "Disks of class $STORAGE_CLASS ($IMG_DIR/$STORAGE_CLASS) :"

  if ! ls "$IMG_DIR/$STORAGE_CLASS"/*.img >/dev/null 2>&1; then
    echo "  (none)"
  else
    printf '  %-10s %-5s %-8s %-8s %-8s %-4s %s\n' NAME TYPE IMAGE FS USED DIO MOUNT
    for INFO_IMG in "$IMG_DIR/$STORAGE_CLASS"/*.img; do
      INFO_NAME=$(basename "$INFO_IMG" .img)
      INFO_SIZE=$(numfmt --to=iec "$(sudo stat -c %s "$INFO_IMG")")
      INFO_TYPE=$(sudo blkid -p -o value -s TYPE "$INFO_IMG" || true)
      if [ -z "$INFO_TYPE" ]; then
        INFO_TYPE="-"
      fi
      INFO_UUID=$(sudo blkid -p -o value -s UUID "$INFO_IMG" || true)
      INFO_MNT="$DISCOVERY_DIR/$INFO_NAME-$INFO_UUID"

      if [ -n "$INFO_UUID" ] && mountpoint -q "$INFO_MNT"; then
        read -r INFO_FS INFO_USED < <(df -B1 --output=size,used "$INFO_MNT" | tail -n1)
        INFO_FS=$(numfmt --to=iec "$INFO_FS")
        INFO_USED=$(numfmt --to=iec "$INFO_USED")
        INFO_LOOP=$(sudo losetup -j "$INFO_IMG" | cut -d: -f1 | head -n1)
        INFO_DIO=$(sudo losetup -n -l -O DIO "$INFO_LOOP" | tr -d ' ')
        if [ "$INFO_DIO" = "1" ]; then
          INFO_DIO="on"
        else
          INFO_DIO="off"
        fi
      else
        INFO_FS="-"
        INFO_USED="-"
        INFO_DIO="-"
        INFO_MNT="(not mounted)"
      fi
      printf '  %-10s %-5s %-8s %-8s %-8s %-4s %s\n' "$INFO_NAME" "$INFO_TYPE" "$INFO_SIZE" "$INFO_FS" "$INFO_USED" "$INFO_DIO" "$INFO_MNT"
    done
  fi

  echo ""
  echo "PersistentVolumes : kubectl get pv"
fi

echo "Script completed successfully."
