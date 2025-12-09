CREATE DATABASE IF NOT EXISTS patients;
USE patients;

CREATE TABLE info (
    patient_id VARCHAR(20) PRIMARY KEY COMMENT 'Mã căn cước công dân của bệnh nhân (12 số)',
    fullname VARCHAR(255) NOT NULL COMMENT 'Họ tên đầy đủ của bệnh nhân',
    age INT NOT NULL COMMENT 'Tuổi của bệnh nhân tại thời điểm cập nhật gần nhất',
    gender ENUM('Nam', 'Nữ', 'Khác') NOT NULL COMMENT 'Giới tính của bệnh nhân',
    dob DATE NOT NULL COMMENT 'Ngày tháng năm sinh (YYYY-MM-DD)',
    ethnicity VARCHAR(100) NOT NULL COMMENT 'Dân tộc của bệnh nhân',
    ward VARCHAR(255) NOT NULL COMMENT 'Phường/xã bệnh nhân đang sinh sống',
    district             VARCHAR(255) NOT NULL
                         COMMENT 'Quận/huyện bệnh nhân đang sinh sống',

    city                 VARCHAR(255) NOT NULL DEFAULT 'Hà Nội'
                         COMMENT 'Thành phố bệnh nhân sinh sống',

    address              VARCHAR(500) NOT NULL
                         COMMENT 'Địa chỉ cụ thể: số nhà, ngõ, ngách, đường, thôn,...',

    phone_number         VARCHAR(20) NOT NULL
                         COMMENT 'Số điện thoại bệnh nhân',

    health_insurance_id  VARCHAR(20) NOT NULL UNIQUE
                         COMMENT 'Mã thẻ bảo hiểm y tế',

    job                  VARCHAR(255) NOT NULL
                         COMMENT 'Nghề nghiệp của bệnh nhân',

    created_at           DATETIME NOT NULL
                         COMMENT 'Thời điểm tạo hồ sơ',

    updated_at           DATETIME NOT NULL
                         COMMENT 'Thời điểm cập nhật hồ sơ'
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COMMENT='Bảng info chứa dữ liệu nhân khẩu học của bệnh nhân';
