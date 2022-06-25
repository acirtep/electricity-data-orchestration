#!/bin/bash -l
sudo chown ssh_user_localhost /Users/petra1/Library/Containers/com.docker.docker/Data/docker.sock
sudo docker stop $1 || true && sudo docker rm $1 || true
