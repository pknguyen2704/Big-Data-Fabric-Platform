# Big Data Fabric Platform – Setup Guide

Tài liệu này hướng dẫn chi tiết cách **cài đặt, cấu hình và triển khai** dự án **Big Data Fabric Platform** bằng **Docker & Docker Compose** trên môi trường Linux (Ubuntu).

---

## Prerequisites

Trước khi bắt đầu, đảm bảo hệ thống đáp ứng các yêu cầu sau:

* **Ubuntu**: 20.04+
* **Git**
* **Docker Engine** ≥ 20.x
* **Docker Compose** (v2 khuyến nghị)
* **RAM**: tối thiểu 16GB (khuyến nghị 32GB)
* **Disk**: ≥ 50GB trống

---

## Install Docker on Ubuntu

### 1. Update system

```bash
sudo apt update
```

### 2. Install required packages

```bash
sudo apt install -y \
  apt-transport-https \
  ca-certificates \
  curl \
  software-properties-common
```

### 3. Add Docker GPG key

```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
```

### 4. Add Docker repository

```bash
echo \
"deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### 5. Install Docker Engine

```bash
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io
```

### 6. Verify installation

```bash
docker --version
docker compose version
```

> ℹ️ **Tip**: Run Docker without `sudo`

```bash
sudo usermod -aG docker $USER
newgrp docker
```

---

## Create Docker Network

Tất cả service trong hệ thống sử dụng chung một Docker bridge network:

```bash
docker network create bdfp-net --driver bridge
```

---

## Fix Permission Issues (HDFS / Hadoop)

Một số container (HDFS, Hadoop) yêu cầu quyền ghi vào volume local:

```bash
sudo chmod -R 777 hadoop_namenode
sudo chmod -R 777 hadoop_datanode1
sudo chmod -R 777 hadoop_datanode2
```

---

## Exposed Ports

| Service          | Port     |
| ---------------- | -------- |
| MySQL            | 33061    |
| PostgreSQL       | 54321    |
| Apache NiFi      | 8443     |
| Apache Kafka     | Internal |
| HDFS NameNode UI | 9870     |
| Apache Airflow   | 8089     |
| Trino            | 8085     |
| OpenMetadata     | 8585     |
| Apache Superset  | 8088     |

---

## Project Structure

```text
Big-Data-Fabric-Platform/
├── analysis/
│   ├── jupyter
│   └── superset
├── documents/                  
├── experiments/
│   └── datasource
│       ├── streaming
│       ├── structured
│       └── unstructure
│       # NiFi XML / JSON templates
├── governance/
│   └── openmetadata             
├── ingestion/
│   └── nifi                     
├── query_engine/
│   └── trino                    
├── schedule/
│   └── airflow                  
├── storage/
│   ├── hdfs
│   └── hive_metastore
└── README.md
```

---

## Setup & Deployment

### Step 1: Clone repository

```bash
git clone https://github.com/pknguyen2704/Big-Data-Fabric-Platform.git
cd Big-Data-Fabric-Platform
```

---

### Step 2: tart services


Hoặc khởi động theo service:

```bash
cd storage/hdfs && docker compose up -d
cd storage/hive_metastore && docker compose up -d
cd ingestion/nifi && docker compose up -d
cd schedule/airflow && docker compose up -d --build
cd query_engine/trino && docker compose up -d
cd governance/openmetadata && docker compose up -d
cd analysis/superset && docker compose up -d
cd analysis/jupiter && docker compose up -d
```

---

## 🌍 Access Services

| Service         | URL                                                      | Username                                                  | Password     |
| --------------- | -------------------------------------------------------- | --------------------------------------------------------- | ------------ |
| Apache NiFi     | [http://localhost:8443/nifi](http://localhost:8443/nifi) | admin                                                     | Admin123456@ |
| Apache Airflow  | [http://localhost:8080](http://localhost:8080)           | airflow                                                   | airflow      |
| OpenMetadata    | [http://localhost:8585](http://localhost:8585)           | [admin@open-metadata.org](mailto:admin@open-metadata.org) | admin        |
| Apache Superset | [http://localhost:8088](http://localhost:8088)           | admin                                                     | admin        |
| Hadoop UI       | [http://localhost:9870](http://localhost:9870)           | —                                                         | —            |
| Trino UI        | [http://localhost:8085](http://localhost:8085)           | admin                                                     | —            |

---

## 🧪 Troubleshooting

### Check container status

```bash
docker ps -a
```

### View logs

```bash
docker compose logs -f <service_name>
```

### Restart service

```bash
docker compose restart <service_name>
```

---
