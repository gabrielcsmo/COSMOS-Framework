import os, logging

QSTAT_CMD = "qstat -F"
QUEUE_ARG = "-q {}"
USED_MEMORY_KEY = "hl:mem_used"
WANTED_STATS = {USED_MEMORY_KEY, "hl:np_load_avg"}

TOTAL_MEMORY_KEY = "hl:mem_total"
UTIL_STATS = {TOTAL_MEMORY_KEY}

def _get_raw(queue):
    cmd = [QSTAT_CMD]
    if queue is not None:
        cmd.append(QUEUE_ARG.format(queue))
    cmd = " ".join(cmd)
    return os.popen(cmd).read()

def log(msg):
    logging.info("[QStatParser] {}".format(msg))

def extract_value(raw_value):
    try:
        if raw_value[-1] == "G":
            return float(raw_value[:-1]) * 1024
        elif raw_value[-1] == 'M':
            return float(raw_value[:-1])
        elif raw_value[-1] == 'K':
            return float(raw_value[:-1]) / 1024
        else:
            return float(raw_value)
    except ValueError:
        pass

    return None

def is_new_machine(line):
    # line filled with '-' marks a new machine
    return line == len(line) * '-'

def qstat_parse(queue):
    raw = _get_raw(queue)
    stats = {k: 0 for k in WANTED_STATS}
    n_machines = 0
    current_machine = None
    new_machine_marker = False
    for line in raw.split("\n"):
        line = " ".join(line.split())  # remove consecutive whitespaces
        if len(line) < 1 or line[0] == '#':
            continue
        if is_new_machine(line):
            new_machine_marker = True
            if current_machine is not None:
                for k in WANTED_STATS:
                    stats[k] += current_machine[k]
            continue
        info = line.split()
        if len(info) < 1:
            continue
        elif len(info) > 1:
            if new_machine_marker:
                # first line for a new machine (after the line filled with '-')
                n_machines += 1
                current_machine = {}
                new_machine_marker = False
            else:
                # line showing info for a running job
                continue
        else:  # some stat we may want
            try:
                k, v = info[0].split("=")
            except ValueError:
                log("Line {!r} isn't in the expected format 'key=value".format(info[0]))
            if k in WANTED_STATS or k in UTIL_STATS:
                val = extract_value(v)
                if val is None:
                    log("For line {!r} => key {!r}, value {!r} could not be parsed!".format(info[0], k, v))
                    continue
                current_machine[k] = val
            
            if TOTAL_MEMORY_KEY in current_machine and USED_MEMORY_KEY in current_machine:
                current_machine[USED_MEMORY_KEY] /= current_machine[TOTAL_MEMORY_KEY]
                del current_machine[TOTAL_MEMORY_KEY]

    if current_machine is not None:
        for k in WANTED_STATS:
            stats[k] += current_machine[k]
    
    if n_machines < 1:
        log("No machines found in queue {!r}".format(queue if queue is not None else "all queues"))
        return None
    
    # cleanup stats names and get average
    return {k.split(":")[-1]: v/n_machines for k, v in stats.items()}