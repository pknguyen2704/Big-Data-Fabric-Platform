#!/bin/bash
# rm -rf /opt/hadoop/data/dataNode/*
sudo chown -R hadoop:hadoop /opt/hadoop/data/dataNode
sudo chmod 755 /opt/hadoop/data/dataNode
hdfs datanode