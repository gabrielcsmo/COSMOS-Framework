import psutil as ps
import socket
import argparse
import select
import os

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
        return "ps -u $USER -o pid,cmd | grep {}* | grep -v grep | awk '{}'".format(self.task_prefix, "{print $1}")

    def get_resources_used(self):
        raw = os.popen(self._procs_pid_cmd).read()
        pids = [int(pid) for pid in filter(lambda p: len(p) > 0, raw.split('\n'))]

        cpu_total_usage_percent = 0.0
        memory_total_usage_percent = 0.0
        nprocs = len(pids)
        for pid in pids:
            try:
                proc = ps.Process(pid)
                cpu_total_usage_percent += proc.cpu_percent(0.1)
                memory_total_usage_percent += proc.memory_percent()
            except ps.NoSuchProcess:
                nprocs -= 1

        cpu_total_usage_percent = cpu_total_usage_percent / nprocs if nprocs > 0 else 0.0
        memory_total_usage_percent = memory_total_usage_percent / nprocs if nprocs > 0 else 0.0
        return cpu_total_usage_percent, memory_total_usage_percent
    
    def get_system_load(self):
        return ps.cpu_percent(), ps.virtual_memory().percent
    
    def get_info(self):
        return "{}|{}|{}|{}".format(*self.get_system_load(), *self.get_resources_used())


def pack_message(message):
    return bytes([len(message)]) + message.encode()


def send_message(message, server):
    msg_bytes = pack_message(message)
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
    send_message(args.whoami, server)

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