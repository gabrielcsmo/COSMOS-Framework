import os, logging

QSTAT_CMD = "qstat -F"
QUEUE_ARG = "-q {}"
WANTED_STATS = {"hl:mem_free", "hl:np_load_avg"}

def _get_raw(queue):
    cmd = [QSTAT_CMD]
    if queue is not None:
        cmd.append(QUEUE_ARG.format(queue))
    cmd = " ".join(cmd)
    return os.popen(cmd).read()

def log(msg):
    logging.info("[QStatParser] {}".format(msg))

def qstat_parse(queue):
    raw = _get_raw(queue)
    stats = {k: 0 for k in WANTED_STATS}
    n_machines = 0
    for line in raw.split("\n"):
        line = " ".join(line.split())  # remove consecutive whitespaces
        if len(line) < 1 or line[0] == '-' or line[0] == '#':
            continue
        info = line.split()
        if len(info) < 1:
            continue
        elif len(info) > 1:  # first line for new machine
            n_machines += 1
            current_machine = info[0]
        else:  # some stat we may want
            try:
                k, v = info[0].split("=")
            except ValueError:
                log("Line {!r} isn't in the expected format 'key=value".format(info[0]))
            if k in WANTED_STATS:
                try:
                    if v[-1] == "G":
                        stats[k] += float(v[:-1])
                    else:
                        stats[k] += float(v)
                except ValueError:
                    log("For line {!r} => key {!r}, value {!r} could not be converted to float!".format(info[0], k, v))
    
    if n_machines < 1:
        log("No machines found in queue {!r}".format(queue if queue is not None else "all queues"))
        return None
    
    # cleanup stats names and get average
    return {k.split(":")[-1]: v/n_machines for k, v in stats.items()}