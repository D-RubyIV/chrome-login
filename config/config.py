
import os

from PySide6.QtCore import QSemaphore
from pydantic_settings import BaseSettings
from logger.logger import my_logger


class DebuggableSemaphore(QSemaphore):
    def acquire(self, *args, **kwargs):
        my_logger.warning(f"[Semaphore] Chuẩn bị acquire, còn {self.available()} slot trống")
        result = super().acquire(*args, **kwargs)
        my_logger.warning(f"[Semaphore] Hoàn tất acquire, còn {self.available()} slot trống")
        return result

    def release(self, *args, **kwargs):
        result = super().release(*args, **kwargs)
        my_logger.warning(f"[Semaphore] Đã release, còn {self.available()} slot trống")
        return result

class Settings(BaseSettings):
    SERVER: str = "http://localhost:8080"
    DBPATH: str = "database.db"

    class Config:
        env_file = ".env"

DEBUG_MODIFY = True
MAX_THREADS = int(max(4, os.cpu_count()))

class Setup:
    def __init__(self):
        self.semaphore = DebuggableSemaphore(MAX_THREADS)

setup = Setup()
settings = Settings()