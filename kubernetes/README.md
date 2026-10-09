Problem from wsl2 : 

Disk d was mounted in /mnt causin error in disk creation : 

    sudo mount --rbind /mnt/disks /mnt/disks
    sudo mount --make-rshared /mnt/disks

Only for test purpose, don't deploy this architecture in wsl.