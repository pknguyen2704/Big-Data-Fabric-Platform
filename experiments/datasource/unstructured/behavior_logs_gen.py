import random
from datetime import datetime, timedelta, time
from typing import List, Dict, Any
from bson import ObjectId

# ========================================
# 1. Định nghĩa Schema Description (Metadata)
# ========================================
SCHEMA_DESCRIPTION = {
    "collection_name": "daily_behavior_logs",
    "description": "Dữ liệu nhật ký sức khỏe tổng hợp theo ngày của bệnh nhân.",
    "fields": {
        "_id": "ObjectId: Định danh duy nhất của bản ghi trong MongoDB.",
        "patient_ID": "String: Mã định danh bệnh nhân.",
        "date": "Date: Ngày ghi nhận nhật ký (YYYY-MM-DD).",
        "diet": {
            "type": "Object",
            "description": "Thông tin dinh dưỡng trong ngày.",
            "fields": {
                "Breakfast": "String: Món ăn sáng.",
                "Lunch": "String: Món ăn trưa.",
                "Dinner": "String: Món ăn tối.",
                "Snack": "String: Các món ăn vặt.",
                "Total_calories": "Int: Tổng lượng calo nạp vào."
            }
        },
        "exercise": {
            "type": "Object",
            "description": "Thông tin vận động/tập luyện.",
            "fields": {
                "Type": "String: Loại hình vận động (Chạy bộ, Gym, Yoga...).",
                "Duration_hours": "Float: Thời gian tập luyện (giờ).",
                "Intensity": "String: Cường độ (Nhẹ, Vừa, Nặng).",
                "Calories_burned": "Float: Lượng calo tiêu thụ."
            }
        },
        "mood": "String: Tâm trạng chủ đạo trong ngày.",
        "water_intake_ml": "Int: Lượng nước uống (ml).",
        "context": {
            "type": "Object",
            "description": "Bối cảnh môi trường.",
            "fields": {
                "Weather": "String: Thời tiết.",
                "Location": "String: Địa điểm chính.",
                "Special_events": "String: Sự kiện đặc biệt (nếu có)."
            }
        }
    }
}

# ========================================
# 2. Daily Behavior Simulator
# ========================================
class DailyBehaviorSimulator:
    def __init__(self):
        # Dữ liệu mẫu để random
        self.foods = ["Phở bò", "Bánh mì", "Cơm tấm", "Salad", "Ức gà luộc", "Bún chả", "Cháo yến mạch", "Không ăn"]
        self.snacks = ["Táo", "Sữa chua", "Bánh quy", "Trà sữa", "Hạt điều", "Không có"]
        self.exercises = ["Chạy bộ", "Yoga", "Gym", "Đạp xe", "Bơi lội", "Đi bộ nhanh"]
        self.intensities = ["Nhẹ", "Vừa", "Nặng"]
        self.moods = ["Vui vẻ", "Căng thẳng", "Bình thường", "Mệt mỏi", "Hào hứng"]
        self.weathers = ["Nắng", "Mưa rào", "Nhiều mây", "Lạnh", "Ẩm ướt"]
        self.locations = ["Nhà riêng", "Văn phòng", "Công tác", "Du lịch", "Bệnh viện"]
        self.events = ["Sinh nhật", "Họp quan trọng", "Ngày nghỉ lễ", "Khám định kỳ", "Không có"]

    def generate_record(self, patient_id: str, date_val: datetime) -> Dict[str, Any]:
        """
        Sinh một bản ghi nhật ký sức khỏe cho 1 bệnh nhân vào 1 ngày cụ thể.
        """
        # --- 1. Diet ---
        bf = random.choice(self.foods)
        lun = random.choice(self.foods)
        din = random.choice(self.foods)
        snack = random.choice(self.snacks)
        total_cal = random.randint(1500, 3000)

        # --- 2. Exercise ---
        ex_type = random.choice(self.exercises)
        ex_dur = round(random.uniform(0.5, 2.0), 2)
        ex_int = random.choice(self.intensities)
        # Calo tiêu thụ ước tính dựa trên cường độ
        base_cal = 300 if ex_int == "Nhẹ" else (500 if ex_int == "Vừa" else 700)
        cal_burned = round(ex_dur * base_cal * random.uniform(0.8, 1.2), 1)
      

        # --- 4. Context & Mood ---
        mood = random.choice(self.moods)
        weather = random.choice(self.weathers)
        loc = random.choice(self.locations)
        evt = random.choice(self.events) if random.random() < 0.2 else "Không có" # 20% có sự kiện
        water = random.randint(1000, 3000)

        # --- CẤU TRÚC DOCUMENT MONGODB ---
        record = {
            # MongoDB tự tạo _id nếu không truyền, hoặc truyền ObjectId()
            "_id": ObjectId(), 
            "patient_ID": patient_id,
            "date": datetime.combine(date_val.date(), time(0,0,0)), # Lưu dạng ISODate trong Mongo
            
            "diet": {
                "Breakfast": bf,
                "Lunch": lun,
                "Dinner": din,
                "Snack": snack,
                "Total_calories": total_cal
            },
            
            "exercise": {
                "Type": ex_type,
                "Duration_hours": ex_dur,
                "Intensity": ex_int,
                "Calories_burned": cal_burned
            },
            
            "mood": mood,
            "water_intake_ml": water,
            
            "context": {
                "Weather": weather,
                "Location": loc,
                "Special_events": evt
            }
        }
        return record

# ========================================
# 3. Hàm tạo nhiễu (Giữ nguyên logic của bạn)
# ========================================
def apply_noise(record: Dict[str, Any], dirty_rate: float = 0.0) -> Dict[str, Any]:
    if dirty_rate <= 0.0:
        return record
    
    dirty_rec = record.copy()
    # Danh sách các trường có thể bị NULL (trừ _id và khóa chính)
    flat_fields = ["mood", "water_intake_ml"] 
    # (Lưu ý: Với nested object, việc gán None phức tạp hơn, ở đây demo gán None cho trường đơn giản)
    
    for field in flat_fields:
        if random.random() <= dirty_rate:
            dirty_rec[field] = None
    return dirty_rec