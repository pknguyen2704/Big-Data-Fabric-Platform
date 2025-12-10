import csv
import random
from datetime import datetime, timedelta

# ================== CẤU HÌNH ==================
INPUT_PATIENTS_CSV = "info.csv"       # File nhân khẩu học
INPUT_VISITS_CSV = "visits.csv" # File lịch sử khám
OUTPUT_HEALTH_CSV = "health_records.csv"

random.seed(100) # Seed mới để dữ liệu phong phú

# ================== 1. KNOWLEDGE BASE: DANH MỤC XÉT NGHIỆM & QUY TẮC ==================

# Catalog định nghĩa các chỉ số: Đơn vị, Dải tham chiếu (bình thường), Nhóm
TEST_CATALOG = {
    # --- Sinh hóa / Huyết học ---
    "GLUCOSE": {"name": "Định lượng Glucose (Máu)", "unit": "mmol/L", "ref_min": 3.9, "ref_max": 6.4, "type": "numeric"},
    "HBA1C":   {"name": "Định lượng HbA1c", "unit": "%", "ref_min": 4.0, "ref_max": 6.0, "type": "numeric"},
    "CHOLESTEROL": {"name": "Cholesterol toàn phần", "unit": "mmol/L", "ref_min": 3.9, "ref_max": 5.2, "type": "numeric"},
    "TRIGLYCERIDE": {"name": "Triglyceride", "unit": "mmol/L", "ref_min": 0.46, "ref_max": 1.88, "type": "numeric"},
    "URE":     {"name": "Định lượng Ure", "unit": "mmol/L", "ref_min": 2.5, "ref_max": 7.5, "type": "numeric"},
    "CREATININE": {"name": "Định lượng Creatinine", "unit": "µmol/L", "ref_min": 62, "ref_max": 120, "type": "numeric"},
    "AST":     {"name": "AST (GOT)", "unit": "U/L", "ref_min": 0, "ref_max": 37, "type": "numeric"},
    "ALT":     {"name": "ALT (GPT)", "unit": "U/L", "ref_min": 0, "ref_max": 40, "type": "numeric"},
    "URIC":    {"name": "Acid Uric", "unit": "µmol/L", "ref_min": 200, "ref_max": 420, "type": "numeric"},
    "WBC":     {"name": "Tổng phân tích TB máu: Bạch cầu (WBC)", "unit": "G/L", "ref_min": 4.0, "ref_max": 10.0, "type": "numeric"},
    "RBC":     {"name": "Tổng phân tích TB máu: Hồng cầu (RBC)", "unit": "T/L", "ref_min": 3.8, "ref_max": 5.8, "type": "numeric"},
    "PLT":     {"name": "Tổng phân tích TB máu: Tiểu cầu (PLT)", "unit": "G/L", "ref_min": 150, "ref_max": 450, "type": "numeric"},
    "CRP":     {"name": "Định lượng CRP (Viêm)", "unit": "mg/L", "ref_min": 0, "ref_max": 5, "type": "numeric"},
    "TROPONIN": {"name": "Troponin T (Tim mạch)", "unit": "ng/L", "ref_min": 0, "ref_max": 14, "type": "numeric"},
    
    # --- Chẩn đoán hình ảnh / Thăm dò chức năng ---
    "XRAY_CHEST": {"name": "X-Quang ngực thẳng", "type": "text"},
    "ULTRASOUND_ABD": {"name": "Siêu âm ổ bụng tổng quát", "type": "text"},
    "ECG": {"name": "Điện tâm đồ (ECG)", "type": "text"},
    "ENT_SCOPE": {"name": "Nội soi Tai Mũi Họng", "type": "text"},
    "GASTRO_SCOPE": {"name": "Nội soi Dạ dày - Tá tràng", "type": "text"},
}

# Mapping: Khoa/Triệu chứng -> Cần làm xét nghiệm gì?
DEPT_TEST_RULES = {
    "Khoa Nội tiết - Đái tháo đường": ["GLUCOSE", "HBA1C", "CREATININE", "URE"],
    "Khoa Tim mạch": ["ECG", "CHOLESTEROL", "TRIGLYCERIDE", "TROPONIN", "AST", "ALT"],
    "Khoa Hô hấp": ["XRAY_CHEST", "WBC", "CRP"],
    "Khoa Tiêu hóa": ["ULTRASOUND_ABD", "AST", "ALT", "GASTRO_SCOPE", "WBC"],
    "Khoa Thận - Tiết niệu": ["URE", "CREATININE", "ULTRASOUND_ABD", "WBC"],
    "Khoa Cơ xương khớp": ["URIC", "CRP", "WBC"],
    "Khoa Nhi": ["WBC", "CRP", "ENT_SCOPE"],
    "Khoa Tai Mũi Họng": ["ENT_SCOPE", "WBC"],
    "Khoa Cấp cứu": ["WBC", "RBC", "PLT", "GLUCOSE", "CREATININE", "ECG", "XRAY_CHEST"],
    "Khoa Nội tổng hợp": ["GLUCOSE", "CHOLESTEROL", "AST", "ALT", "WBC", "RBC", "ULTRASOUND_ABD"],
    "Khoa Truyền nhiễm": ["WBC", "CRP", "AST", "ALT"],
}

# ================== 2. LOGIC SINH KẾT QUẢ (ENGINE) ==================

def generate_blood_type():
    return random.choices(["A", "B", "AB", "O"], weights=[0.25, 0.25, 0.1, 0.4])[0]

def generate_body_metrics(age, gender):
    """Sinh chiều cao/cân nặng cơ bản dựa trên tuổi giới"""
    if age < 5: 
        h = random.randint(50, 110)
        w = random.randint(5, 20)
    elif age < 15:
        h = random.randint(110, 160)
        w = random.randint(20, 50)
    else:
        if gender == "Nam":
            h = random.randint(160, 185)
            w = random.randint(55, 90)
        else:
            h = random.randint(150, 170)
            w = random.randint(45, 75)
    return h, w

def calculate_bmi(h_cm, w_kg):
    if h_cm == 0: return 0
    return round(w_kg / ((h_cm/100)**2), 2)

def generate_numeric_value(test_key, context_flags):
    """
    Sinh giá trị số.
    context_flags: Danh sách các cờ hiệu (vd: 'DIABETES', 'INFECTION', 'HYPERTENSION')
    để quyết định xem chỉ số có nên bất thường hay không.
    """
    cfg = TEST_CATALOG[test_key]
    min_v, max_v = cfg["ref_min"], cfg["ref_max"]
    span = max_v - min_v
    
    # Mặc định: Giá trị bình thường (Normal distribution around center)
    val = random.uniform(min_v + 0.1*span, max_v - 0.1*span)
    
    # --- LOGIC BẤT THƯỜNG ---
    is_abnormal = False
    
    # 1. Tiểu đường -> Glucose, HbA1c cao
    if "DIABETES" in context_flags and test_key in ["GLUCOSE", "HBA1C"]:
        if random.random() < 0.8: # 80% cơ hội cao
            val = random.uniform(max_v, max_v + 2*span)
            is_abnormal = True

    # 2. Nhiễm trùng (Sốt) -> WBC, CRP cao
    if "INFECTION" in context_flags and test_key in ["WBC", "CRP"]:
        if random.random() < 0.9:
            val = random.uniform(max_v, max_v + 5.0)
            is_abnormal = True

    # 3. Mỡ máu/Tim mạch -> Cholesterol cao
    if "LIPID" in context_flags and test_key in ["CHOLESTEROL", "TRIGLYCERIDE"]:
        if random.random() < 0.7:
            val = random.uniform(max_v, max_v + 3.0)
            is_abnormal = True
            
    # 4. Suy thận -> Creatinine cao
    if "RENAL" in context_flags and test_key in ["CREATININE", "URE"]:
        val = random.uniform(max_v, max_v * 3)
        is_abnormal = True

    # 5. Gout -> Uric cao
    if "GOUT" in context_flags and test_key == "URIC":
        val = random.uniform(max_v, 800)
        is_abnormal = True

    return round(val, 2), is_abnormal

def generate_text_result(test_key, context_flags):
    """Sinh kết quả dạng Text (Chẩn đoán hình ảnh)"""
    normal_texts = [
        "Hình ảnh trong giới hạn bình thường.",
        "Chưa phát hiện tổn thương khu trú.",
        "Các cấu trúc giải phẫu bình thường.",
        "Không thấy hình ảnh bất thường."
    ]
    
    abnormal_texts = {
        "XRAY_CHEST": ["Đám mờ thùy dưới phổi phải", "Rốn phổi đậm", "Hình ảnh viêm phế quản", "Bóng tim to nhẹ"],
        "ULTRASOUND_ABD": ["Gan nhiễm mỡ độ 1", "Sỏi túi mật kích thước 5mm", "Nang thận phải", "Gan thô nhẹ"],
        "ECG": ["Nhịp xoang nhanh", "Thiếu máu cơ tim cục bộ thành dưới", "Ngoại tâm thu thất rải rác"],
        "ENT_SCOPE": ["Họng sung huyết đỏ", "Amidan quá phát độ 2", "Viêm mũi xoang cấp"],
        "GASTRO_SCOPE": ["Viêm trợt hang vị dạ dày", "Trào ngược thực quản độ A", "Viêm niêm mạc tá tràng"]
    }
    
    # Nếu có cờ báo bệnh, tăng tỷ lệ ra kết quả bất thường
    has_disease = len(context_flags) > 0
    if has_disease and random.random() < 0.6:
        choices = abnormal_texts.get(test_key, ["Bất thường không đặc hiệu"])
        return random.choice(choices), "Bất thường"
    
    return random.choice(normal_texts), "Bình thường"

# ================== 3. DATA LOADING & PREPARATION ==================

def load_patient_static_data(info_path):
    """
    Đọc file info, tạo bộ nhớ đệm cho các chỉ số CỐ ĐỊNH của bệnh nhân:
    - Nhóm máu
    - Chiều cao nền
    - Cân nặng nền
    - Bệnh nền (Comorbidities) để làm flag
    """
    print("Đang tải dữ liệu bệnh nhân...")
    p_data = {}
    try:
        with open(info_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                pid = row["patient_id"]
                try:
                    age = int(row["age"])
                except:
                    age = 30
                gender = row["gender"]
                
                # Sinh dữ liệu tĩnh
                h, w = generate_body_metrics(age, gender)
                b_type = generate_blood_type()
                
                # Phân tích bệnh nền để tạo cờ (Flags)
                job = row.get("job", "") # Nghề nghiệp cũng có thể gợi ý
                
                # Dùng thông tin từ file info hoặc tự tạo giả lập logic bệnh nền nếu file info ko có cột comorbidities
                # Ở đây giả sử ta tự deduce từ age cho đơn giản hoặc nếu có cột comorbidities thì parse
                flags = []
                if age > 50: flags.append("LIPID")
                if age > 65: flags.append("HYPERTENSION")
                
                p_data[pid] = {
                    "age": age,
                    "gender": gender,
                    "blood_type": b_type,
                    "height": h,
                    "base_weight": w,
                    "flags": set(flags) # Set các cờ bệnh
                }
    except FileNotFoundError:
        print("Lỗi: Không tìm thấy file info.csv")
    
    return p_data

def parse_date(d_str):
    try:
        return datetime.strptime(d_str, "%Y-%m-%d %H:%M:%S")
    except:
        return None

# ================== MAIN PROCESS ==================

def main():
    # 1. Load thông tin tĩnh của bệnh nhân
    patients_db = load_patient_static_data(INPUT_PATIENTS_CSV)
    if not patients_db: return

    print("Đang xử lý visits và sinh xét nghiệm...")
    
    # 2. Đọc file visits và xử lý dòng chảy (stream processing) để tiết kiệm RAM
    with open(INPUT_VISITS_CSV, "r", encoding="utf-8") as f_in, \
         open(OUTPUT_HEALTH_CSV, "w", newline="", encoding="utf-8") as f_out:
        
        reader = csv.DictReader(f_in)
        
        # Header cho file kết quả
        fieldnames = [
            "test_id", "visit_id", "patient_id", 
            "test_code", "test_name", "test_result", "test_unit", "reference_range",
            "abnormal_flag", # Cờ báo bất thường (Normal/High/Low/Abnormal)
            "test_date", 
            "height", "weight", "bmi", "blood_type", "comorbidities_snapshot"
        ]
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        
        test_id_counter = 1
        
        for row in reader:
            visit_id = row["visit_id"]
            pid = row["patient_id"]
            dept = row["department"]
            reason = row["visit_reason"].lower()
            visit_date_str = row["visit_date"]
            
            p_info = patients_db.get(pid)
            if not p_info: continue # Bỏ qua nếu ko khớp ID
            
            # --- XÂY DỰNG CONTEXT (BỐI CẢNH) ---
            # Kết hợp cờ bệnh nền cũ + Lý do khám hiện tại
            context_flags = p_info["flags"].copy()
            
            # Phân tích lý do khám để thêm cờ
            if "đường" in reason or "tiểu đường" in reason: context_flags.add("DIABETES")
            if "sốt" in reason or "viêm" in reason or "ho" in reason: context_flags.add("INFECTION")
            if "ngực" in reason or "tim" in reason: context_flags.add("LIPID")
            if "khớp" in reason or "gout" in reason: context_flags.add("GOUT")
            
            # --- QUYẾT ĐỊNH DANH SÁCH TEST ---
            tests_to_run = []
            
            # 1. Lấy test theo Khoa
            dept_tests = DEPT_TEST_RULES.get(dept, ["WBC", "GLUCOSE"]) # Mặc định
            tests_to_run.extend(dept_tests)
            
            # 2. Thêm test theo Lý do cụ thể (Bổ sung)
            if "sốt" in reason: tests_to_run.append("CRP")
            if "ngực" in reason: tests_to_run.append("ECG")
            if "bụng" in reason: tests_to_run.append("ULTRASOUND_ABD")
            
            # Khử trùng lặp
            tests_to_run = list(set(tests_to_run))
            
            # --- SINH DỮ LIỆU SINH TRẮC (VITALS) CHO LẦN KHÁM NÀY ---
            # Cân nặng dao động nhẹ +/- 2kg so với base
            current_weight = p_info["base_weight"] + random.uniform(-1.5, 1.5)
            current_bmi = calculate_bmi(p_info["height"], current_weight)
            
            # Parse ngày khám
            visit_dt = parse_date(visit_date_str)
            if not visit_dt: visit_dt = datetime.now()
            
            # Sinh từng test
            for t_key in tests_to_run:
                if t_key not in TEST_CATALOG: continue
                
                t_cfg = TEST_CATALOG[t_key]
                t_name = t_cfg["name"]
                t_type = t_cfg["type"]
                
                # Thời gian làm test: Sau giờ khám 15p - 2 tiếng
                test_dt = visit_dt + timedelta(minutes=random.randint(15, 120))
                
                result_val = ""
                unit = ""
                ref_range = ""
                abn_flag = "Normal"
                
                if t_type == "numeric":
                    val_num, is_abn = generate_numeric_value(t_key, context_flags)
                    result_val = str(val_num)
                    unit = t_cfg["unit"]
                    ref_range = f"{t_cfg['ref_min']} - {t_cfg['ref_max']}"
                    
                    if is_abn:
                        if val_num > t_cfg["ref_max"]: abn_flag = "High"
                        elif val_num < t_cfg["ref_min"]: abn_flag = "Low"
                        
                elif t_type == "text":
                    res_text, status = generate_text_result(t_key, context_flags)
                    result_val = res_text
                    abn_flag = "Abnormal" if status == "Bất thường" else "Normal"
                
                # Ghi vào CSV
                writer.writerow({
                    "test_id": test_id_counter,
                    "visit_id": visit_id,
                    "patient_id": pid,
                    "test_code": t_key,
                    "test_name": t_name,
                    "test_result": result_val,
                    "test_unit": unit,
                    "reference_range": ref_range,
                    "abnormal_flag": abn_flag,
                    "test_date": test_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "height": p_info["height"],
                    "weight": round(current_weight, 1),
                    "bmi": current_bmi,
                    "blood_type": p_info["blood_type"],
                    "comorbidities_snapshot": ", ".join(context_flags) if context_flags else "None"
                })
                
                test_id_counter += 1
                
        print(f"Xong! Đã tạo {test_id_counter} bản ghi xét nghiệm tại {OUTPUT_HEALTH_CSV}")

if __name__ == "__main__":
    main()