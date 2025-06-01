import logging
from logging.handlers import RotatingFileHandler
import colorlog

def setup_logger():
    logger = logging.getLogger("my_logger")
    logger.setLevel(logging.DEBUG)  # Ghi từ mức DEBUG trở lên
    if not logger.hasHandlers():
        console_formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            }
        )
        # Handler cho console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)

        file_handler = RotatingFileHandler(
            "app.log",
            maxBytes=10 * 1024 * 1024,  # 5MB
            backupCount=0,  # Giữ lại tối đa 3 file cũ
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(console_formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    # Ngăn chặn log bị lặp
    logger.propagate = False
    return logger

my_logger = setup_logger()