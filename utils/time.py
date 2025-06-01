import time
from datetime import datetime, timedelta, timezone

from dateutil import parser

def time_stamp_convert(timestamp_ms: int):
    converted_time = datetime.fromtimestamp(timestamp_ms / 1000)
    formatted_time = converted_time.strftime("%d-%m-%Y %H:%M:%S")
    return formatted_time

def time_relative(time_str: str):
    # Chuyển đổi chuỗi thời gian thành datetime (tự động nhận diện múi giờ)
    time_obj = parser.parse(time_str).replace(tzinfo=None)  # Loại bỏ múi giờ

    now = datetime.now().replace(microsecond=0)
    diff = now - time_obj

    # Xác định là "trước" hay "sau"
    is_past = diff.total_seconds() >= 0
    diff = abs(diff)  # Lấy giá trị tuyệt đối để xử lý thời gian

    # Lấy số ngày từ timedelta
    days = diff.days

    # Kiểm tra khoảng thời gian và trả về thông báo tương ứng
    if diff < timedelta(seconds=60):
        result = f"{diff.seconds} s"
    elif diff < timedelta(minutes=60):
        result = f"{diff.seconds // 60} m"
    elif diff < timedelta(hours=24):
        result = f"{diff.seconds // 3600} h"
    elif days < 7:
        result = f"{days} d"
    elif days < 30:
        result = f"{days // 7} w"
    elif days < 365:
        result = f"{days // 30} M"
    else:
        result = f"{days // 365} y"

    return f"{result} {'trước' if is_past else 'sau'}"

def timestamp_ago(timestamp):
    now = int(time.time())  # Current time in seconds
    diff = now - timestamp  # Difference between now and the timestamp

    if diff < 60:
        return f"{diff} giây trước"
    elif diff < 3600:
        minutes = diff // 60
        return f"{minutes} phút trước"
    elif diff < 86400:
        hours = diff // 3600
        return f"{hours} giờ trước"
    elif diff < 2592000:
        days = diff // 86400
        return f"{days} ngày trước"
    elif diff < 31536000:
        months = diff // 2592000
        return f"{months} tháng trước"
    else:
        years = diff // 31536000
        return f"{years} năm trước"