import argparse
import time
import csv
import os
import sys
import urllib.parse  
from datetime import datetime, timedelta

# Import thư viện load env
from dotenv import load_dotenv 

import pymongo
from pymongo import MongoClient
import certifi

# Import logic sinh dữ liệu
from behavior_logs_gen import DailyBehaviorSimulator, apply_noise, SCHEMA_DESCRIPTION

# ========================================
# CẤU HÌNH MÔI TRƯỜNG
# ========================================
# 1. Load file .env
load_dotenv()

# 2. Lấy thông tin từ biến môi trường
M_USER = os.getenv("MONGO_USER")
M_PASS = os.getenv("MONGO_PASSWORD")
M_CLUSTER = os.getenv("MONGO_CLUSTER")
M_DB_NAME = os.getenv("MONGO_DB_NAME", "medical_lake") # Mặc định là medical_lake nếu không có trong env

# 3. Tạo URI kết nối an toàn (Xử lý ký tự đặc biệt trong pass)
if not M_USER or not M_PASS or not M_CLUSTER:
    print("❌ LỖI: Thiếu thông tin cấu hình trong file .env")
    print("👉 Hãy tạo file .env chứa: MONGO_USER, MONGO_PASSWORD, MONGO_CLUSTER")
    sys.exit(1)

# Mã hóa username và password để tránh lỗi URL
safe_user = urllib.parse.quote_plus(M_USER)
safe_pass = urllib.parse.quote_plus(M_PASS)

# Tạo connection string chuẩn
DEFAULT_MONGO_URI = f"mongodb+srv://{safe_user}:{safe_pass}@{M_CLUSTER}/?appName=cluster0"

COLLECTION_NAME = "daily_behavior_logs"
META_COLLECTION = "_schema_metadata"

# ========================================
# HÀM KẾT NỐI VÀ GỬI
# ========================================
def get_mongo_collection(uri, db_name, col_name):
    print(f"🔌 Đang kết nối tới Cluster: {M_CLUSTER}...")
    
    # Sử dụng certifi.where() để lấy đường dẫn chứng chỉ SSL chuẩn
    client = MongoClient(uri, tlsCAFile=certifi.where())
    
    # Kiểm tra kết nối thử
    try:
        client.admin.command('ping')
        print("✅ Kết nối & Xác thực MongoDB thành công!")
    except Exception as e:
        print(f"❌ Kết nối MongoDB thất bại: {e}")
        print("👉 Gợi ý: Kiểm tra lại Username/Password trong file .env hoặc IP Whitelist.")
        sys.exit(1)
        
    db = client[db_name]
    return db[col_name], db[META_COLLECTION]

def load_patient_ids_from_csv(file_path):
    pids = []
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ Không tìm thấy file: {file_path}")
    
    with open(file_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        if 'patient_id' not in reader.fieldnames:
            raise ValueError(f"❌ File CSV phải có cột 'patient_id'.")
        for row in reader:
            if row['patient_id'].strip():
                pids.append(row['patient_id'].strip())
    return list(set(pids))

# ========================================
# LOGIC CHẠY BATCH (Ngày)
# ========================================
def process_day_batch(collection, simulator, patient_ids, current_date, dirty_rate, delay=None):
    """
    Sinh và gửi dữ liệu của TẤT CẢ bệnh nhân trong 1 ngày cụ thể.
    """
    batch_data = []
    print(f"⏳ Đang sinh dữ liệu cho ngày: {current_date.date()}...")
    
    for pid in patient_ids:
        # 1. Sinh dữ liệu thô
        record = simulator.generate_record(pid, current_date)
        
        # 2. Tạo nhiễu (nếu có)
        final_record = apply_noise(record, dirty_rate)
        
        batch_data.append(final_record)
        
        # (Optional) Realtime delay giả lập từng người gửi
        if delay:
            time.sleep(delay)

    # 3. Gửi Bulk Insert vào MongoDB (Hiệu năng cao hơn insert từng dòng)
    if batch_data:
        try:
            result = collection.insert_many(batch_data)
            print(f"✅ [MongoDB] Đã insert {len(result.inserted_ids)} bản ghi ngày {current_date.date()}.")
            return len(result.inserted_ids)
        except Exception as e:
            print(f"❌ Lỗi insert MongoDB: {e}")
            return 0
    return 0

# ========================================
# MAIN MODES
# ========================================
def run_history_mode(collection, simulator, patient_ids, start_date, end_date, dirty_rate):
    total = 0
    current = start_date
    while current <= end_date:
        total += process_day_batch(collection, simulator, patient_ids, current, dirty_rate, delay=None)
        current += timedelta(days=1)
    print(f"\n🎉 [HISTORY DONE] Tổng cộng đã gửi {total} bản ghi.")

def run_realtime_mode(collection, simulator, patient_ids, target_date, dirty_rate, delay):
    print(f"\n📡 [REALTIME] Bắt đầu đẩy dữ liệu ngày {target_date.date()} từng người một...")
    count = 0
    for pid in patient_ids:
        record = simulator.generate_record(pid, target_date)
        final_record = apply_noise(record, dirty_rate)
        
        try:
            collection.insert_one(final_record)
            print(f"   -> Sent log for Patient: {pid}")
            count += 1
        except Exception as e:
            print(f"❌ Error: {e}")
        
        if delay:
            time.sleep(delay)
            
    print(f"\n🎉 [REALTIME DONE] Đã gửi {count} bản ghi.")

# ========================================
# CLI ARGUMENTS
# ========================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Behavior Log MongoDB Generator")
    parser.add_argument("--patient_file", type=str, required=True, help="Path file CSV patient_id")
    parser.add_argument("--mode", choices=["history", "realtime"], required=True)
    parser.add_argument("--start", type=str, help="YYYY-MM-DD (History mode)")
    parser.add_argument("--end", type=str, help="YYYY-MM-DD (History mode)")
    parser.add_argument("--date", type=str, help="YYYY-MM-DD (Realtime mode)")
    parser.add_argument("--delay", type=float, default=0.1, help="Delay giữa các records (giây)")
    parser.add_argument("--dirty_rate", type=float, default=0.0)
    
    # Cho phép override URI từ command line, nếu không có thì dùng từ .env
    parser.add_argument("--uri", type=str, default=DEFAULT_MONGO_URI, help="MongoDB connection URI (optional)")
    parser.add_argument("--db", type=str, default=M_DB_NAME)
    parser.add_argument("--collection", type=str, default=COLLECTION_NAME)

    args = parser.parse_args()
    
    # 1. Kết nối Mongo
    data_col, meta_col = get_mongo_collection(args.uri, args.db, args.collection)
    
    # 2. Gửi Metadata
    print("ℹ️  Đang cập nhật Schema Metadata vào MongoDB...")
    try:
        meta_col.replace_one(
            {"collection_name": args.collection}, 
            SCHEMA_DESCRIPTION, 
            upsert=True
        )
    except Exception as e:
        print(f"⚠️ Không thể update metadata (có thể do lỗi mạng hoặc quyền), bỏ qua. Chi tiết: {e}")

    # 3. Load Patients & Simulator
    try:
        pids = load_patient_ids_from_csv(args.patient_file)
        print(f"👥 Tìm thấy {len(pids)} bệnh nhân.")
    except Exception as e:
        print(e)
        exit(1)

    simulator = DailyBehaviorSimulator()

    # 4. Run Modes
    if args.mode == "history":
        if not args.start or not args.end:
            print("❌ Mode history cần --start và --end")
            exit(1)
        s_date = datetime.strptime(args.start, "%Y-%m-%d")
        e_date = datetime.strptime(args.end, "%Y-%m-%d")
        run_history_mode(data_col, simulator, pids, s_date, e_date, args.dirty_rate)

    elif args.mode == "realtime":
        target = datetime.strptime(args.date, "%Y-%m-%d") if args.date else datetime.now()
        run_realtime_mode(data_col, simulator, pids, target, args.dirty_rate, args.delay)