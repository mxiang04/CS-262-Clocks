import datetime
import logging
import os


def setup_logger(logger_name, log_file, level=logging.INFO):
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    log_format = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
    file_handler = logging.FileHandler(log_file, mode="w")
    file_handler.setFormatter(log_format)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def make_folder(id):
    sub_folder = "logs/" + datetime.datetime.now().strftime("%m_%d_%y")
    if not os.path.exists(sub_folder):
        os.makedirs(sub_folder)

    return (
        "logs/"
        + datetime.datetime.now().strftime("%m_%d_%y")
        + "/machine"
        + str(id)
        + ".log"
    )
