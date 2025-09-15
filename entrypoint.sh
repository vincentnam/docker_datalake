swift-proxy-server /etc/swift/proxy-server.conf


docker run -it -v ./etc/swift/proxy-server.conf:/etc/swift/proxy-server.conf -v ./etc/swift/swift.conf:/etc/swift/swift.conf swift-base bash