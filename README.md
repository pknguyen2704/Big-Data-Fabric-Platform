# Big-Data-Fabric-Platform

**Team:** 08 - HotTopic25  
**Project:** UILDING A BIG DATA PLATFORM FOR DISTRIBUTED DATA INTEGRATION USING DATA FABRIC 

---
---
## 🎯 Mục tiêu hệ thống (Project Objectives)

Dự án **Big-Data-Fabric-Platform** nhằm xây dựng một nền tảng Big Data hoàn chỉnh dựa trên kiến trúc **Data Fabric**, tập trung giải quyết các bài toán:

* Tích hợp dữ liệu **phân tán – dị thể – đa định dạng** (structured, semi-structured, streaming)
* Truy cập dữ liệu **logic thống nhất** mà không cần di chuyển vật lý (zero / minimal copy)
* Quản trị dữ liệu xuyên suốt vòng đời thông qua **Active Metadata & Lineage**
* Tự động hóa pipeline dữ liệu theo hướng **DataOps**
* Hỗ trợ phân tích, BI và mở rộng cho AI/ML

---

## 🧠 Tổng quan kiến trúc Data Fabric trong dự án

![alt text](assets/big-data-fabric-platform-architecture.png)
Hệ thống được xây dựng theo mô hình **Storage – Compute – Governance tách rời**, trong đó:

* **Storage Layer**
  → HDFS + Iceberg (Data Lakehouse)

* **Ingestion Layer**
  → Apache NiFi (Batch + Streaming)

* **Transformation Layer**
  → dbt + Trino (ELT, Medallion Architecture)

* **Query & Virtualization Layer**
  → Trino (Federated SQL Engine)

* **Orchestration Layer**
  → Apache Airflow (Workflow as Code)

* **Governance & Metadata Layer**
  → OpenMetadata (Active Metadata, Lineage, Data Quality)

* **Analytics Layer**
  → Apache Superset (Self-service BI)

Kiến trúc này cho phép:

* Dữ liệu **ở yên tại nguồn**
* Logic xử lý và truy vấn được **ảo hóa**
* Metadata trở thành **trung tâm điều phối thông minh**

---

## 🔄 Luồng xử lý dữ liệu tổng quát (End-to-End Flow)

```text
[Data Sources]
   ├── Structured (MySQL, PostgreSQL, CSV)
   ├── Streaming (Kafka)
   └── Semi/Unstructured (MongoDB)
        ↓
[Apache NiFi]
        ↓
[HDFS + Iceberg (Bronze / Silver)]
        ↓
[dbt + Trino]
        ↓
[Iceberg Gold Layer]
        ↓
[Superset / BI / Analytics]
        ↓
[OpenMetadata: Lineage + Quality + Governance]
```

---

## 📁 Giải thích chi tiết cấu trúc thư mục

### `analysis/`

Chứa các công cụ phục vụ **khai thác & phân tích dữ liệu**:

* `jupiter/` – Notebook phân tích thử nghiệm
* `superset/` – Cấu hình, metadata và truy vấn BI

---

### `documents/`

* `assets/` – Hình ảnh kiến trúc, sơ đồ hệ thống
* `setup.md` – **Tài liệu quan trọng** hướng dẫn khởi động hệ thống theo thứ tự
* `open-metadata.md` – Hướng dẫn cấu hình OpenMetadata

---

### `experiments/datasource/`

Chứa **dữ liệu giả lập (synthetic data)** mô phỏng hệ thống bệnh viện:

* `structured/` – CSV, relational data
* `streaming/` – dữ liệu mô phỏng streaming
* `unstructured/` – dữ liệu bán cấu trúc
* `patients_seed_last_5000.csv` – dữ liệu mẫu bệnh nhân

👉 Phục vụ cho việc **test pipeline ingestion & transformation**

---

### `ingestion/nifi/`

* Dockerfile & template cho Apache NiFi
* Các flow ingest dữ liệu:

  * Batch
  * Streaming
  * File-based

👉 Đây là **cửa ngõ dữ liệu đầu vào của toàn hệ thống**

---

### `storage/`

* `hdfs/` – HDFS cluster (Data Lake)
* `hive_metastore/` – Metadata store cho Iceberg & Trino

👉 Đóng vai trò **nền tảng lưu trữ vật lý**

---

### `query_engine/trino/`

* Cấu hình Trino
* Hadoop config
* Connector cho Iceberg, Hive, Kafka

👉 Thực hiện:

* Federated Query
* Data Virtualization
* SQL thống nhất cho toàn bộ hệ sinh thái

---

### `schedule/`

* Cấu hình Apache Airflow
* DAG điều phối:

  * Ingestion
  * Transformation
  * Data Quality Check
  * Metadata ingestion

---

### `governance/openmetadata/`

* Docker Compose cho OpenMetadata
* Metadata Agents
* Lineage, Quality, Classification


---

## Hướng dẫn sử dụng cơ bản (Quick Start)

### 1. Khởi động hệ thống theo thứ tự

**Bắt buộc đọc:** `documents/setup.md`

Thứ tự khuyến nghị:

1. Storage (HDFS + Hive Metastore)
2. Trino
3. NiFi
4. Airflow
5. OpenMetadata
6. Superset

---

### 2. Xử lý & biến đổi dữ liệu

* dbt model chạy thông qua Airflow
* Dữ liệu được chuẩn hóa theo:

  * Bronze
  * Silver
  * Gold

---

### 3. Khám phá metadata & lineage

* Truy cập OpenMetadata
* Theo dõi:

  * Data Lineage
  * Data Quality
  * Ownership
  * PII Classification

---

### 5️⃣ Phân tích & BI

* Superset kết nối trực tiếp Trino
* Dashboard sử dụng bảng `iceberg.gold.*`

---

## 👥 Team & Contact

**Team 08 – HotTopic25**
📧 Email: **[pknguyen2704@gmail.com](mailto:pknguyen2704@gmail.com)**
🎓 University of Engineering and Technology – VNU
