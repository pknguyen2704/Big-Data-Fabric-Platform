import csv
import random
from datetime import datetime, timedelta
from faker import Faker

# ================== CẤU HÌNH ==================

INPUT_PATIENTS_CSV = "info.csv"
OUTPUT_VISITS_CSV = "visits.csv"

# Số lượt khám cần sinh
NUM_VISITS = 3000000 
VISIT_END_CAP = datetime(2025, 12, 31, 23, 59, 59)

random.seed(42)
fake = Faker("vi_VN")

# ================== 1. DANH MỤC LÂM SÀNG (GIỮ NGUYÊN) ==================
# ... (Phần danh mục này giữ nguyên như code cũ của bạn vì đã tốt rồi) ...
# Để code gọn, tôi thu gọn phần này, bạn dán lại phần DICT cũ vào đây nhé.
# Tôi sẽ định nghĩa lại biến quan trọng nhất để code chạy được.

REASON_TO_DEPARTMENTS = {
    # Nhóm Nội - Tim mạch - Hô hấp
    "Kiểm tra sức khỏe định kỳ": ["Khoa Khám bệnh", "Khoa Nội tổng hợp"],
    "Mệt mỏi kéo dài": ["Khoa Nội tổng hợp"],
    "Huyết áp cao": ["Khoa Tim mạch"],
    "Đau ngực": ["Khoa Tim mạch", "Khoa Cấp cứu"],
    "Khó thở": ["Khoa Hô hấp", "Khoa Cấp cứu"],
    "Ho kéo dài": ["Khoa Hô hấp"],
    "Tiểu đường tái khám": ["Khoa Nội tiết - Đái tháo đường"],
    "Rối loạn tiêu hóa": ["Khoa Tiêu hóa"],
    "Đau dạ dày": ["Khoa Tiêu hóa"],
    
    # Nhóm Thần kinh - Cơ xương khớp
    "Đau đầu": ["Khoa Thần kinh"],
    "Đau nửa đầu": ["Khoa Thần kinh"],
    "Đau lưng": ["Khoa Cơ xương khớp"],
    "Đau khớp gối": ["Khoa Cơ xương khớp"],
    
    # Nhóm Nhi
    "Trẻ sốt cao": ["Khoa Nhi"],
    "Trẻ ho nhiều": ["Khoa Nhi"],
    "Trẻ biếng ăn": ["Khoa Nhi"],
    
    # Nhóm Sản
    "Khám thai định kỳ": ["Khoa Phụ sản"],
    "Đau bụng dưới": ["Khoa Phụ sản", "Khoa Tiêu hóa"],
    
    # Nhóm Cấp cứu / Ngoại
    "Tai nạn giao thông": ["Khoa Cấp cứu", "Khoa Chấn thương chỉnh hình và Cột sống"],
    "Tai nạn sinh hoạt": ["Khoa Cấp cứu", "Khoa Ngoại tổng hợp"],
    "Sốt cao kéo dài": ["Khoa Truyền nhiễm"],
    "Sốt xuất huyết": ["Khoa Truyền nhiễm"],
    "Phát ban": ["Khoa Da liễu"],
    "Đau mắt đỏ": ["Khoa Mắt"],
    "Viêm họng": ["Khoa Tai Mũi Họng"],
}

ALL_VISIT_REASONS = list(REASON_TO_DEPARTMENTS.keys())

# Nhóm đặc thù
PEDIATRIC_REASONS = ["Trẻ sốt cao", "Trẻ ho nhiều", "Trẻ biếng ăn"]
OBSTETRIC_REASONS = ["Khám thai định kỳ", "Đau bụng dưới"]
ELDERLY_FAVORED_REASONS = ["Huyết áp cao", "Đau ngực", "Tiểu đường tái khám", "Đau lưng", "Đau khớp gối", "Mệt mỏi kéo dài"]

# Bác sĩ
DOCTOR_LAST_NAMES = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi"]
DOCTOR_MIDDLE_NAMES = ["Văn", "Hữu", "Đức", "Thanh", "Thị", "Ngọc", "Xuân", "Quốc", "Minh"]
DOCTOR_FIRST_NAMES = ["An", "Bình", "Cường", "Dũng", "Hùng", "Lan", "Linh", "Hoa", "Hương", "Trang"]

def generate_doctor_name():
    return f"{random.choice(DOCTOR_LAST_NAMES)} {random.choice(DOCTOR_MIDDLE_NAMES)} {random.choice(DOCTOR_FIRST_NAMES)}"

# ================== 2. HÀM XỬ LÝ DATE THÔNG MINH ==================

def parse_flexible_date(date_str):
    """Hỗ trợ đọc cả format yyyy-mm-dd (MySQL) và dd-mm-yyyy (VN)"""
    date_str = date_str.strip()
    # Thử format chuẩn yyyy-mm-dd
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        pass
    # Thử format VN dd-mm-yyyy
    try:
        return datetime.strptime(date_str, "%d-%m-%Y")
    except ValueError:
        pass
    # Thử format có giờ phút giây
    try:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None

def random_visit_date_logic(created_at_patient, end_cap_date):
    """
    Logic sinh ngày khám:
    - Ngày khám PHẢI >= Ngày tạo hồ sơ bệnh nhân (created_at).
    - Ngày khám <= Hết năm 2025.
    """
    start_date = created_at_patient
    end_date = end_cap_date

    # Nếu ngày tạo hồ sơ đã vượt quá ngày chốt sổ (hiếm), thì lấy chính ngày tạo
    if start_date >= end_date:
        return start_date

    delta = end_date - start_date
    # Random số giây cộng thêm từ thời điểm tạo hồ sơ
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start_date + timedelta(seconds=random_seconds)

# ================== 3. LOAD PATIENTS VỚI DỮ LIỆU GỐC ==================

def load_patients(path):
    patients = []
    print(f"Đang đọc file {path}...")
    try:
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse DOB
                dob = parse_flexible_date(row.get("dob", ""))
                
                # Parse Created At (Thời điểm bệnh nhân vào hệ thống)
                created_at_str = row.get("created_at", "")
                created_at = parse_flexible_date(created_at_str)
                
                # Nếu không có created_at, fallback về dob (trường hợp data cũ)
                if not created_at:
                    created_at = dob if dob else datetime(2023, 1, 1)

                if dob and created_at:
                    patients.append({
                        "id": row["patient_id"],
                        "gender": row["gender"],
                        "dob": dob,
                        "created_at": created_at
                    })
    except FileNotFoundError:
        print(f"LỖI: Không tìm thấy file {path}")
        return []
    
    print(f"-> Đã load {len(patients)} bệnh nhân hợp lệ.")
    return patients

# ================== 4. LOGIC CHỌN LÝ DO & KHOA (CORE LOGIC) ==================

def pick_reason_and_dept(age_at_visit, gender):
    """Chọn lý do khám dựa trên tuổi TẠI THỜI ĐIỂM KHÁM và Giới tính"""
    
    possible_reasons = []
    
    # 1. Logic lọc theo tuổi
    if age_at_visit <= 15:
        # Trẻ em: Ưu tiên nhóm Nhi + các bệnh hô hấp chung
        possible_reasons.extend(PEDIATRIC_REASONS * 10) # Tăng trọng số
        possible_reasons.extend(["Sốt cao kéo dài", "Sốt xuất huyết", "Phát ban", "Đau mắt đỏ", "Viêm họng"])
    elif age_at_visit >= 60:
        # Người già: Ưu tiên bệnh mãn tính
        possible_reasons.extend(ELDERLY_FAVORED_REASONS * 5)
        possible_reasons.extend([r for r in ALL_VISIT_REASONS if r not in PEDIATRIC_REASONS])
    else:
        # Người lớn: Trừ nhóm Nhi
        possible_reasons.extend([r for r in ALL_VISIT_REASONS if r not in PEDIATRIC_REASONS])

    # 2. Logic lọc theo giới tính (Sản khoa)
    final_reasons = []
    for r in possible_reasons:
        if r in OBSTETRIC_REASONS:
            # Chỉ Nữ và trong độ tuổi sinh sản (15-50) mới khám sản
            if gender == "Nữ" and 15 <= age_at_visit <= 50:
                final_reasons.append(r)
        else:
            final_reasons.append(r)
            
    # Fallback nếu list rỗng
    if not final_reasons: 
        final_reasons = ["Kiểm tra sức khỏe định kỳ"]

    chosen_reason = random.choice(final_reasons)
    chosen_dept = random.choice(REASON_TO_DEPARTMENTS[chosen_reason])
    
    return chosen_reason, chosen_dept

def determine_visit_type_and_inpatient(reason, dept):
    """Quyết định loại khám và có nhập viện không"""
    reason_lower = reason.lower()
    
    # Loại khám
    if any(x in reason_lower for x in ["tai nạn", "sốt cao", "khó thở", "cấp cứu"]):
        v_type = "Cấp cứu"
    elif "định kỳ" in reason_lower:
        v_type = "Định kỳ"
    elif "tái khám" in reason_lower:
        v_type = "Tái khám"
    else:
        v_type = "Tự phát" # Khám khi thấy bệnh
        
    # Nhập viện (Logic đơn giản hóa)
    inpatient = "Không"
    prob = 0.05 # Cơ bản 5%
    
    if v_type == "Cấp cứu": prob = 0.7
    if dept in ["Khoa Phẫu thuật", "Khoa Truyền nhiễm", "Khoa Tim mạch"]: prob += 0.2
    
    if random.random() < prob:
        inpatient = "Có"
        
    return v_type, inpatient

# ================== MAIN ==================

def main():
    patients = load_patients(INPUT_PATIENTS_CSV)
    if not patients: return

    print(f"Bắt đầu sinh {NUM_VISITS} lượt khám...")
    
    with open(OUTPUT_VISITS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["visit_id", "patient_id", "visit_date", "doctor_name", 
                         "visit_type", "visit_reason", "inpatient", "department", "created_at"])
        
        for i in range(1, NUM_VISITS + 1):
            # 1. Chọn random 1 bệnh nhân
            p = random.choice(patients)
            
            # 2. Sinh ngày khám (Quan trọng: Phải sau ngày tạo hồ sơ)
            visit_dt = random_visit_date_logic(p["created_at"], VISIT_END_CAP)
            
            # 3. Tính tuổi tại thời điểm khám
            age_at_visit = visit_dt.year - p["dob"].year
            
            # 4. Chọn bệnh và khoa dựa trên tuổi & giới tính
            reason, dept = pick_reason_and_dept(age_at_visit, p["gender"])
            
            # 5. Các thông tin khác
            doc_name = generate_doctor_name()
            v_type, inpatient = determine_visit_type_and_inpatient(reason, dept)
            
            # Created_at của bản ghi khám (thường sau visit vài phút/giờ)
            rec_created_at = visit_dt + timedelta(minutes=random.randint(5, 120))
            
            writer.writerow([
                i, 
                p["id"], 
                visit_dt.strftime("%Y-%m-%d %H:%M:%S"), # Chuẩn MySQL
                doc_name,
                v_type,
                reason,
                inpatient,
                dept,
                rec_created_at.strftime("%Y-%m-%d %H:%M:%S")
            ])
            
            if i % 10000 == 0:
                print(f"-> Đã sinh: {i}")

    print(f"HOÀN TẤT. File: {OUTPUT_VISITS_CSV}")

if __name__ == "__main__":
    main()