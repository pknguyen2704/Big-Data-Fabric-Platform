# gen_data.py
import uuid
from datetime import datetime, timedelta, time
from typing import List, Dict, Any
import random

# ========================================
# 1. Mapping Device ↔ Patient (Dựa trên List ID có sẵn)
# ========================================
def create_device_patient_mapping(patient_ids: List[str]) -> List[Dict[str, Any]]:
    """
    Tạo mapping: Mỗi patient_id trong list sẽ được gán một device_id số nguyên.
    """
    mapping = []
    for idx, pid in enumerate(patient_ids):
        mapping.append({
            "device_id": idx + 1,  # Device ID tự tăng: 1, 2, 3...
            "patient_id": pid      # Patient ID từ file CSV
        })
    return mapping

# ========================================
# 2. Smart Band Simulator
# ========================================
class SmartBandSimulator:
    def __init__(self, devices: List[Dict[str, Any]]):
        self.state = {}
        for d in devices:
            dev_id = d["device_id"]
            self.state[dev_id] = {
                "device_id": dev_id,
                "patient_id": d["patient_id"], 
                "step_rate_per_min": 1 + (dev_id % 3),
                "resting_hr": 55 + (dev_id % 20),
                "spo2_base": min(94 + (dev_id % 6), 100),
                "last_day": None,
                # Daily counters
                "daily_steps": 0,
                "daily_calories": 0.0,
                "daily_standing_hours": 0.0,
                "daily_run_distance": 0.0,
                # Sleep
                "sleep_start": None,
                "total_sleep_hours": 0.0,
                "total_deep_sleep_hours": 0.0,
                # Total calories lũy tiến
                "total_calories": 0.0,
                "last_ts": None
            }

    @staticmethod
    def is_sleeping(ts: datetime) -> bool:
        return ts.hour >= 21 or ts.hour < 6

    def generate_smart_band_record(self, dev_id: int, ts: datetime) -> Dict[str, Any]:
        s = self.state[dev_id]
        today = ts.date()
        sleeping = self.is_sleeping(ts)

        # Reset counters nếu qua ngày mới
        if s["last_day"] != today:
            s["last_day"] = today
            s["daily_steps"] = 0
            s["daily_calories"] = 0.0
            s["daily_standing_hours"] = 0.0
            s["daily_run_distance"] = 0.0
            if not sleeping:
                s["sleep_start"] = None

        # Tính delta time
        last_ts = s.get("last_ts") or ts
        delta_min = max(0, (ts - last_ts).total_seconds() / 60)

        if sleeping:
            if s["sleep_start"] is None:
                if ts.hour >= 21:
                    s["sleep_start"] = datetime.combine(today, time(21, 0))
                else:
                    s["sleep_start"] = datetime.combine(today - timedelta(days=1), time(21, 0))
            
            sleep_hours = round((ts - s["sleep_start"]).total_seconds() / 3600, 2)
            deep_sleep_hours = round(sleep_hours * random.uniform(0.5, 0.65), 2)
            calories_inc = delta_min * 0.7
            s["total_calories"] += calories_inc
            
            daily_steps_inc = 0
            standing_hours_inc = 0
            run_distance_inc = 0.0
            
            heart_rate = s["resting_hr"] - random.randint(5, 12)
            spo2 = max(90, min(100, s["spo2_base"] - random.randint(0, 1)))
            stress_level = 1
        else:
            sleep_hours = 0.0
            deep_sleep_hours = 0.0
            s["sleep_start"] = None

            hour = ts.hour
            factor = 1.8 if (7 <= hour <= 9 or 17 <= hour <= 19) else (1.0 if 9 < hour < 17 else (0.8 if 19 < hour < 21 else 0.1))
            
            daily_steps_inc = int(delta_min * s["step_rate_per_min"] * factor)
            standing_hours_inc = delta_min / 60.0
            run_distance_inc = round(daily_steps_inc * 0.00075, 3)
            calories_inc = round(daily_steps_inc * 0.04, 2)

            s["daily_steps"] += daily_steps_inc
            s["daily_standing_hours"] += standing_hours_inc
            s["daily_run_distance"] += run_distance_inc
            s["total_calories"] += calories_inc

            avg_steps = daily_steps_inc / delta_min if delta_min > 0 else 0
            activity_hr = int(avg_steps * 1.5)
            diurnal = 6 if 7 <= hour <= 9 else (5 if 17 <= hour <= 19 else (-5 if 0 <= hour <= 5 else 0))
            heart_rate = max(40, min(200, s["resting_hr"] + activity_hr + diurnal))
            spo2 = max(85, min(100, s["spo2_base"] - (2 if avg_steps > 30 else 1 if avg_steps > 10 else 0)))
            stress_level = 3 if 9 <= hour <= 12 else 2

        s["total_sleep_hours"] = sleep_hours
        s["total_deep_sleep_hours"] = deep_sleep_hours
        s["last_ts"] = ts

        # --- TRẢ VỀ KẾT QUẢ VỚI SCHEMA MỚI ---
        return {
            "transmission_id": str(uuid.uuid4()), # ID của lần gửi (UUID)
            "device_id": s["device_id"],          # Mã thiết bị (Int)
            "patient_id": s["patient_id"],        # Patient ID (String từ CSV)
            "created_at": ts.isoformat(),
            "daily_steps": s["daily_steps"],
            "SpO2": spo2,
            "sleep_hours": sleep_hours,
            "deep_sleep_hours": deep_sleep_hours,
            "calories_burned": round(s["total_calories"], 2),
            "standing_hours": round(s["daily_standing_hours"], 2),
            "run_distance": round(s["daily_run_distance"], 3),
            "stress_level": stress_level,
            "heart_rate": heart_rate
        }

    def generate_smart_band_data(self, ts: datetime) -> List[Dict[str, Any]]:
        return [self.generate_smart_band_record(dev_id, ts) for dev_id in sorted(self.state.keys())]

# ========================================
# 3. Apply noise (Giữ nguyên)
# ========================================
def apply_noise(record: Dict[str, Any], dirty_rate: float = 0.0, excluded_fields=None) -> Dict[str, Any]:
    if excluded_fields is None:
        excluded_fields = []
    if dirty_rate <= 0.0:
        return record
    dirty_record = record.copy()
    for field in list(dirty_record.keys()):
        if field in excluded_fields or field in ["created_at", "transmission_id", "patient_id", "device_id"]:
            continue
        if random.random() <= dirty_rate:
            dirty_record[field] = None
    return dirty_record