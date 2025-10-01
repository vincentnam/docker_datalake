#!/bin/bash
set -e
cd /etc/swift
swift-ring-builder account.builder create 18 1 1
swift-ring-builder account.builder add r1z1-10.5.3.1:6002/sdb0 100
swift-ring-builder account.builder rebalance
swift-ring-builder container.builder create 18 1 1
swift-ring-builder container.builder add r1z1-10.5.4.1:6001/sdb0 100
swift-ring-builder container.builder rebalance
swift-ring-builder object.builder create 18 3 1
swift-ring-builder object.builder add r1z1-10.5.10.1:6000/sda1 100
swift-ring-builder object.builder add r1z1-10.5.10.2:6000/sda1 100
swift-ring-builder object.builder add r1z1-10.5.10.3:6000/sda1 100
swift-ring-builder object.builder rebalance
chown -R swift:swift *.ring.gz *.builder
echo "Rings built"