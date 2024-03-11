import logging, os

def setup_custom_logger(name, log_file, formatter, level=logging.INFO):
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

simple_formatter = logging.Formatter("%(message)s")

perf_logger_file = "performance.log"
i = 0
while os.path.exists(perf_logger_file):
    i += 1
    perf_logger_file = f"performance{i}.log"

print(f"Performance logging to: {perf_logger_file}")
perf_logger = setup_custom_logger("PerfLogger", perf_logger_file, simple_formatter)