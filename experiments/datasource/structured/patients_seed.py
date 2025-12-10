import csv
import random

# ================== CẤU HÌNH ==================
NUM_RECORDS = 100000
OUTPUT_CSV = "patients_seed.csv"
RANDOM_SEED = 42

random.seed(RANDOM_SEED)

# ================== CHỈ SỬ DỤNG MÃ HÀ NỘI ==================
PROVINCE_CODES = ["001"] 

# ================== HÀM SINH DỮ LIỆU ==================

def generate_cccd(existing_set: set) -> str:
    """
    Sinh CCCD 12 số chuẩn quy tắc: 001 G YY NNNNNN
    - 001: Mã Hà Nội (Cố định)
    - G: Mã giới tính & thế kỷ
      + Thế kỷ 20 (sinh 1900-1999): Nam 0, Nữ 1
      + Thế kỷ 21 (sinh 2000-2099): Nam 2, Nữ 3
    - YY: 2 số cuối năm sinh
    - NNNNNN: 6 số ngẫu nhiên
    """
    while True:
        # 1. Random năm sinh (giả lập từ 1950 đến 2023)
        birth_year = random.randint(1950, 2024)
        
        # 2. Random giới tính (0: Nam, 1: Nữ)
        gender_input = random.choice([0, 1])

        # 3. Tính mã G (Giới tính + Thế kỷ)
        if 1900 <= birth_year <= 1999:
            g_code = 0 if gender_input == 0 else 1
        else: # 2000 trở đi
            g_code = 2 if gender_input == 0 else 3
        
        # 4. Lắp ráp
        province_code = PROVINCE_CODES[0] # Luôn là 001
        year_suffix = f"{birth_year % 100:02d}"
        random_part = f"{random.randint(0, 999999):06d}"
        
        cccd = f"{province_code}{g_code}{year_suffix}{random_part}"
        
        if cccd not in existing_set:
            existing_set.add(cccd)
            return cccd

def generate_bhyt(existing_set: set) -> str:
    """
    Sinh mã số BHXH (BHYT) 10 chữ số.
    """
    while True:
        bhyt = f"{random.randint(0, 9999999999):010d}"
        if bhyt not in existing_set:
            existing_set.add(bhyt)
            return bhyt

# ================== MAIN PROCESS ==================

def main():
    print(f"Đang sinh {NUM_RECORDS} bản ghi...")
    
    used_cccds = set()
    used_bhyts = set()
    
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["patient_id", "health_insurance_id"])
        
        for i in range(NUM_RECORDS):
            cccd = generate_cccd(used_cccds)
            bhyt = generate_bhyt(used_bhyts)
            
            writer.writerow([cccd, bhyt])
            
            if (i + 1) % 10000 == 0:
                print(f"-> Đã sinh: {i + 1}/{NUM_RECORDS}")

    print(f"HOÀN TẤT! File dữ liệu: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()