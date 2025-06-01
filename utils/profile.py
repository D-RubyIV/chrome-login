import random
import string
from datetime import datetime


def generate_random_code_with_date(date=None):
    # Nếu không truyền ngày vào thì dùng ngày hiện tại
    if date is None:
        date = datetime.now()

    # Định dạng ngày thành chuỗi ddmmyyyy
    date_str = date.strftime('%d%m%Y')

    # Tạo chuỗi ngẫu nhiên gồm 10 ký tự chữ và số
    random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

    # Trả về chuỗi theo định dạng mong muốn
    return f"{random_part.lower()}-{date_str}"


