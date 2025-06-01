import contextvars
import functools
import threading
from contextlib import contextmanager
from typing import TypeVar

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from config.config import settings, MAX_THREADS
from sqlalchemy.pool import QueuePool

from logger.logger import my_logger

T = TypeVar('T')
R = TypeVar('R')

db_session_context = contextvars.ContextVar("db_session", default=None)

engine = create_engine(
    f"sqlite+pysqlite:///{settings.DBPATH}?check_same_thread=False",
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    poolclass=QueuePool,
    echo=False,
    pool_pre_ping=True,
    connect_args={"timeout": 15}
)

print(f"DB Path: ", settings.DBPATH)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


class SessionManager:
    def __init__(self):
        pass

    @staticmethod
    @contextmanager
    def get_session() -> Session:
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()


def db(func):
    @functools.wraps(func)
    def wrap_func(*args, **kwargs):
        db_session = db_session_context.get()
        return func(*args, **kwargs, session=db_session)

    return wrap_func


# Sử dụng Semaphore với giới hạn 2
lock_db_index = 1  # Khởi tạo biến index

db_semaphore = threading.Semaphore(MAX_THREADS)


def transactional(func):
    @functools.wraps(func)
    def wrap_func(*args, **kwargs):
        global lock_db_index  # Tham chiếu đến biến toàn cục
        # Kiểm tra truy cập vào semaphore, chỉ có 2 luồng được phép truy cập cùng lúc
        # Chỉ một số lượng luồng nhất định có thể truy cập cơ sở dữ liệu đồng thời
        # Lấy session hiện tại từ context
        existing_session = db_session_context.get()
        if existing_session:
            # Nếu đã có session, sử dụng session đó
            return func(*args, **kwargs)

        # Nếu chưa có session, tạo mới
        with SessionManager.get_session() as new_session:
            db_semaphore.acquire(timeout=3)
            # my_logger.info(f"LOCK DB INDEX {lock_db_index}")  # In ra log với index
            db_session_context.set(new_session)
            try:
                # Gọi hàm với session mới
                result = func(*args, **kwargs)
                # Commit transaction sau khi hoàn thành
                new_session.commit()
                return result
            except Exception as e:
                my_logger.error(f"Error in transactional function {func.__name__}: {e}")
                my_logger.info("===[TRANSACTIONAL ROLL BACK]===")
                new_session.rollback()
                raise
            finally:
                new_session.close()
                # Dọn dẹp context để tránh giữ session cũ
                db_session_context.set(None)
                db_semaphore.release()  # Giải phóng semaphore cho các luồng khác
                # my_logger.info(f"UNLOCK DB {lock_db_index}")

                lock_db_index += 1  # Tăng index mỗi khi một luồng kết thúc

    return wrap_func