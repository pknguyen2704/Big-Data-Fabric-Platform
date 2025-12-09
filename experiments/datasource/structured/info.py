import csv
import random
import re
import unicodedata
from datetime import datetime, date, timedelta

import pdfplumber
from faker import Faker
fake = Faker("vi_VN")
# ================== CẤU HÌNH CƠ BẢN ==================

NUM_RECORDS = 100000
OUTPUT_CSV = "patients_info.csv"
# PDF_PATH = "hn.pdf"  # sửa đúng tên file PDF của anh

random.seed(42)

# ================== HÀM TIỆN ÍCH CHUNG ==================


def strip_prefix(name: str) -> str:
    """
    Loại bỏ tiền tố Quận / Huyện / Thị xã / Phường / Xã / Thị trấn.
    Ví dụ: "Quận Hoàng Mai" -> "Hoàng Mai"
           "Phường Hoàng Liệt" -> "Hoàng Liệt"
    """
    if not name:
        return ""
    name = name.strip()
    prefixes = ["Quận", "Huyện", "Thị xã", "Phường", "Xã", "Thị trấn"]
    for p in prefixes:
        if name.startswith(p + " "):
            return name[len(p) + 1 :].strip()
    return name


def normalize_name(s: str) -> str:
    """
    Chuẩn hoá chuỗi để so sánh:
    - lower
    - bỏ khoảng trắng dư
    - bỏ dấu tiếng Việt (NFD)
    """
    if not s:
        return ""
    s = s.strip().lower()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s


# ================== 1. ĐỌC PDF → QUẬN / PHƯỜNG / STREET ==================

district_pattern = re.compile(r"^\s*\d+\.\s*(Quận|Huyện|Thị xã)\s+(.+?)(:|gồm có|$)")
ward_pattern = re.compile(r"^\s*-\s*(Phường|Xã|Thị trấn)\s+(.+?)\s*$")
street_pattern = re.compile(r"^\s*\+\s*(.+?)\s*$")


def clean_note_in_parentheses(text: str) -> str:
    # bỏ phần ghi chú trong ngoặc ở cuối
    return re.sub(r"\s*\(.*?\)\s*$", "", text).strip()


def load_location_from_pdf(pdf_path: str):
    """
    Trả về list location:
    [
      {
        "district": "Hoàng Mai",
        "ward": "Hoàng Liệt",
        "ward_type": "phuong" | "xa",
        "streets": ["Nguyễn Hữu Thọ", "Hoàng Liệt", ...]
      },
      ...
    ]
    """
    tmp = {}  # district -> { ward -> [streets] }

    current_district = None
    current_ward = None

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for raw_line in text.splitlines():
                line = raw_line.strip()
                if not line:
                    continue

                # 1) Quận / Huyện / Thị xã
                m_dist = district_pattern.match(line)
                if m_dist:
                    kind, name, _ = m_dist.groups()
                    full = f"{kind} {name.strip()}"
                    current_district = strip_prefix(full)  # chỉ còn tên quận/huyện
                    tmp.setdefault(current_district, {})
                    current_ward = None
                    continue

                # 2) Phường / Xã / Thị trấn
                m_ward = ward_pattern.match(line)
                if m_ward and current_district:
                    kind, name = m_ward.groups()
                    full_ward = f"{kind} {name.strip()}"
                    ward_clean = strip_prefix(full_ward)  # chỉ tên phường/xã/thị trấn
                    tmp[current_district].setdefault(ward_clean, [])
                    current_ward = ward_clean
                    continue

                # 3) Street
                m_street = street_pattern.match(line)
                if m_street and current_district and current_ward:
                    street = clean_note_in_parentheses(m_street.group(1))
                    if street:
                        tmp[current_district][current_ward].append(street)

    locations = []

    # xác định quận nội thành để phân loại ward_type
    inner_districts = {
        "Ba Đình",
        "Hoàn Kiếm",
        "Đống Đa",
        "Hai Bà Trưng",
        "Hoàng Mai",
        "Thanh Xuân",
        "Cầu Giấy",
        "Tây Hồ",
        "Long Biên",
        "Nam Từ Liêm",
        "Bắc Từ Liêm",
        "Hà Đông",
    }

    for district, wards in tmp.items():
        for ward, streets in wards.items():
            if district in inner_districts:
                wtype = "phuong"
            else:
                wtype = "xa"  # coi ngoại thành là xã/thị trấn

            locations.append(
                {
                    "district": district,
                    "ward": ward,
                    "ward_type": wtype,
                    "streets": streets[:],
                }
            )

    return locations


LOCATIONS = load_location_from_pdf(PDF_PATH)
if not LOCATIONS:
    raise RuntimeError("Không load được dữ liệu địa chỉ từ PDF – kiểm tra lại PDF_PATH.")


# ================== 2. GIẢ LẬP THÔN NGOẠI THÀNH (KHÔNG LIST CỨNG THEO XÃ) ==================

THON_CORES = [
    # hướng & vị trí
    "Thượng",
    "Trung",
    "Hạ",
    "Đông",
    "Đoài",
    "Tây",
    "Bắc",
    "Nam",
    "Nội",
    "Ngoại",
    "Mới",
    "Cũ",
    "Trong",
    "Ngoài",
    "Trên",
    "Dưới",
    # địa hình / đặc trưng
    "Đồi",
    "Đồng",
    "Đầm",
    "Bãi",
    "Cầu",
    "Chùa",
    "Đình",
    "Bến",
    "Sông",
    "Gò",
    # chữ Hán - Việt
    "Phú",
    "Phúc",
    "Lộc",
    "Thọ",
    "An",
    "Bình",
    "Hòa",
    "Hưng",
    "Thịnh",
    "Vượng",
    "Vinh",
    "Nhân",
    "Đức",
    "Tài",
    "Mỹ",
    "Thanh",
    "Xuân",
    "Quang",
    "Minh",
    "Long",
    "Tiến",
    "Thuận",
]


def random_thon_name(ward_name: str, district_name: str) -> str:
    """
    Sinh tên thôn giả lập, nhưng:
    - Không trùng với ward
    - Không trùng với district
    (so sánh theo normalize_name)
    """
    norm_ward = normalize_name(ward_name)
    norm_dist = normalize_name(district_name)

    for _ in range(30):
        core = random.choice(THON_CORES)
        # phần lõi để so sánh
        core_norm = normalize_name(core)
        if core_norm in {norm_ward, norm_dist}:
            continue
        # tên thôn đầy đủ
        thon = f"Thôn {core}"
        return thon

    # fallback rất hiếm khi xảy ra
    return "Thôn Nhân Hòa"


# ================== 3. SINH ADDRESS DỰA TRÊN DISTRICT / WARD / STREET / THÔN ==================


def random_house_number():
    return random.randint(1, 999)


def random_ngo_number():
    return random.randint(1, 200)


def random_ngach_number():
    return random.randint(1, 100)


def generate_address_entry(location: dict) -> str:
    """
    - Không đưa ward vào address (ward ở cột riêng).
    - Trong address:
        + street không được trùng ward hoặc district
        + thôn (cho xã/thị trấn) cũng không trùng ward hoặc district
    - Nội thành: 3 kiểu: mặt đường, trong ngõ, trong ngách.
    - Ngoại thành: CHỈ số nhà + thôn (không có đường, không có ngõ/ngách).
    """
    ward_type = location["ward_type"]
    ward_name = location["ward"]
    district_name = location["district"]

    norm_ward = normalize_name(ward_name)
    norm_dist = normalize_name(district_name)

    # 1. Chọn street, loại những tên trùng ward hoặc district
    all_streets = [
        s.strip()
        for s in location["streets"]
        if isinstance(s, str) and s.strip()
    ]

    filtered_streets = [
        s
        for s in all_streets
        if normalize_name(s) not in {norm_ward, norm_dist}
    ]

    if filtered_streets:
        street = random.choice(filtered_streets)
    else:
        # fallback: tên generic chắc chắn khác ward/district
        street = "Đường Liên Xã"

    house = random_house_number()
    ngo = random_ngo_number()
    ngach = random_ngach_number()

    r = random.random()
    is_rural = ward_type in {"xa"}  # ngoại thành

    if not is_rural:
        # ---- Nội thành: phường ----
        # 50% mặt đường, 30% trong ngõ, 20% trong ngách
        if r < 0.5:
            addr = f"số {house} {street}"
        elif r < 0.8:
            addr = f"số {house} ngõ {ngo} {street}"
        else:
            addr = f"số {house} ngách {ngach} ngõ {ngo} {street}"
    else:
        # ---- Ngoại thành: xã / thị trấn ----
        # THEO YÊU CẦU: chỉ số nhà + thôn, không đường, không ngõ/ngách
        thon = random_thon_name(ward_name, district_name)
        addr = f"số {house} {thon}"

    return addr



# ================== 4. CÁC THÀNH PHẦN KHÁC: CCCD, BHYT, SĐT, HỌ TÊN, DÂN TỘC, JOB ==================

OTHER_PROVINCE_CODES = [
    "002",
    "004",
    "006",
    "008",
    "010",
    "011",
    "012",
    "014",
    "015",
    "017",
    "019",
    "020",
    "022",
    "024",
    "025",
    "026",
    "027",
    "030",
    "031",
    "033",
    "034",
    "036",
    "037",
    "038",
    "040",
    "042",
    "044",
    "045",
    "046",
    "048",
    "049",
    "051",
    "052",
    "054",
    "056",
    "058",
    "060",
    "062",
    "064",
    "066",
    "067",
    "068",
    "070",
    "072",
    "074",
    "075",
    "077",
    "079",
    "080",
    "082",
    "083",
    "084",
    "086",
    "087",
    "089",
    "091",
    "092",
    "093",
    "094",
    "095",
    "096",
]


def generate_cccd(dob: date, gender: str) -> str:
    """
    CCCD 12 số giả lập gần đúng:
    AAA B YY XXXXXX
    - AAA: mã tỉnh (001 Hà Nội; tỉnh khác random)
    - B: mã giới tính + thế kỷ (đơn giản: Nam=0, Nữ=1, Khác=2)
    - YY: 2 số cuối năm sinh
    - XXXXXX: 6 số random
    """
    if random.random() < 0.6:
        province_code = "001"  # Hà Nội
    else:
        province_code = random.choice(OTHER_PROVINCE_CODES)

    if gender == "Nam":
        gender_code = "0"
    elif gender == "Nữ":
        gender_code = "1"
    else:
        gender_code = "2"

    yy = f"{dob.year % 100:02d}"
    tail = f"{random.randint(0, 999999):06d}"
    return province_code + gender_code + yy + tail


def generate_health_insurance_id(existing: set) -> str:
    while True:
        hid = f"{random.randint(0, 9999999999):010d}"
        if hid not in existing:
            existing.add(hid)
            return hid


PHONE_PREFIXES = [
    "032",
    "033",
    "034",
    "035",
    "036",
    "037",
    "038",
    "039",  # Viettel
    "096",
    "097",
    "098",
    "081",
    "082",
    "083",
    "084",
    "085",  # Vinaphone
    "086",
    "088",
    "089",
    "090",
    "091",  # Mobi
]


def generate_phone() -> str:
    prefix = random.choice(PHONE_PREFIXES)
    tail = f"{random.randint(0, 9999999):07d}"
    return prefix + tail


ETHNICITIES = [
    "Kinh",
    "Tày",
    "Thái",
    "Mường",
    "Khmer",
    "Hoa",
    "Nùng",
    "HMông",
    "Dao",
    "Gia Rai",
    "Ê Đê",
    "Ba Na",
    "Sán Chay",
    "Chăm",
    "Cơ Ho",
    "Xơ Đăng",
    "Sán Dìu",
    "Hrê",
]



def random_ethnicity() -> str:
    if random.random() < 0.7:
        return "Kinh"
    return random.choice([e for e in ETHNICITIES if e != "Kinh"])


def random_job_by_age(age: int) -> str:
    """
    Chọn nghề nghiệp phù hợp với nhóm tuổi:
    - < 6 tuổi: chưa có nghề
    - 6–17: học sinh là chính
    - 18–22: sinh viên + 1 số nghề part-time / mới đi làm
    - 23–60: tuổi lao động, phân tán nhiều nghề
    - > 60: thiên về nghỉ hưu, nội trợ, nông dân, buôn bán nhỏ
    """

    if age < 6:
        return "Chưa có nghề"

    if 6 <= age <= 17:
        # chủ yếu là học sinh
        if random.random() < 0.9:
            return "Học sinh"
        else:
            return random.choice(["Bán hàng part-time", "Phụ giúp gia đình"])

    if 18 <= age <= 22:
        r = random.random()
        if r < 0.6:
            return "Sinh viên"
        elif r < 0.8:
            return random.choice(
                [
                    "Nhân viên phục vụ",
                    "Bán hàng",
                    "Nhân viên chăm sóc khách hàng",
                    "Nhân viên văn phòng",
                ]
            )
        else:
            return random.choice(
                [
                    "Công nhân",
                    "Kinh doanh tự do",
                    "Tài xế",
                ]
            )

    if 23 <= age <= 60:
        jobs_working = [
            "Công nhân",
            "Nông dân",
            "Nhân viên văn phòng",
            "Giảng viên",
            "Bác sĩ",
            "Y tá",
            "Kỹ sư",
            "Lập trình viên",
            "Tài xế",
            "Kinh doanh tự do",
            "Nội trợ",
            "Công an",
            "Bộ đội",
            "Luật sư",
            "Kế toán",
            "Giáo viên",
            "Nhà báo",
            "Kiến trúc sư",
            "Dược sĩ",
            "Nhân viên ngân hàng",
            "Đầu bếp",
            "Hướng dẫn viên du lịch",
            "Nhân viên bán hàng",
            "Nhân viên marketing",
        ]
        return random.choice(jobs_working)

    # > 60
    jobs_elderly = [
        "Nghỉ hưu",
        "Nội trợ",
        "Nông dân",
        "Buôn bán nhỏ",
        "Kinh doanh tự do",
    ]
    return random.choice(jobs_elderly)



def random_job() -> str:
    return random.choice(JOBS)


MALE_FIRST_NAMES = [
    "Anh",
    "Bình",
    "Cường",
    "Dũng",
    "Đạt",
    "Hùng",
    "Huy",
    "Khang",
    "Khôi",
    "Long",
    "Minh",
    "Nam",
    "Phong",
    "Quân",
    "Quang",
    "Sơn",
    "Thắng",
    "Thiện",
    "Trung",
    "Tuấn",
]
FEMALE_FIRST_NAMES = [
    "Anh",
    "Chi",
    "Dung",
    "Giang",
    "Hà",
    "Hạnh",
    "Hoa",
    "Hương",
    "Khánh",
    "Lan",
    "Linh",
    "Ly",
    "Mai",
    "My",
    "Ngọc",
    "Nhung",
    "Phương",
    "Quỳnh",
    "Thảo",
    "Trang",
]
LAST_NAMES = [
    "Nguyễn",
    "Trần",
    "Lê",
    "Phạm",
    "Hoàng",
    "Huỳnh",
    "Phan",
    "Vũ",
    "Võ",
    "Đặng",
    "Bùi",
    "Đỗ",
    "Hồ",
    "Ngô",
    "Dương",
    "Lý",
]
MIDDLE_NAMES_COMMON = [
    "Văn",
    "Hữu",
    "Đức",
    "Thanh",
    "Thị",
    "Ngọc",
    "Xuân",
    "Quốc",
    "Minh",
    "Anh",
    "Gia",
]


def generate_fullname_and_gender():
    r = random.random()
    if r < 0.49:
        gender = "Nam"
        first = random.choice(MALE_FIRST_NAMES)
    elif r < 0.98:
        gender = "Nữ"
        first = random.choice(FEMALE_FIRST_NAMES)
    else:
        gender = "Khác"
        first = random.choice(list(set(MALE_FIRST_NAMES + FEMALE_FIRST_NAMES)))

    last = random.choice(LAST_NAMES)
    middle = random.choice(MIDDLE_NAMES_COMMON)

    fullname = f"{last} {middle} {first}"
    return fullname, gender


# ================== 5. NGÀY THÁNG: dob, created_at, updated_at, age ==================


def random_datetime(start: datetime, end: datetime) -> datetime:
    delta = end - start
    seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=seconds)


def generate_dates():
    """
    Sinh ngày tháng hợp lý hơn:
    - created_at: 2024-01-01 -> 2025-12-05
    - Chọn age trước (0–95) theo phân bố:
        + 0–5:   ~5%  (trẻ nhỏ)
        + 6–17:  ~20% (học sinh)
        + 18–22: ~20% (sinh viên / mới đi làm)
        + 23–60: ~45% (tuổi lao động chính)
        + 61–95: ~10% (người già)
    - dob sinh sao cho đúng tuổi tại thời điểm created_at
    - updated_at >= created_at
    """
    # 1. created_at
    created_start = datetime(2024, 1, 1, 0, 0, 0)
    created_end = datetime(2025, 12, 5, 23, 59, 59)
    created_at = random_datetime(created_start, created_end)

    # 2. chọn tuổi theo phân bố
    r = random.random()
    if r < 0.05:
        age = random.randint(0, 5)
    elif r < 0.25:
        age = random.randint(6, 17)
    elif r < 0.45:
        age = random.randint(18, 22)
    elif r < 0.90:
        age = random.randint(23, 60)
    else:
        age = random.randint(61, 95)

    # 3. sinh dob phù hợp với age tại thời điểm created_at
    #    làm đơn giản: random đến khi age khớp
    while True:
        year = created_at.year - age
        month = random.randint(1, 12)
        # tránh lỗi ngày tháng (vd 31/02)
        if month in {1, 3, 5, 7, 8, 10, 12}:
            day_max = 31
        elif month in {4, 6, 9, 11}:
            day_max = 30
        else:
            # tháng 2
            day_max = 29  # chấp nhận 29 để đơn giản
        day = random.randint(1, day_max)
        try:
            dob = date(year, month, day)
        except ValueError:
            continue

        # tính lại tuổi check
        age_check = created_at.year - dob.year - (
            (created_at.month, created_at.day) < (dob.month, dob.day)
        )
        if age_check == age:
            break

    # 4. updated_at >= created_at
    updated_end = created_end
    updated_at = random_datetime(created_at, updated_end)

    return dob, created_at, updated_at, age


# ================== 6. GENERATOR CHÍNH ==================


def main():
    used_cccd = set()
    used_hid = set()

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "patient_id",
                "fullname",
                "age",
                "gender",
                "dob",
                "ethnicity",
                "ward",
                "district",
                "city",
                "address",
                "phone_number",
                "health_insurance_id",
                "job",
                "created_at",
                "updated_at",
            ]
        )

        for _ in range(NUM_RECORDS):
            # 1. Địa chỉ
            location = random.choice(LOCATIONS)
            district = location["district"]
            ward = location["ward"]
            city = "Hà Nội"

            address = generate_address_entry(location)

            # 2. Họ tên & giới tính
            fullname, gender = generate_fullname_and_gender()

            # 3. Dân tộc, nghề nghiệp, điện thoại
            ethnicity = random_ethnicity()
            phone = generate_phone()

            # 4. Ngày tháng & tuổi
            dob, created_at, updated_at, age = generate_dates()

            job = random_job_by_age(age)

            # 5. CCCD duy nhất
            while True:
                cccd = generate_cccd(dob, gender)
                if cccd not in used_cccd:
                    used_cccd.add(cccd)
                    break

            # 6. BHYT duy nhất
            health_id = generate_health_insurance_id(used_hid)

            writer.writerow(
                [
                    cccd,
                    fullname,
                    age,
                    gender,
                    dob.strftime("%d-%m-%Y"),
                    ethnicity,
                    ward,
                    district,
                    city,
                    address,
                    phone,
                    health_id,
                    job,
                    created_at.strftime("%d-%m-%Y %H:%M:%S"),
                    updated_at.strftime("%d-%m-%Y %H:%M:%S"),
                ]
            )

    print(f"Đã sinh xong {NUM_RECORDS} bản ghi vào {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
