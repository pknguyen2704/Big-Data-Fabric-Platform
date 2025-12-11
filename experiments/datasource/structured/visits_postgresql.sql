

CREATE TABLE visits (
    visit_id       BIGINT PRIMARY KEY, -- Khớp với cột 1: visit_id
    patient_id     CHAR(12) NOT NULL,  -- Khớp với cột 2: patient_id (CCCD)
    visit_date     TIMESTAMP NOT NULL, -- Khớp với cột 3: visit_date
    doctor_name    VARCHAR(100),       -- Khớp với cột 4: doctor_name
    visit_type     VARCHAR(50),        -- Khớp với cột 5: visit_type
    visit_reason   VARCHAR(255),       -- Khớp với cột 6: visit_reason
    inpatient      VARCHAR(10),        -- Khớp với cột 7: inpatient (Mới)
    department     VARCHAR(100),       -- Khớp với cột 8: department
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Khớp với cột 9: created_at
    
    -- Cột này không có trong CSV, nhưng nên giữ để quản lý DB
    updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
);

-- 4. Thêm Comment (Documentation)
COMMENT ON TABLE visits IS 'Bảng lưu trữ lịch sử khám chữa bệnh chi tiết của bệnh nhân (Dữ liệu giả lập)';

-- Thêm mô tả chi tiết cho từng Cột
COMMENT ON COLUMN visits.visit_id IS 'Mã định danh duy nhất cho mỗi lượt khám';
COMMENT ON COLUMN visits.patient_id IS 'Mã Căn cước công dân (CCCD) của bệnh nhân';
COMMENT ON COLUMN visits.visit_date IS 'Thời gian thực tế diễn ra lượt khám';
COMMENT ON COLUMN visits.doctor_name IS 'Họ và tên bác sĩ phụ trách lượt khám';
COMMENT ON COLUMN visits.visit_type IS 'Phân loại hình thức khám.';
COMMENT ON COLUMN visits.visit_reason IS 'Triệu chứng lâm sàng hoặc lý do chính khiến bệnh nhân đi khám';
COMMENT ON COLUMN visits.inpatient IS 'Chỉ định nhập viện nội trú sau khi khám.';
COMMENT ON COLUMN visits.department IS 'Tên Khoa/Phòng tiếp nhận khám';
COMMENT ON COLUMN visits.created_at IS 'Thời điểm bản ghi lượt khám được ghi nhận vào hệ thống';
COMMENT ON COLUMN visits.updated_at IS 'Thời điểm thông tin lượt khám được cập nhật lần cuối cùng';

-- 5. Tạo Trigger tự động cập nhật updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = CURRENT_TIMESTAMP;
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_visits
BEFORE UPDATE ON visits
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();