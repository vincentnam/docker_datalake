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
#export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/usr/lib/wsl/lib:/mnt/c/Travail/docker_datalake/.venv/Scripts:/mnt/c/Python313/Scripts/:/mnt/c/Python313/:/mnt/c/Program Files/Common Files/Oracle/Java/javapath:/mnt/c/Program Files (x86)/Common Files/Oracle/Java/java8path:/mnt/c/Program Files (x86)/Common Files/Oracle/Java/javapath:/mnt/c/WINDOWS/system32:/mnt/c/WINDOWS:/mnt/c/WINDOWS/System32/Wbem:/mnt/c/WINDOWS/System32/WindowsPowerShell/v1.0/:/mnt/c/WINDOWS/System32/OpenSSH/:/mnt/c/ProgramData/chocolatey/bin:/mnt/c/Program Files/Go/bin:/mnt/c/TDM-GCC-64/bin:/mnt/c/Program Files/Git/cmd:/mnt/c/Program Files/nodejs/:/mnt/c/Users/covdang/.cargo/bin:/mnt/c/Users/covdang/AppData/Local/Microsoft/WindowsApps:/mnt/c/Users/covdang/AppData/Local/Programs/Microsoft VS Code/bin:/mnt/c/Users/covdang/AppData/Local/Programs/Ollama:/mnt/c/Users/covdang/go/bin:/mnt/c/Program Files (x86)/GnuWin32/bin:/mnt/c/Users/covdang/AppData/Local/GitHubDesktop/bin:/mnt/c/Users/covdang/AppData/Roaming/npm:/usr/bin/site_perl:/usr/bin/vendor_perl:/usr/bin/core_perl:/opt/python/usr/local/bin/

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

