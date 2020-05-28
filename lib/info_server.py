from threading import Thread, Event, Lock
import socket, select, sys
from time import sleep
import logging
import json, struct
from lib.common import InfoKeys
from lib.custom_loggers import perf_logger

INFO_SERVICE_HOSTNAME = socket.gethostname()
INFO_SERVICE_PORT = 28972

class Connection(object):
    def __init__(self, conn_socket):
        self.conn_socket: socket.socket = conn_socket
        self.receive = None
        self.recv_size = None
        self.send = None
        self.hostname = None
        self.usage_lock = Lock()
        self.usage = {InfoKeys.SYSTEM_CPU: 0, InfoKeys.SYSTEM_MEMORY: 0}

    def send_message(self):
        if self.send is None or len(self.send) == 0:
            return None
        
        while len(self.send) > 0:
            bytes_sent = self.conn_socket.send(self.send)
            self.send = self.send[bytes_sent:]
        
        self.send = None
        
    def update(self):
        stats = json.loads(self.receive)
        self.usage_lock.acquire()
        self.usage = stats
        self.usage_lock.release()
        perf_logger.info(json.dumps({'host': self.hostname, 'stats': stats}))
        
    def local_update_usage(self, task):
        self.usage_lock.acquire()
        self.usage[InfoKeys.SYSTEM_CPU] += (task.length / 10) * task.cpu_weight
        self.usage[InfoKeys.SYSTEM_MEMORY] += (task.length / 10) * task.memory_weight
        self.usage_lock.release()

class SystemInfoServer(Thread):
    stop_server = Event()

    def __init__(self):
        Thread.__init__(self)
        self.start()
        self.active_connections = {}
        self.host_to_connection_map = {}
    
    def get_usage(self, hostname):
        while hostname not in self.host_to_connection_map:
            sleep(1)
   
        return self.host_to_connection_map[hostname].usage
    
    def local_update_usage(self, hostname, task):
        self.host_to_connection_map[hostname].local_update_usage(task)

    def remove_connection(self, fileno):
        conn = self.active_connections[fileno]
        try:
            conn.conn_socket.close()
        except:
            pass
        self.epoll.unregister(fileno)
        del self.active_connections[fileno]
    
    def create_socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setblocking(False)
        try:
            s.bind((INFO_SERVICE_HOSTNAME, INFO_SERVICE_PORT))
        except socket.error as msg:
            logging.error("[SystemInfoServer] Couldn't bind server socket. Error: {}".format(msg))
            exit(1)
        print("[SystemInfoServer] Listening on {}:{}".format(INFO_SERVICE_HOSTNAME, INFO_SERVICE_PORT))
        s.listen(1)
        return s
    
    def handle_incoming_connection(self):
        conn, addr = self.server_socket.accept()
        conn.setblocking(False)
        self.epoll.register(conn.fileno(), select.EPOLLIN)
        self.active_connections[conn.fileno()] = Connection(conn_socket=conn)

    def handle_incoming_message(self, fileno):
        '''
            First byte received represents the length of the mesage to be received.
        '''
        conn = self.active_connections[fileno]
        received = conn.conn_socket.recv(1024)

        if received is None:
            return

        if conn.recv_size is None and len(received) >= 4:
            conn.recv_size = struct.unpack("I", received[:4])[0]
            conn.receive = received[4:]
        else:
            if conn.receive is None:
                conn.receive = b""
            conn.receive += received
        
        if len(conn.receive) == conn.recv_size:
            # first message received tells us which host is associated with the conenction
            if conn.hostname is None:
                conn.hostname = json.loads(conn.receive)[InfoKeys.HOSTNAME]
                self.host_to_connection_map[conn.hostname] = conn
                print("[SystemInfoServer] Registered {}.".format(conn.hostname, fileno))
            else:
                conn.update()
            conn.recv_size, conn.receive = None, None

    def run(self):
        self.server_socket = self.create_socket()
        self.epoll = select.epoll()
        self.epoll.register(self.server_socket.fileno(), select.EPOLLIN)

        try:
            while not SystemInfoServer.stop_server.is_set():
                events = self.epoll.poll(timeout=1)
                for fileno, event in events:
                    if fileno == self.server_socket.fileno():
                        self.handle_incoming_connection()
                    elif event & select.EPOLLIN:
                        self.handle_incoming_message(fileno)
                    elif event & select.EPOLLHUP:
                        self.remove_connection(fileno)
        finally:
            print("Shutting down system info server...")
            for fileno, conn in self.active_connections.items():
                # let the service know it should shutdown
                conn.conn_socket.setblocking(True)
                conn.conn_socket.send(b"q")

                conn.conn_socket.close()
            self.epoll.close()
            self.server_socket.close()
