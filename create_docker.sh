#!/bin/bash
dockerPid=`sudo docker ps -a |grep 'cellxgene-fastapi' |awk '{print $1}'`;
echo "docker pid " $dockerPid;
sudo docker stop $dockerPid;
sudo docker rm $dockerPid;
dockerImage=`sudo docker images|grep 'cellxgene-fastapi'|awk '{print $3}'`;
echo "docker image" $dockerImage;
sudo docker rmi $dockerImage;
sudo docker build -t cellxgene-fastapi:v1.0 .
sudo docker run -dti -p 5050:5050 --restart=always --name cellxgene-fastapi cellxgene-fastapi:v1.0
