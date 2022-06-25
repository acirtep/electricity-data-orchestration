#!/bin/bash -l
sudo docker run -d \
    --name firefox_container \
    --network web \
    --mount source=/tmp/export_folder,target=/tmp/export_folder,type=bind \
    --shm-size=2g --privileged=true \
    --net-alias firefox \
    selenium/standalone-firefox:98.0
