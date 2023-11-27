#!/bin/bash
kill $(ps aux | grep 'fastapi' | awk '{print $2}')
cd /data/single-cell/cellxgene-fastapi;git pull;nohup /root/anaconda3/envs/cellxgene_fastapi/bin/python main.py &