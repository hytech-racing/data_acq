import threading
import queue
import cantools
import can
from py_data_acq.common.protobuf_helpers import pack_protobuf_msg
from py_data_acq.common.common_types import QueueData, DataInputType
from hytech_eth_np_proto_py import ht_eth_pb2
import socket

class UDPInterface(threading.Thread):
    def __init__(self, output_queue: queue.Queue[QueueData], config_output_queue: queue.Queue[QueueData], recv_ip: str, recv_port: int):
        super().__init__()
        self.output_queue = output_queue
        self.config_output_queue = config_output_queue
        self.recv_ip = recv_ip
        self.recv_port = recv_port

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((self.recv_ip, self.recv_port))
            while True:
                data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
                self.process_data(data, addr)

    def process_data(self, data, addr):
        union_msg = ht_eth_pb2.HT_ETH_Union()
        try:
            union_msg.ParseFromString(data)
            for field_desc, value in union_msg.ListFields():
                if field_desc.message_type is not None:
                    composite_msg = getattr(union_msg, field_desc.name)
                    queue_data = QueueData(composite_msg.DESCRIPTOR.name, composite_msg, DataInputType.ETHERNET_DATA)
                    
                    if composite_msg.DESCRIPTOR.name == 'config':
                        self.config_output_queue.put(queue_data)
                    self.output_queue.put(queue_data)
        except Exception as e:
            print(e)

class CANInterface(threading.Thread):
    def __init__(self, can_msg_decoder: cantools.db.Database, message_classes, queue: queue.Queue[QueueData], can_bus):
        super().__init__()
        self.can_msg_decoder = can_msg_decoder
        self.message_classes = message_classes
        self.out_queue = queue
        self.can_bus = can_bus

    def run(self):
        reader = can.BufferedReader()
        notifier = can.Notifier(self.can_bus, [reader])

        while True:
            msg = reader.get_message()  # This blocks until a message is available
            if msg is None:
                continue

            id = msg.arbitration_id
            try:
                decoded_msg = self.can_msg_decoder.decode_message(
                    msg.arbitration_id, msg.data, decode_containers=True
                )
                
                msg = self.can_msg_decoder.get_message_by_frame_id(msg.arbitration_id)
                
                msg = pack_protobuf_msg(
                    decoded_msg, msg.name.lower(), self.message_classes
                )
                
                data = QueueData(msg.DESCRIPTOR.name, msg, DataInputType.CAN_DATA)
                self.out_queue.put(data)
                
            except Exception as e:
                print(e)

        notifier.stop()

class InterfaceProducer:
    def __init__(self, can_msg_db: cantools.db.Database, message_classes, can_bus, recv_ip, recv_port):
        self.output_queue = queue.Queue()
        self.config_output_queue = queue.Queue()
        self.can_interface_producer = CANInterface(can_msg_db, message_classes, self.output_queue, can_bus)
        self.udp_interface_producer = UDPInterface(self.output_queue, self.config_output_queue, recv_ip, recv_port)

    def start(self):
        self.can_interface_producer.start()
        self.udp_interface_producer.start()

    def join(self):
        self.can_interface_producer.join()
        self.udp_interface_producer.join()



