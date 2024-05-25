import queue
import threading
import socket
from py_data_acq.common.common_types import QueueData


class InterfaceConsumer(threading.Thread):
    def __init__(self, interface_queue: queue.Queue[QueueData], sendto_ip: str, sendto_port: int):
        super().__init__()
        self.interface_queue = interface_queue
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sendto_ip = sendto_ip
        self.sendto_port = sendto_port
        
    def run(self):
        while True:
            output = self.interface_queue.get()
            self.sock.sendto(output.data, (self.sendto_ip, self.sendto_port))
            