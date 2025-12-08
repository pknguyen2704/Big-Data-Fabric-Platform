import argparse
import random
import time
import json
import csv  # Thêm thư viện đọc CSV
import os
import numpy as np
from datetime import datetime, timedelta
from confluent_kafka.avro import AvroProducer, loads

# Import từ file gen_data mới
from smart_band_gen import (
    create_device_patient_mapping,
    SmartBandSimulator,
    apply_noise
)

KAFKA_TOPIC = "smart_band"
KAFKA_SERVER = "localhost:9092"
SCHEMA_REGISTRY_URL = "http://localhost:8081"

# ========================================
# Avro schema (CẬP NHẬT MỚI)
# ========================================
SMART_BAND_SCHEMA = {
    "namespace": "com.example.smart_band",
    "type": "record",
    "name": "SmartBandData",
    "fields": [
        {"name": "transmission_id", "type": "string"},           # ID gói tin
        {"name": "device_id", "type": ["null", "int"], "default": None},
        {"name": "patient_id", "type": ["null", "string"], "default": None}, # Đổi sang string
        {"name": "created_at", "type": ["null", "long"], "default": None},
        {"name": "daily_steps", "type": ["null", "int"], "default": None},
        {"name": "SpO2", "type": ["null", "int"], "default": None},
        {"name": "sleep_hours", "type": ["null", "double"], "default": None},
        {"name": "deep_sleep_hours", "type": ["null", "double"], "default": None},
        {"name": "calories_burned", "type": ["null", "double"], "default": None},
        {"name": "standing_hours", "type": ["null", "double"], "default": None},
        {"name": "run_distance", "type": ["null", "double"], "default": None},
        {"name": "stress_level", "type": ["null", "int"], "default": None},
        {"name": "heart_rate", "type": ["null", "int"], "default": None}
    ]
}

value_schema = loads(json.dumps(SMART_BAND_SCHEMA))

producer_config = {
    'bootstrap.servers': KAFKA_SERVER,
    'schema.registry.url': SCHEMA_REGISTRY_URL
}

producer = AvroProducer(producer_config, default_value_schema=value_schema)

# ========================================
# HÀM ĐỌC CSV
# ========================================
def load_patient_ids_from_csv(file_path):
    pids = []
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ Không tìm thấy file: {file_path}")
    
    with open(file_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        # Kiểm tra xem header có cột patient_id không
        if 'patient_id' not in reader.fieldnames:
            raise ValueError(f"❌ File CSV phải có cột 'patient_id'. Các cột hiện tại: {reader.fieldnames}")
            
        for row in reader:
            if row['patient_id'].strip():
                pids.append(row['patient_id'].strip())
    
    # Loại bỏ duplicate nếu cần
    return list(set(pids))

# ========================================
# SEND BATCH (GIỮ NGUYÊN LOGIC, CHỈ SỬA PRINT)
# ========================================
def send_batch(simulator, timestamp, dirty_rate, excluded_fields, delay=None):
    batch = simulator.generate_smart_band_data(timestamp)
    count = 0

    for rec in batch:
        # created_at từ ISO → epoch millis
        if isinstance(rec.get("created_at"), str):
            dt = datetime.fromisoformat(rec["created_at"])
            rec["created_at"] = int(dt.timestamp() * 1000)

        # numpy → python native
        for k, v in rec.items():
            if isinstance(v, np.generic):
                rec[k] = v.item()

        dirty_rec = apply_noise(rec, dirty_rate=dirty_rate, excluded_fields=excluded_fields)

        try:
            producer.produce(topic=KAFKA_TOPIC, value=dirty_rec)
            # Chỉ in 1 mẫu để đỡ rối mắt
            if count == 0: 
                print(f"[{timestamp}] Sent sample: TransID={dirty_rec['transmission_id']} | PID={dirty_rec['patient_id']}")
        except Exception as e:
            print(f"❌ Error producing: {e}")

        count += 1
        if delay:
            time.sleep(delay)

    producer.flush()
    return count

# ... (Giữ nguyên run_history_mode và run_realtime_mode) ...
def run_history_mode(simulator, start_date, end_date, interval_minutes, dirty_rate, excluded_fields):
    print(f"\n⏳ [HISTORY] Gửi dữ liệu từ {start_date.date()} đến {end_date.date()}...\n")
    timestamp = start_date
    interval = timedelta(minutes=interval_minutes)
    total = 0

    while timestamp < end_date:
        total += send_batch(simulator, timestamp, dirty_rate, excluded_fields, delay=None)
        timestamp += interval

    print(f"\n✅ Đã gửi tổng {total} bản ghi lịch sử.")

def run_realtime_mode(simulator, target_date, interval_minutes, dirty_rate, excluded_fields, delay):
    print(f"\n⏳ [REALTIME] Giả lập ngày {target_date.date()}...\n")
    start = datetime(target_date.year, target_date.month, target_date.day, 0, 0)
    end = start + timedelta(days=1)
    timestamp = start
    interval = timedelta(minutes=interval_minutes)
    total = 0

    while timestamp < end:
        total += send_batch(simulator, timestamp, dirty_rate, excluded_fields, delay)
        timestamp += interval

    print(f"\n✅ Đã gửi realtime {total} bản ghi.")

# ========================================
# CLI (CẬP NHẬT)
# ========================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Smart Band Data Sender")

    # Thay num_devices/num_users bằng file csv
    parser.add_argument("--patient_file", type=str, required=True, help="Đường dẫn đến file CSV chứa patient_id")
    
    parser.add_argument("--mode", choices=["history", "realtime"], required=True)
    parser.add_argument("--start", type=str)
    parser.add_argument("--end", type=str)
    parser.add_argument("--date", type=str)
    parser.add_argument("--delay", type=float, default=0.05) # Giảm delay mặc định
    parser.add_argument("--interval", type=int, default=5)
    parser.add_argument("--dirty_rate", type=float, default=0.0)
    parser.add_argument("--exclude", type=str, default="")

    args = parser.parse_args()

    random.seed(42)
    excluded_fields = [f.strip() for f in args.exclude.split(",") if f.strip() != ""]

    # 1. Đọc danh sách Patients
    print(f"\n📂 Đang đọc file: {args.patient_file}")
    patient_ids = load_patient_ids_from_csv(args.patient_file)
    print(f"✅ Tìm thấy {len(patient_ids)} bệnh nhân.")

    # 2. Tạo Mapping
    devices = create_device_patient_mapping(patient_ids)
    
    # 3. Khởi tạo Simulator
    simulator = SmartBandSimulator(devices)

    # 4. Chạy chế độ tương ứng
    if args.mode == "history":
        if not args.start or not args.end:
            print("❌ Mode history cần tham số --start và --end (YYYY-MM-DD)")
            exit(1)
        start_date = datetime.strptime(args.start, "%Y-%m-%d")
        end_date = datetime.strptime(args.end, "%Y-%m-%d") + timedelta(days=1)
        run_history_mode(simulator, start_date, end_date, args.interval, args.dirty_rate, excluded_fields)

    elif args.mode == "realtime":
        if not args.date:
            print("❌ Mode realtime cần tham số --date (YYYY-MM-DD)")
            exit(1)
        target_date = datetime.strptime(args.date, "%Y-%m-%d")
        run_realtime_mode(simulator, target_date, args.interval, args.dirty_rate, excluded_fields, args.delay)