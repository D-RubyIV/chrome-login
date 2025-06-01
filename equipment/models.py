import uuid
from datetime import datetime

import pytz
from sqlalchemy import Column
from sqlalchemy import String, Integer, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
Base = declarative_base()

vietnam_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
current_time_in_vietnam = datetime.now().replace(microsecond=0)

class BaseModel(DeclarativeBase):
    __abstract__ = True
    alias = "N/a"
    id: Mapped[str] = mapped_column(
        String(36),  # UUID lưu dưới dạng chuỗi
        primary_key=True,
        default=lambda: str(uuid.uuid4()),  # Tạo UUID tự động
    )
    created_time: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        default=current_time_in_vietnam,
    )
    updated_time: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        default=current_time_in_vietnam,
        onupdate=current_time_in_vietnam,
    )


class ProfileRecord(BaseModel):
    __abstract__ = False
    __tablename__ = 'accounts'

    name = Column(String(50))
    profile_path = Column(String(50))
    browser_version = Column(String(50))
    raw_proxy = Column(String(100))
    raw_note = Column(String(50))
    is_selected = Column(Boolean, default=False)

    def __str__(self):
        return f"Name: {self.name}|Profile path: {self.profile_path}|Version: {self.browser_version}"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "profile_path": self.profile_path,
            "browser_version": self.browser_version,
            "raw_proxy": self.raw_proxy,
            "raw_note": self.raw_note,
            "is_selected": self.is_selected,
            "created_time": self.created_time if self.created_time else None,
            "updated_time": self.updated_time if self.updated_time else None,
        }
