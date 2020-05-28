import logging

def setup_custom_logger(name, log_file, formatter, level=logging.INFO):
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

simple_formatter = logging.Formatter("%(message)s")

perf_logger = setup_custom_logger("PerfLogger", "performance.log", simple_formatter)