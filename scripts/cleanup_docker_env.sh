#!/bin/bash -l
today=`date +%Y-%m-%d.%H:%M:%S`
sudo docker logs firefox_container >> /logs/firefox_container/"$today.log"
sudo docker stop firefox_container || true && sudo docker rm firefox_container || true
sudo chown petra1 /Users/petra1/Library/Containers/com.docker.docker/Data/docker.sock
