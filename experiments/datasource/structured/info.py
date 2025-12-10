import csv
import random
from datetime import datetime, date, timedelta

# ================== CẤU HÌNH ==================
INPUT_SEED_FILE = "patients_seed.csv"
OUTPUT_INFO_FILE = "info.csv"
LAST_N_RECORDS_2025 = 5000 
RANDOM_SEED = 42

random.seed(RANDOM_SEED)

# Dữ liệu địa chính Hà Nội
HANOI_LOCATIONS = {
    "Ba Đình": ["Phúc Xá", "Trúc Bạch", "Vĩnh Phúc", "Cống Vị", "Liễu Giai", "Nguyễn Trung Trực", "Quán Thánh", "Ngọc Hà", "Điện Biên", "Đội Cấn", "Ngọc Khánh", "Kim Mã", "Giảng Võ", "Thành Công"],
    "Hoàn Kiếm": ["Phúc Tân", "Đồng Xuân", "Hàng Mã", "Hàng Buồm", "Hàng Đào", "Hàng Bồ", "Cửa Đông", "Lý Thái Tổ", "Hàng Bạc", "Hàng Gai", "Chương Dương", "Hàng Trống", "Cửa Nam", "Hàng Bông", "Tràng Tiền", "Trần Hưng Đạo", "Phan Chu Trinh", "Hàng Bài"],
    "Đống Đa": ["Cát Linh", "Văn Miếu", "Quốc Tử Giám", "Láng Thượng", "Ô Chợ Dừa", "Văn Chương", "Hàng Bột", "Láng Hạ", "Khâm Thiên", "Thổ Quan", "Nam Đồng", "Trung Phụng", "Quang Trung", "Trung Liệt", "Phương Liên", "Thịnh Quang", "Trung Tự", "Kim Liên", "Khương Thượng", "Ngã Tư Sở", "Phương Mai"],
    "Hai Bà Trưng": ["Nguyễn Du", "Bạch Đằng", "Phạm Đình Hổ", "Lê Đại Hành", "Đồng Nhân", "Phố Huế", "Đống Mác", "Thanh Lương", "Thanh Nhàn", "Cầu Dền", "Bách Khoa", "Đồng Tâm", "Vĩnh Tuy", "Bạch Mai", "Quỳnh Mai", "Quỳnh Lôi", "Minh Khai", "Trương Định"],
    "Cầu Giấy": ["Nghĩa Đô", "Nghĩa Tân", "Mai Dịch", "Dịch Vọng", "Dịch Vọng Hậu", "Quan Hoa", "Yên Hòa", "Trung Hòa"],
    "Thanh Xuân": ["Khương Đình", "Khương Mai", "Khương Trung", "Hạ Đình", "Kim Giang", "Nhân Chính", "Phương Liệt", "Thanh Xuân Bắc", "Thanh Xuân Nam", "Thanh Xuân Trung", "Thượng Đình"],
    "Hà Đông": ["Nguyễn Trãi", "Mộ Lao", "Văn Quán", "Vạn Phúc", "Yết Kiêu", "Quang Trung", "La Khê", "Phú La", "Phúc La", "Hà Cầu", "Yên Nghĩa", "Kiến Hưng", "Phú Lương", "Phú Lãm", "Dương Nội", "Biên Giang", "Đồng Mai"],
}
INNER_DISTRICTS = {"Ba Đình", "Hoàn Kiếm", "Đống Đa", "Hai Bà Trưng", "Cầu Giấy", "Thanh Xuân", "Hà Đông"}
STREET_NAMES = ["Nguyễn Trãi", "Lê Văn Lương", "Giải Phóng", "Trường Chinh", "Láng", "Xuân Thủy", "Cầu Giấy", "Phạm Hùng", "Nguyễn Chí Thanh", "Liễu Giai", "Đội Cấn", "Kim Mã", "Giảng Võ", "Tôn Đức Thắng", "Nguyễn Lương Bằng", "Tây Sơn", "Chùa Bộc", "Thái Hà", "Huỳnh Thúc Kháng", "Hoàng Quốc Việt"]

def extract_info_from_cccd(cccd: str):
    if len(cccd) != 12: return 1990, "Nam"
    g_code = int(cccd[3])
    yy = int(cccd[4:6])
    if g_code in [0, 1]:
        birth_year = 1900 + yy
        gender = "Nam" if g_code == 0 else "Nữ"
    elif g_code in [2, 3]:
        birth_year = 2000 + yy
        gender = "Nam" if g_code == 2 else "Nữ"
    else:
        birth_year = 1990
        gender = "Nam"
    return birth_year, gender

def generate_dob_and_visit_date(birth_year: int, is_forced_2025: bool):
    """
    Sinh DOB và Created_at sao cho logic không bị lỗi (Khám sau khi sinh)
    """
    # 1. Sinh DOB
    d1 = date(birth_year, 1, 1)
    d2 = date(birth_year, 12, 31)
    dob = d1 + timedelta(days=random.randint(0, (d2 - d1).days))
    
    # 2. Xác định khung thời gian khám
    if is_forced_2025:
        visit_start = datetime(2025, 1, 1, 8, 0, 0)
        visit_end = datetime(2025, 12, 31, 17, 0, 0)
    else:
        visit_start = datetime(2023, 1, 1, 8, 0, 0)
        visit_end = datetime(2025, 12, 31, 17, 0, 0)
    
    # 3. FIX LOGIC QUAN TRỌNG:
    # Chuyển DOB thành datetime để so sánh
    dob_datetime = datetime(dob.year, dob.month, dob.day, 0, 0, 0)
    
    # Nếu ngày sinh nằm SAU ngày bắt đầu khám dự kiến (ví dụ sinh cuối 2023 mà khung khám từ đầu 2023)
    if dob_datetime >= visit_start:
        # Dời ngày bắt đầu khám lên bằng ngày sinh (khám sơ sinh) hoặc sau đó 1 ngày
        visit_start = dob_datetime + timedelta(hours=random.randint(2, 24))

    # Nếu sau khi dời mà start vượt quá end (ví dụ sinh 31/12/2025 mà end là 31/12/2025)
    if visit_start > visit_end:
        visit_start = visit_end # Ép khám vào giờ chót

    # Random trong khoảng hợp lệ
    delta = visit_end - visit_start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    created_at = visit_start + timedelta(seconds=random_seconds)
    
    updated_at = created_at + timedelta(minutes=random.randint(30, 4000))
    
    return dob, created_at, updated_at

def random_job_by_age(age: int) -> str:
    if age < 6: return "Trẻ em"
    if 6 <= age <= 18: return "Học sinh"
    if 18 < age <= 22: return random.choice(["Sinh viên", "Lao động tự do"])
    if age > 60: return random.choice(["Hưu trí", "Nội trợ", "Người cao tuổi"])
    return random.choice(["Kỹ sư", "Bác sĩ", "Giáo viên", "Công nhân", "Nhân viên văn phòng", "Kinh doanh", "Lái xe", "Kế toán"])

def generate_fullname(gender: str) -> str:
    ho = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng"]
    dem = ["Văn", "Hữu", "Đức", "Minh", "Quang"] if gender == "Nam" else ["Thị", "Thu", "Ngọc", "Phương", "Thanh"]
    ten = ["Hùng", "Dũng", "Nam", "Khánh", "Long", "Quân"] if gender == "Nam" else ["Lan", "Mai", "Hoa", "Hương", "Trang", "Linh"]
    return f"{random.choice(ho)} {random.choice(dem)} {random.choice(ten)}"

def generate_address(district: str, ward: str) -> str:
    house = random.randint(1, 999)
    if district in INNER_DISTRICTS:
        street = random.choice(STREET_NAMES)
        return f"Số {house}, {street}" if random.random() < 0.7 else f"Số {house}, Ngõ {random.randint(1,200)}, {street}"
    else:
        return f"{random.choice(['Thôn Thượng', 'Thôn Hạ', 'Xóm 1'])}"

def main():
    print("Đang xử lý tạo Info...")
    rows = []
    
    try:
        with open(INPUT_SEED_FILE, "r", encoding="utf-8") as f:
            seeds = list(csv.DictReader(f))
    except FileNotFoundError:
        print(f"Lỗi: Thiếu file {INPUT_SEED_FILE}. Hãy chạy Bước 1 trước.")
        return

    total = len(seeds)
    for idx, seed in enumerate(seeds):
        cccd = seed["patient_id"]
        
        # 1. Lấy năm sinh
        birth_year, gender = extract_info_from_cccd(cccd)
        
        # 2. Logic 5000 người cuối
        is_forced_2025 = (idx >= total - LAST_N_RECORDS_2025)
        
        # 3. Sinh ngày tháng (Logic đã fix)
        dob, created_at, updated_at = generate_dob_and_visit_date(birth_year, is_forced_2025)
        
        # 4. Tính tuổi
        age = created_at.year - dob.year - ((created_at.month, created_at.day) < (dob.month, dob.day))
        
        # 5. Các field khác
        dist = random.choice(list(HANOI_LOCATIONS.keys()))
        ward = random.choice(HANOI_LOCATIONS[dist])
        
        rows.append({
            "patient_id": cccd,
            "fullname": generate_fullname(gender),
            "age": age,
            "gender": gender,
            "dob": dob.strftime("%Y-%m-%d"),
            "ethnicity": "Kinh",
            "ward": ward, "district": dist, "city": "Hà Nội",
            "address": generate_address(dist, ward),
            "phone_number": "09" + "".join([str(random.randint(0,9)) for _ in range(8)]),
            "health_insurance_id": seed["health_insurance_id"],
            "job": random_job_by_age(age),
            "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": updated_at.strftime("%Y-%m-%d %H:%M:%S")
        })
        
        if (idx + 1) % 10000 == 0: print(f"-> {idx + 1}/{total}")

    with open(OUTPUT_INFO_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
        
    print(f"HOÀN TẤT: {OUTPUT_INFO_FILE}")

if __name__ == "__main__":
    main()