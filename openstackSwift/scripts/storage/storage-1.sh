#!/bin/bash


get_loop_for_device_number() {
  local number=""
  local output
  output=
  echo "null"
}


ls /internal_dev
mkdir -p /srv/node/swift-storage-d-1 /internal_dev

truncate --size 1G /internal_dev/swift-storage-d-1
mkfs.xfs -f -L size=512 /internal_dev/swift-storage-d-1
losetup -f /internal_dev/swift-storage-d-1 -v
losetup

mount -t xfs -o noatime  /dev/loop0 /srv/node/swift-storage-d-1

#truncate -s 1GB /internal_dev/;
#echo "    created storage device /internal_dev/ of 1GB";
#export PATH=/home/vincentnam/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/usr/lib/wsl/lib:/mnt/c/Program Files/Microsoft/jdk-17.0.14.7-hotspot/bin:/mnt/c/WINDOWS/system32:/mnt/c/WINDOWS:/mnt/c/WINDOWS/System32/Wbem:/mnt/c/WINDOWS/System32/WindowsPowerShell/v1.0/:/mnt/c/WINDOWS/System32/OpenSSH/:/mnt/c/Program Files/dotnet/:/mnt/c/Program Files/NVIDIA Corporation/NVIDIA app/NvDLISR:/mnt/c/Program Files (x86)/NVIDIA Corporation/PhysX/Common:/mnt/c/Program Files/Docker/Docker/resources/bin:/mnt/c/ProgramData/chocolatey/bin:/mnt/c/Program Files/nodejs/:/mnt/c/Program Files/Git/cmd:/mnt/c/Program Files/PuTTY/:/mnt/c/Users/dangv/AppData/Local/Android/Sdk/platform-tools:/mnt/c/Users/dangv/AppData/Local/Android/Sdk/tools:/mnt/c/Users/dangv/AppData/Local/Programs/Python/Python313/Scripts/:/mnt/c/Users/dangv/AppData/Local/Programs/Python/Python313/:/mnt/c/Users/dangv/AppData/Local/Programs/Python/Launcher/:/mnt/c/Users/dangv/AppData/Local/Microsoft/WindowsApps:/mnt/c/Users/dangv/AppData/Local/Programs/Microsoft VS Code/bin:/mnt/c/Users/dangv/.lmstudio/bin:/mnt/c/Users/dangv/AppData/Local/Programs/Ollama:/mnt/c/Users/dangv/AppData/Roaming/npm:/mnt/c/Users/dangv/AppData/Local/GitHubDesktop/bin:/snap/bin:/opt/python/usr/local/bin/

#echo "[[ creating directories ]]"


mkdir -p /srv/node/swift-storage-d-1

chown -R swift:swift /srv/node


sed -i -e 's/RSYNC_ENABLE=false/RSYNC_ENABLE=true/g' /etc/default/rsync
rm /run/rsyslogd.pid
## Start rsync
/etc/init.d/rsync start

## Start memcached
/etc/init.d/memcached start

## Restart rsyslog
rsyslogd

swift-account-server /etc/swift/account/account-1.conf verbose &
swift-object-server /etc/swift/object/object-1.conf verbose &
swift-container-server /etc/swift/container/container-1.conf &
wait

