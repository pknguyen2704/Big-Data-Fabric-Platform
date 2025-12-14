# Big-Data-Fabric-Platform

**Team:** 08 - HotTopic25  
**Project:** UILDING A BIG DATA PLATFORM FOR DISTRIBUTED DATA INTEGRATION USING DATA FABRIC 

---

## 1. Prerequisites (Yêu cầu tiền quyết)

Hệ thống được xây dựng dựa trên kiến trúc **Microservices** và chạy hoàn toàn trên **Docker**.  
Do đặc thù của các nền tảng Big Data (Hadoop, Trino, OpenMetadata), hệ thống yêu cầu tài nguyên phần cứng tương đối lớn.

### 1.1 Hardware Requirements (Cấu hình phần cứng)

Để đảm bảo toàn bộ stack hoạt động ổn định, máy tính triển khai cần đáp ứng:

- **RAM:**  
  - Tối thiểu **16GB**  
  - Khuyến nghị **24GB RAM** (theo môi trường thực nghiệm của nhóm)
- **CPU:** Tối thiểu **4 vCPUs**
- **Disk Space:** Trống ít nhất **50GB**

### Software Requirements

- **Docker Engine:** `>= 20.10.0`
- **Docker Compose:** `>= 1.29.0`
- **Git**

---

## 2. Installation & Deployment (Cài đặt & Triển khai)

Thực hiện theo các bước sau để khởi động toàn bộ nền tảng.

### Bước 1: Clone mã nguồn

```bash
git clone https://github.com/pknguyen2704/Big-Data-Fabric-Platform.git
cd Big-Data-Fabric-Platform
```

### Bước 2: Cấu hình môi trường

Trước khi chạy, cần thiết lập các biến môi trường và thông tin đăng nhập.

Sao chép file mẫu:

```bash
cp .env.example .env
```

### Bước 3: Khởi động hệ thống

Để tránh quá tải tài nguyên khi khởi động đồng thời, **khuyến khích khởi động theo thứ tự**.

#### Option A: Khởi động toàn bộ (Cho máy mạnh)

```bash
docker-compose up -d
```

⏳ Thời gian chờ khởi động hoàn tất: **10–15 phút**

#### Option B: Khởi động từng phần (Khuyến nghị)

```bash
# 1. Storage & Metadata Layer
docker-compose up -d database namenode datanode hive-metastore

# 2. Processing & Ingestion Layer
docker-compose up -d nifi trino-coordinator

# 3. Governance & Orchestration Layer
docker-compose up -d openmetadata-server airflow-webserver
```

---

## 3. Access Information (Thông tin truy cập)

Sau khi hệ thống khởi động thành công, các dịch vụ có thể truy cập qua trình duyệt:

| Service         | Role          | URL                                                      | Default User | Default Password      |
| --------------- | ------------- | -------------------------------------------------------- | ------------ | --------------------- |
| Apache NiFi     | Ingestion     | [http://localhost:8443/nifi](http://localhost:8443/nifi) | admin        | *(trong file `.env`)* |
| Apache Airflow  | Orchestration | [http://localhost:8080](http://localhost:8080)           | airflow      | airflow               |
| OpenMetadata    | Governance    | [http://localhost:8585](http://localhost:8585)           | admin        | admin                 |
| Apache Superset | Visualization | [http://localhost:8088](http://localhost:8088)           | admin        | admin                 |
| MinIO Console   | S3 Storage UI | [http://localhost:9001](http://localhost:9001)           | minioadmin   | minioadmin            |
| Trino UI        | Query Monitor | [http://localhost:8090](http://localhost:8090)           | admin        | *(No password)*       |

> **Lưu ý:**
> Nếu chưa truy cập được, vui lòng:
>
> * Đợi thêm vài phút để các service Java khởi động hoàn tất, hoặc
> * Kiểm tra log:
>
> ```bash
> docker-compose logs -f [service_name]
> ```

---

## 4. Reproducibility Guide (Hướng dẫn tái lập kết quả)

Để tái hiện các kết quả thực nghiệm trong **Báo cáo – Mục 4 (Experiments 2)**, thực hiện theo các kịch bản sau.

---

### Kịch bản 1: Ingestion & Data Generation (Sinh dữ liệu giả lập)

Dữ liệu đầu vào là **Synthetic Data** mô phỏng bệnh nhân.

1. Truy cập **Apache NiFi**:
   [https://localhost:8443/nifi](https://localhost:8443/nifi)
2. Tìm **Process Group** có tên **`Data Generator`**
3. Chuột phải → chọn **Start**
4. Kiểm tra dữ liệu đã được đẩy vào Kafka qua topic:

   ```
   kafka.public.smart_band
   ```

---

### Kịch bản 2: Transformation Pipeline (Làm sạch & Chuẩn hóa)

Chạy pipeline ETL để chuyển dữ liệu từ **Bronze → Silver → Gold**.

1. Truy cập **Apache Airflow**:
   [http://localhost:8080](http://localhost:8080)
2. Kích hoạt DAG:

   ```
   dbt_transformation_pipeline
   ```
3. DAG sẽ:

   * Làm sạch dữ liệu từ Kafka / MongoDB
   * Lưu trữ dữ liệu dưới dạng **Apache Iceberg** trên HDFS / MinIO
   * Tạo các bảng phân tích tại lớp **Gold**

---

### Kịch bản 3: Data Governance & Lineage (Quản trị dữ liệu)

Kiểm tra **Active Metadata** và **Data Lineage**.

1. Truy cập **OpenMetadata**:
   [http://localhost:8585](http://localhost:8585)
2. Vào mục **Pipelines**, chọn pipeline vừa chạy
3. Chọn tab **Lineage** để xem luồng dữ liệu:

   ```
   Kafka / MongoDB → Silver Iceberg → Gold Tables
   ```
4. Vào mục **Data Quality** để xem các test cases tự động:

   * Kiểm tra null
   * Schema drift
   * Data freshness

---

### Kịch bản 4: Visualization (Trực quan hóa)

1. Truy cập **Apache Superset**:
   [http://localhost:8088](http://localhost:8088)
2. Vào **Dashboards**
3. Chọn dashboard:

   ```
   Health Monitoring Dashboard
   ```

Dashboard hiển thị các biểu đồ phân tích dựa trên dữ liệu đã được xử lý.

---

## 5. Project Structure (Cấu trúc dự án)

```bash
Big-Data-Fabric-Platform/
├── airflow/                # Mã nguồn & cấu hình Apache Airflow (DAGs)
├── dbt_project/            # Các model biến đổi dữ liệu (dbt models)
├── nifi_templates/         # File template XML/JSON cho luồng NiFi
├── docker/                 # Các file Dockerfile tùy chỉnh
├── data_generator/         # Script Python sinh dữ liệu giả lập [QUAN TRỌNG]
├── documentation/          # Tài liệu thiết kế & Báo cáo PDF
├── docker-compose.yaml     # File triển khai chính
└── README.md               # Tài liệu này
```

---

## 6. Troubleshooting (Xử lý lỗi thường gặp)

### ❌ Lỗi: `No space left on device` hoặc container tự tắt

**Nguyên nhân:**

* Thiếu RAM hoặc ổ cứng

**Khắc phục:**

* Tăng tài nguyên cho Docker: `Preferences → Resources`
* Dọn dẹp Docker:

```bash
docker system prune
```

---

### ❌ Lỗi kết nối giữa Superset và Trino

**Khắc phục:**

* Đảm bảo container **Trino** ở trạng thái `healthy` trước khi truy vấn từ Superset

---

## Contact

**Team 08**
📧 Email: *[Email liên hệ của trưởng nhóm]*

---

```

Nếu bạn muốn, mình có thể:
- Chuẩn hóa README theo **chuẩn học thuật / hội đồng chấm đồ án**
- Viết thêm phần **Architecture Diagram**, **Tech Stack**, hoặc **Abstract**
- Việt hóa / Anh hóa song ngữ cho README
```
