




Rocky Linux 9 - to install dbus-python (pip install dbus-python)
    dnf install -y dbus-devel glib2-devel python3.12-devel gcc pkgconf-pkg-config 


    pip install dbus-python docker











## Globals.yml configuration : 


Ip configuration that worked : ip a
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet 10.255.255.254/32 brd 10.255.255.254 scope global lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host 
       valid_lft forever preferred_lft forever
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether 00:15:5d:dc:c7:30 brd ff:ff:ff:ff:ff:ff
    inet 172.31.204.48/20 brd 172.31.207.255 scope global eth0
       valid_lft forever preferred_lft forever
    inet 127.0.0.1/32 scope global eth0
       valid_lft forever preferred_lft forever
    inet6 fe80::215:5dff:fedc:c730/64 scope link 
       valid_lft forever preferred_lft forever
48: br-9ad6d32cd7aa: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN group default 
    link/ether ce:0c:9d:e7:d7:f3 brd ff:ff:ff:ff:ff:ff
    inet 172.18.0.1/16 brd 172.18.255.255 scope global br-9ad6d32cd7aa
       valid_lft forever preferred_lft forever
    inet6 fe80::cc0c:9dff:fee7:d7f3/64 scope link 
       valid_lft forever preferred_lft forever
59: br-7f84d76eb877: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN group default 
    link/ether 26:7b:50:cd:e0:d0 brd ff:ff:ff:ff:ff:ff
    inet 172.19.0.1/16 brd 172.19.255.255 scope global br-7f84d76eb877
       valid_lft forever preferred_lft forever
    inet6 fe80::247b:50ff:fecd:e0d0/64 scope link 
       valid_lft forever preferred_lft forever
