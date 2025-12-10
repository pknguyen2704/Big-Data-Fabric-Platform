# Setup

## Prerequisites

- Docker
- Git

#install docker on vm

sudo apt update

sudo apt install apt-transport-https ca-certificates curl software-properties-common

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update

sudo apt install docker-ce

#create network in docker

sudo docker network create dfp-net --driver bridge


# Fix cac bug ve quyen/ user
sudo chmod -R 777 hadoop_namenode
sudo chmod -R 777 hadoop_datanode1
sudo chmod -R 777 hadoop_datanode2

# Các port để làm việc
ds-mysql: 33061
ds-postgres: 54321
nifi: 8443
kafka:
hdfs: 9870
airflow: 8089
trino: 8085
openmetadata: 8585
superset: 8088


## Setup

1. Clone the repository
2. Create docker network
```bash
docker network create -d bridge bdfp-net
```
3. Go to each directory and run docker-compose up -d
```bash
docker-compose up -d
```

![alt text](assets/big-data-fabric-platform-architecture.png)