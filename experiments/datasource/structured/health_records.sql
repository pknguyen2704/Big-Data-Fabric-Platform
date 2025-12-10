CREATE DATABASE IF NOT EXISTS patients CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE patients;

DROP TABLE IF EXISTS health_records;

CREATE TABLE health_records (
    test_id BIGINT NOT NULL PRIMARY KEY COMMENT 'Mã định danh xét nghiệm',
    visit_id BIGINT NOT NULL COMMENT 'Mã lượt khám, liên kết với bảng visits',
    patient_id CHAR(12) NOT NULL COMMENT 'Mã CCCD bệnh nhân, liên kết với bảng info',
    test_code VARCHAR(50) NOT NULL COMMENT 'Mã code xét nghiệm',
    test_name VARCHAR(255) NOT NULL COMMENT 'Tên xét nghiệm đầy đủ',
    test_result VARCHAR(500) COMMENT 'Kết quả (Lưu dạng chuỗi vì có cả số và mô tả hình ảnh)',
    test_unit VARCHAR(50) COMMENT 'Đơn vị đo (VD: mmol/L, %)',
    reference_range VARCHAR(100) COMMENT 'Khoảng tham chiếu bình thường',
    abnormal_flag ENUM('Normal', 'High', 'Low', 'Abnormal') DEFAULT 'Normal' COMMENT 'Cờ cảnh báo bất thường',
    test_date DATETIME NOT NULL COMMENT 'Thời điểm thực hiện xét nghiệm',
    height DECIMAL(5, 2) COMMENT 'Chiều cao (cm)',
    weight DECIMAL(5, 2) COMMENT 'Cân nặng (kg)',
    bmi DECIMAL(4, 2) COMMENT 'Chỉ số BMI',
    blood_type VARCHAR(5) COMMENT 'Nhóm máu',
    comorbidities_snapshot TEXT COMMENT 'Danh sách bệnh nền tại thời điểm khám',

    -- Tạo Index để truy vấn nhanh hơn
    INDEX idx_patient_visit (patient_id, visit_id),
    INDEX idx_test_code (test_code),
    INDEX idx_abnormal (abnormal_flag),
    
) 
ENGINE=InnoDB 
DEFAULT CHARSET=utf8mb4 
COLLATE=utf8mb4_unicode_ci
COMMENT='Bảng lưu trữ kết quả Cận lâm sàng (Xét nghiệm & Chẩn đoán hình ảnh)';