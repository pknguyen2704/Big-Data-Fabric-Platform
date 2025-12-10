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
from pymongo.errors import CollectionInvalid
import certifi

# Import logic sinh dữ liệu
from behavior_logs_gen import DailyBehaviorSimulator, apply_noise

# ========================================
# 1. Định nghĩa MongoDB JSON Schema (Validator)
# ========================================
# Đây là phần dịch từ SCHEMA_DESCRIPTION sang ngôn ngữ mà MongoDB hiểu ($jsonSchema)
VALIDATOR_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["patient_ID", "date"], # Các trường bắt buộc phải có
        "title": "Daily Behavior Logs",
        "description": "Dữ liệu nhật ký sức khỏe tổng hợp theo ngày của bệnh nhân.",
        "properties": {
            "_id": {
                "bsonType": "objectId",
                "description": "Định danh duy nhất của bản ghi."
            },
            "patient_ID": {
                "bsonType": "string",
                "description": "Mã định danh bệnh nhân."
            },
            "date": {
                "bsonType": "date",
                "description": "Ngày ghi nhận nhật ký (YYYY-MM-DD)."
            },
            "diet": {
                "bsonType": "object",
                "description": "Thông tin dinh dưỡng trong ngày.",
                "properties": {
                    "Breakfast": {"bsonType": "string"},
                    "Lunch": {"bsonType": "string"},
                    "Dinner": {"bsonType": "string"},
                    "Snack": {"bsonType": "string"},
                    "Total_calories": {"bsonType": "int", "minimum": 0}
                }
            },
            "exercise": {
                "bsonType": "object",
                "description": "Thông tin vận động/tập luyện.",
                "properties": {
                    "Type": {"bsonType": "string"},
                    "Duration_hours": {"bsonType": "double"}, # Python float -> Mongo double
                    "Intensity": {"bsonType": "string"},
                    "Calories_burned": {"bsonType": "double"}
                }
            },
            "mood": {
                "bsonType": ["string", "null"], # Cho phép string hoặc null (nếu tạo nhiễu)
                "description": "Tâm trạng chủ đạo trong ngày."
            },
            "water_intake_ml": {
                "bsonType": ["int", "null"],
                "description": "Lượng nước uống (ml)."
            },
            "context": {
                "bsonType": "object",
                "description": "Bối cảnh môi trường.",
                "properties": {
                    "Weather": {"bsonType": "string"},
                    "Location": {"bsonType": "string"},
                    "Special_events": {"bsonType": "string"}
                }
            }
        }
    }
}

# ========================================
# CẤU HÌNH MÔI TRƯỜNG
# ========================================
load_dotenv()
M_USER = os.getenv("MONGO_USER")
M_PASS = os.getenv("MONGO_PASSWORD")
M_CLUSTER = os.getenv("MONGO_CLUSTER")
M_DB_NAME = os.getenv("MONGO_DB_NAME", "medical_lake")

if not M_USER or not M_PASS or not M_CLUSTER:
    print("❌ LỖI: Thiếu thông tin cấu hình trong file .env")
    sys.exit(1)

safe_user = urllib.parse.quote_plus(M_USER)
safe_pass = urllib.parse.quote_plus(M_PASS)
DEFAULT_MONGO_URI = f"mongodb+srv://{safe_user}:{safe_pass}@{M_CLUSTER}/?appName=cluster0"

COLLECTION_NAME = "daily_behavior_logs"

# ========================================
# HÀM KẾT NỐI & CẤU HÌNH SCHEMA
# ========================================
def setup_database_and_schema(uri, db_name, col_name):
    print(f"🔌 Đang kết nối tới Cluster: {M_CLUSTER}...")
    client = MongoClient(uri, tlsCAFile=certifi.where())
    
    try:
        client.admin.command('ping')
        print("✅ Kết nối MongoDB thành công!")
    except Exception as e:
        print(f"❌ Kết nối thất bại: {e}")
        sys.exit(1)
        
    db = client[db_name]
    
    # --- CẬP NHẬT SCHEMA VALIDATOR ---
    print(f"⚙️  Đang cấu hình Schema Validator cho '{col_name}'...")
    
    # Kiểm tra xem collection đã tồn tại chưa
    col_names = db.list_collection_names()
    
    if col_name not in col_names:
        # 1. Nếu chưa có, tạo mới kèm validator
        try:
            db.create_collection(col_name, validator=VALIDATOR_SCHEMA)
            print("✅ Đã tạo collection mới với Schema Validation.")
        except Exception as e:
            print(f"⚠️ Lỗi tạo collection: {e}")
    else:
        # 2. Nếu đã có, dùng lệnh 'collMod' để cập nhật validator
        try:
            command = {
                "collMod": col_name,
                "validator": VALIDATOR_SCHEMA,
                "validationLevel": "moderate" # Cảnh báo nếu sai schema nhưng vẫn cho ghi (hoặc 'strict' để chặn)
            }
            db.command(command)
            print("✅ Đã cập nhật Schema Validation vào collection hiện tại.")
        except Exception as e:
            print(f"⚠️ Không thể cập nhật Schema (có thể do quyền user): {e}")

    return db[col_name]

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
    batch_data = []
    print(f"⏳ Đang sinh dữ liệu cho ngày: {current_date.date()}...")
    
    for pid in patient_ids:
        record = simulator.generate_record(pid, current_date)
        final_record = apply_noise(record, dirty_rate)
        batch_data.append(final_record)
        if delay: time.sleep(delay)

    if batch_data:
        try:
            # ordered=False để nếu 1 record lỗi (sai schema) thì các record khác vẫn chạy
            result = collection.insert_many(batch_data, ordered=False)
            print(f"✅ [MongoDB] Insert thành công {len(result.inserted_ids)} bản ghi.")
            return len(result.inserted_ids)
        except pymongo.errors.BulkWriteError as bwe:
            # Bắt lỗi nếu dữ liệu vi phạm schema (nếu validationLevel là strict)
            print(f"⚠️ Một số bản ghi bị từ chối do lỗi Schema hoặc trùng lặp: {bwe.details['nInserted']} đã insert.")
            return bwe.details['nInserted']
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
            print(f"❌ Error (Có thể do sai Schema): {e}")
        
        if delay: time.sleep(delay)
            
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
    parser.add_argument("--delay", type=float, default=0.1, help="Delay (s)")
    parser.add_argument("--dirty_rate", type=float, default=0.0)
    
    parser.add_argument("--uri", type=str, default=DEFAULT_MONGO_URI)
    parser.add_argument("--db", type=str, default=M_DB_NAME)
    parser.add_argument("--collection", type=str, default=COLLECTION_NAME)

    args = parser.parse_args()
    
    # 1. Kết nối & Cài đặt Schema
    data_col = setup_database_and_schema(args.uri, args.db, args.collection)
    
    # 2. Load Patients & Simulator
    try:
        pids = load_patient_ids_from_csv(args.patient_file)
        print(f"👥 Tìm thấy {len(pids)} bệnh nhân.")
    except Exception as e:
        print(e)
        exit(1)

    simulator = DailyBehaviorSimulator()

    # 3. Run Modes
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