Be sure to have docker-ce version installed (needed for docker compose command) (see https://docs.docker.com/engine/install/ubuntu/)
Config of docker version used during tests : 

Client: Docker Engine - Community
 Version:           23.0.1
 API version:       1.42
 Go version:        go1.19.5
 Git commit:        a5ee5b1
 Built:             Thu Feb  9 19:46:56 2023
 OS/Arch:           linux/amd64
 Context:           default

Server: Docker Engine - Community
 Engine:
  Version:          23.0.1
  API version:      1.42 (minimum version 1.12)
  Go version:       go1.19.5
  Git commit:       bc3805a
  Built:            Thu Feb  9 19:46:56 2023
  OS/Arch:          linux/amd64
  Experimental:     false
 containerd:
  Version:          1.6.18
  GitCommit:        2456e983eb9e37e47538f59ea18f2043c9a73640
 runc:
  Version:          1.1.4
  GitCommit:        v1.1.4-0-g5fd4c4d
 docker-init:
  Version:          0.19.0
  GitCommit:        de40ad0



To deploy the architecture, use local-deployment.sh file.
It contains config as config file inside the script. Default conf is settled as an exemple config for automatic deployment. 
Don't forget to change content : 
- Certificate information (SSL conf at the beginning)
- .env file config with differents password and path.

(#TODO : Change config into config file)

#TODO : Swift is currently unavailable. 