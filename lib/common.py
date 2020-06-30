# in here goes anything that should be available in hosts and framework, so anything that is common between the two components
# avoid imports in this file, as packages will need to be installed on hosts and on the machine that runs the framework

class InfoKeys:
    SYSTEM_MEMORY = "sys_mem"
    SYSTEM_CPU = "sys_cpu"
    PER_TASK_USAGE = "t_usage"
    TASK_CPU = "cpu"
    TASK_MEMORY = "mem"
    TASK_MEM_INTENSIVE = "m_intensive"
    TASK_COUNT = "count"
    HOSTNAME = "hostname"
    TIMESTAMP = "timestamp"