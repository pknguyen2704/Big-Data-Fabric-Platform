# Thực nghiệm

## Môi trường triển khai (Implementation Environment)

Để đánh giá tính khả thi và hiệu năng của **nền tảng Big Data Fabric** được đề xuất, nghiên cứu đã xây dựng một môi trường thực nghiệm thống nhất trên hạ tầng điện toán đám mây. Hệ thống được triển khai trên một **máy ảo (Virtual Machine – VM)** thuộc **Google Cloud Platform (GCP)**, đóng vai trò là node xử lý trung tâm, nơi vận hành toàn bộ các thành phần của hệ sinh thái dữ liệu.

### Triển khai phần mềm

Chiến lược **container hóa (containerization)** được áp dụng nhằm đảm bảo tính nhất quán môi trường và khả năng tái lập (reproducibility). Toàn bộ các thành phần mã nguồn mở (Apache NiFi, Trino, Iceberg, OpenMetadata, v.v.) đều được đóng gói và vận hành dưới dạng **Docker containers**. Việc điều phối container được thực hiện bằng **Docker Compose**, cho phép quản lý tập trung mạng nội bộ và biến môi trường.

Toàn bộ mã nguồn và cấu hình triển khai được quản lý phiên bản và công khai tại:

> [https://github.com/pknguyen2704/Big-Data-Fabric-Platform.git](https://github.com/pknguyen2704/Big-Data-Fabric-Platform.git)

---

## Bài toán và nguồn dữ liệu

### Thực trạng

Các bệnh viện tại Việt Nam hiện đang vận hành nhiều hệ thống thông tin độc lập như HIS, PACS, LIS, EMR/EHR và các hệ thống chuyên biệt khác. Những hệ thống này thường được phát triển bởi các nhà cung cấp khác nhau, ở các thời điểm khác nhau, và được tối ưu cho từng nghiệp vụ riêng lẻ.

Cách tiếp cận phân mảnh này dẫn đến:

* **Dữ liệu bị phân tán**, không đồng nhất về mô hình và định dạng
* Khó xây dựng **cái nhìn tổng thể lấy bệnh nhân làm trung tâm**
* Hạn chế trong việc kết hợp dữ liệu lịch sử và dữ liệu gần thời gian thực
* Quản trị, phân quyền và bảo mật thiếu tính tập trung
* Chất lượng dữ liệu không đồng đều, khó theo dõi thay đổi schema

Những hạn chế trên đặt ra nhu cầu xây dựng một nền tảng dữ liệu thống nhất, có khả năng:

* Tổ chức dữ liệu theo vòng đời bệnh nhân
* Xử lý cả dữ liệu theo lô (batch) và gần thời gian thực
* Đảm bảo quản trị và bảo mật tập trung
* Mở rộng cho các bài toán phân tích dài hạn

Kiến trúc **Data Fabric** đáp ứng tốt các yêu cầu này thông qua việc cung cấp một lớp logic thống nhất, tích hợp dữ liệu phân tán dựa trên metadata, data virtualization và governance.

---

### Nguồn dữ liệu

Do dữ liệu y tế là dữ liệu nhạy cảm và chịu ràng buộc pháp lý nghiêm ngặt, nghiên cứu sử dụng **dữ liệu giả lập (synthetic data)** để mô phỏng các hệ thống dữ liệu phổ biến trong bệnh viện. Dữ liệu được xây dựng từ năm nguồn chính.

---

### 1. Dữ liệu nhân khẩu học bệnh nhân

* **Mô tả:** Lưu trữ thông tin định danh và nhân khẩu học bệnh nhân
* **Quy mô:** 100.000 bản ghi
* **Mục đích:** Là nền tảng cho các phân tích lấy bệnh nhân làm trung tâm
* **Đặc điểm:**

  * Dữ liệu có cấu trúc
  * Mỗi bệnh nhân tương ứng một bản ghi
  * Tần suất cập nhật thấp

**Thuộc tính chính:**

* Định danh: `patient_id`, `fullname`, `health_insurance_id`
* Nhân khẩu học: `age`, `gender`, `ethnicity`, `job`
* Liên hệ: `phone_number`, `address`, `ward`, `district`, `city`
* Metadata: `created_at`, `updated_at`

**Ràng buộc toàn vẹn:**

* `patient_id` là duy nhất
* Tất cả các trường bắt buộc có giá trị
* Địa chỉ được tổ chức theo cấu trúc phân cấp
* Theo dõi lịch sử thay đổi bằng timestamp

---

### 2. Dữ liệu lượt khám bệnh

* **Mô tả:** Ghi nhận các lượt khám của bệnh nhân giai đoạn 2023–2025
* **Quy mô:** 3.000.000 bản ghi
* **Mục đích:** Phân tích theo thời gian và hoạt động vận hành bệnh viện
* **Đặc điểm:**

  * Dữ liệu có cấu trúc, dạng chuỗi thời gian
  * Tần suất cập nhật cao
  * Quan hệ một-nhiều với bệnh nhân

---

### 3. Hồ sơ sức khỏe bệnh nhân

* **Mô tả:** Lưu trữ kết quả khám và xét nghiệm y tế
* **Quy mô:** 11.548.244 bản ghi
* **Mục đích:** Phân tích sức khỏe bệnh nhân theo thời gian
* **Đặc điểm:**

  * Dữ liệu có cấu trúc
  * Liên kết với bệnh nhân và lượt khám

---

### 4. Dữ liệu hành vi người dùng (MongoDB)

* **Mô tả:** Nhật ký sinh hoạt và hành vi hằng ngày của bệnh nhân
* **Định dạng:** JSON bán cấu trúc
* **Tần suất:** Hàng ngày
* **Mục đích:** Phân tích mối liên hệ giữa lối sống và sức khỏe

---

### 5. Dữ liệu cảm biến IoT (Kafka)

* **Mô tả:** Dữ liệu sinh lý gần thời gian thực từ thiết bị đeo
* **Loại dữ liệu:** Streaming / sự kiện
* **Mục đích:** Theo dõi sức khỏe liên tục

---

## Xử lý dữ liệu

Quy trình xử lý dữ liệu được triển khai trên một **lớp truy vấn phân tán thống nhất**, cho phép truy cập đồng thời nhiều nguồn dữ liệu dị thể mà không cần tập trung hóa dữ liệu ngay từ đầu.

### Công nghệ chính

* **Apache Trino:** Công cụ truy vấn SQL phân tán
* **dbt:** Quản lý và hiện thực hóa logic biến đổi dữ liệu
* **Apache Iceberg:** Định dạng bảng giao dịch cho Data Lakehouse

Mô hình xử lý tuân theo nguyên lý **ELT**, trong đó Trino đảm nhiệm thực thi truy vấn và dbt quản lý tầng biến đổi.

---

### Tổng quan luồng xử lý

Các nguồn dữ liệu bao gồm cơ sở dữ liệu quan hệ, data warehouse, nền tảng streaming và document store. Quy trình xử lý được chia thành hai hướng:

1. **Nguồn dữ liệu có cấu trúc và chất lượng cao**: truy vấn trực tiếp
2. **Nguồn dữ liệu bán cấu trúc hoặc không chắc chắn**: làm sạch và chuẩn hóa bằng dbt

---

### Xử lý dữ liệu có cấu trúc

Dữ liệu từ MySQL, PostgreSQL và Snowflake được truy vấn trực tiếp thông qua Trino và được sử dụng như các bảng tham chiếu trong mô hình dbt, không thực hiện nhân bản hay biến đổi dữ liệu tại nguồn.

---

### Xử lý dữ liệu sự kiện từ Kafka

* Apache NiFi thu thập dữ liệu theo yêu cầu
* Dữ liệu được lưu trữ trong Kafka và xử lý theo mô hình batch
* dbt thực hiện làm sạch, chuẩn hóa và chuyển đổi kiểu dữ liệu thời gian
* Loại bỏ các bản ghi không đầy đủ

Kết quả được materialize tại bảng:

```
iceberg.silver.smart_band
```

---

### Xử lý dữ liệu phi cấu trúc từ MongoDB

* Trích xuất các trường cần thiết từ document
* Chuẩn hóa schema
* Xử lý giá trị thiếu

Kết quả được materialize tại:

```
iceberg.silver.daily_behavior_logs
```

---

### Tầng dữ liệu phân tích (Gold)

Các bảng Silver được kết hợp với dữ liệu có cấu trúc để tạo ra các bảng phân tích nghiệp vụ, được materialize tại:

```
iceberg.gold.*
```

---

## Quan sát dữ liệu & Quản trị metadata

**OpenMetadata** đóng vai trò là lớp quản trị và quan sát trung tâm.

### Thu thập metadata

* Kết nối tới CSDL, data warehouse và Kafka
* Pipeline thu thập tự động
* Điều phối bởi Apache Airflow

### Chức năng chính

* Phát hiện schema và schema drift
* Mô tả chi tiết bảng và cột
* Xem dữ liệu mẫu an toàn
* Tự động phân loại dữ liệu nhạy cảm (PII)

---

### Quản trị chất lượng dữ liệu

#### Data Profiling

* Thống kê cấp bảng
* Thống kê và phân phối dữ liệu cấp cột

#### Kiểm thử chất lượng dữ liệu

* Ràng buộc cấp bảng
* Ràng buộc cấp cột
* Thực thi định kỳ và cảnh báo

---

## Model Context Protocol (MCP)

Trong kiến trúc này, **OpenMetadata hoạt động như một MCP Server**, cho phép các AI Agent tương tác ngữ nghĩa với hệ sinh thái metadata.

AI Agent có thể:

* Khám phá tập dữ liệu hiện có
* Hiểu lineage, ownership và chất lượng
* Định vị dữ liệu phân tích (ví dụ: BMI)
* Không cần truy cập trực tiếp dữ liệu thô

Hai kịch bản prompt được sử dụng để đánh giá:

1. *Liệt kê toàn bộ bảng và nguồn dữ liệu, phân loại theo loại dịch vụ*
2. *Dữ liệu BMI của bệnh nhân nằm ở đâu?*

---

## Trực quan hóa dữ liệu

Lớp trực quan hóa bao gồm:

* **Apache Superset:** Dashboard BI
* **Jupyter Notebook:** Phân tích nâng cao
* **Claude MCP:** Trợ lý phân tích dựa trên metadata

Tất cả công cụ đều truy cập dữ liệu thông qua **Trino** và metadata thông qua **OpenMetadata**, đảm bảo quản trị và nhất quán.

---

## Data Lineage (Truy vết dòng chảy dữ liệu)

OpenMetadata tự động xây dựng **Data Lineage đầu-cuối** bằng cách phân tích truy vấn SQL, mô hình dbt và nhật ký pipeline.

### Lợi ích

* Phân tích tác động khi thay đổi schema
* Truy vết nguyên nhân lỗi dữ liệu
* Minh bạch hóa và tăng độ tin cậy dữ liệu

Tài liệu này hoàn thiện phần thực nghiệm cho nền tảng **Big Data Fabric Platform** được đề xuất.
