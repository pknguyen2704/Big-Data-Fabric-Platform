DROP DATABASE IF EXISTS HOSPITAL_DB;
-- 1. Tạo Database và Schema (Nếu chưa có)
CREATE DATABASE IF NOT EXISTS PATIENTS;
CREATE SCHEMA IF NOT EXISTS PATIENTS.PUBLIC;

USE SCHEMA PATIENTS.PUBLIC;

-- 2. Tạo bảng info
CREATE OR REPLACE TABLE info (
    -- Snowflake không bắt buộc độ dài cho VARCHAR, nhưng ta giữ để rõ ràng về mặt nghiệp vụ
    patient_id VARCHAR(12) NOT NULL COMMENT 'Mã căn cước công dân (CCCD) 12 số',
    
    fullname VARCHAR(255) NOT NULL COMMENT 'Họ và tên đầy đủ',
    
    age NUMBER NOT NULL COMMENT 'Tuổi tại thời điểm ghi nhận', -- Snowflake dùng NUMBER thay cho INT UNSIGNED
    
    -- Snowflake không có kiểu ENUM, ta dùng VARCHAR và (tùy chọn) thêm Constraint check
    gender VARCHAR(10) NOT NULL DEFAULT 'Khác' COMMENT 'Giới tính (Nam, Nữ, Khác)', 
    
    dob DATE NOT NULL COMMENT 'Ngày sinh',
    
    ethnicity VARCHAR(50) DEFAULT 'Kinh' COMMENT 'Dân tộc',
    
    ward VARCHAR(100) NOT NULL COMMENT 'Phường/Xã',
    
    district VARCHAR(100) NOT NULL COMMENT 'Quận/Huyện',
    
    city VARCHAR(100) DEFAULT 'Hà Nội' COMMENT 'Tỉnh/Thành phố',
    
    address VARCHAR(255) NOT NULL COMMENT 'Địa chỉ chi tiết (Số nhà, đường, thôn...)',
    
    phone_number VARCHAR(15) NOT NULL COMMENT 'Số điện thoại liên hệ',
    
    health_insurance_id VARCHAR(15) NOT NULL COMMENT 'Mã số Bảo hiểm y tế',
    
    job VARCHAR(100) COMMENT 'Nghề nghiệp',
    
    -- TIMESTAMP_NTZ: Timestamp No Time Zone (Tương đương DATETIME của MySQL)
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP() COMMENT 'Thời điểm tạo bản ghi (Ngày khám)',
    
    -- Snowflake không hỗ trợ "ON UPDATE CURRENT_TIMESTAMP" tự động trong DDL
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP() COMMENT 'Thời điểm cập nhật bản ghi cuối cùng',

    -- Định nghĩa Khóa chính (Lưu ý: Snowflake KHÔNG thực thi ràng buộc này, chỉ để làm metadata)
    CONSTRAINT pk_patient_id PRIMARY KEY (patient_id),
    
    -- Định nghĩa Unique (Lưu ý: Snowflake cũng KHÔNG thực thi ràng buộc này)
    CONSTRAINT uq_health_insurance_id UNIQUE (health_insurance_id)
)
COMMENT = 'Thông tin nhân khẩu học bệnh nhân';