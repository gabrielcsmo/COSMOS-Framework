import psutil as ps
import socket
import argparse
import select
import os
import json
from common import InfoKeys

parser = argparse.ArgumentParser()
parser.add_argument('--server', action="store", help="Info server hostname",
                    type=str, required=True)
parser.add_argument('--port', action="store", help="Info server port",
                    type=int, required=True)
parser.add_argument('--whoami', action="store", type=str, required=True)
parser.add_argument('--task_prefix', action="store", type=str, required=True)
parser.add_argument('--report_timeout', action="store", type=float, required=True, help="In seconds, how often to report usage.")

class SystemInfoService(object):
    def __init__(self, task_prefix):
        super().__init__()
        self.task_prefix = task_prefix

    @property
    def _procs_pid_cmd(self):
        return "ps -u $USER -o pid,cmd | grep ./{} | grep -v grep | awk '{}'".format(self.task_prefix, "{print $1}")

    @property
    def _tasks_pids(self):
        print("ps_cmd: {}".format(self._procs_pid_cmd))
        raw = os.popen(self._procs_pid_cmd).read()
        pids = [int(pid) for pid in filter(lambda p: len(p) > 0, raw.split('\n'))]

        print("pids: {}".format(str(pids)))
        return pids
    
    @property
    def _processes(self):
        for pid in self._tasks_pids:
            try:
                yield ps.Process(pid)
            except ps.NoSuchProcess:
                pass
    
    def _get_process_usage(self, process):
        cpu_usage = process.cpu_percent(0.1)
        memory_usage = process.memory_percent()
        return cpu_usage, memory_usage

    def _get_resources_used(self):
        per_task_usage = {}
        for proc in self._processes:
            name = proc.name().replace(self.task_prefix, "")
            if name not in per_task_usage:
                per_task_usage[name] = {InfoKeys.TASK_CPU: 0, InfoKeys.TASK_MEMORY: 0, InfoKeys.TASK_COUNT: 0, InfoKeys.TASK_MEM_INTENSIVE: False}
            
            cpu_usage, memory_usage = self._get_process_usage(proc)
            per_task_usage[name][InfoKeys.TASK_CPU] += cpu_usage
            per_task_usage[name][InfoKeys.TASK_MEMORY] += memory_usage
            per_task_usage[name][InfoKeys.TASK_COUNT] += 1

        for task_name in per_task_usage.keys():
            current_entry = per_task_usage[task_name]
            current_entry[InfoKeys.TASK_CPU] /= current_entry[InfoKeys.TASK_COUNT]
            current_entry[InfoKeys.TASK_MEM_INTENSIVE] = current_entry[InfoKeys.TASK_MEMORY] > 30

        return per_task_usage        
    
    def _get_system_load(self):
        return {InfoKeys.SYSTEM_CPU: ps.cpu_percent(),
                InfoKeys.SYSTEM_MEMORY: ps.virtual_memory().percent}
    
    def get_info(self):
        system_load = self._get_system_load()
        per_task_usage = self._get_resources_used()

        return {**system_load, InfoKeys.PER_TASK_USAGE: per_task_usage}

def pack_message(message):
    return bytes([len(message)]) + message.encode()

def send_message(message, server):
    msg_bytes = pack_message(json.dumps(message))
    while len(msg_bytes) > 0:
        bytessent = server.send(msg_bytes)
        msg_bytes = msg_bytes[bytessent:]

from time import sleep
def main():
    args = parser.parse_args()

    hostname = args.whoami
    timeout = args.report_timeout

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            server.connect((args.server, args.port))
            break
        except socket.error:
            sleep(1)
            pass

    sys_info = SystemInfoService(args.task_prefix)    
    send_message({InfoKeys.HOSTNAME: hostname}, server)

    while True:
        # send usage
        send_message(sys_info.get_info(), server)

        try:
            # sleep while waiting to receive something, when anything is received, shutdown
            server.settimeout(timeout)
            server.recv(1)
            break
        except:
            server.settimeout(0)

    server.close()


if __name__ == "__main__":
    main()