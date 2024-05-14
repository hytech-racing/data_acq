import asyncio
import socket
import asyncudp
from hytech_eth_np_proto_py import ht_eth_pb2

from typing import Any
from py_data_acq.common.common_types import QueueData, SharedQueueManager

# this class will be able to take in any protobuf message from any port and using the port to type map 
# parse the data in the correct way and output the correct data to all of the output data queues 
class SocketInterface:
    def __await__(self):
        async def closure():
            return self
        return closure().__await__()
    def __enter__(self):
        return self
    def __exit__(self, exc_, exc_type_, tb_):
        pass
    def __aenter__(self):
        return self
    async def __aexit__(self, exc_type: Any, exc_val: Any, traceback: Any):
        pass
    def __init__(self, shared_fxglv_queue_event: asyncio.Event, shared_mcap_queue_event: asyncio.Event, queue_manager: SharedQueueManager, command_queue: asyncio.Queue[QueueData]):
        self.fxglv_event = shared_fxglv_queue_event
        self.mcap_event = shared_mcap_queue_event
        self.queue_manager = queue_manager
        self.cmd_q = command_queue
    # receives the udp data and outputs the data into the passed in output queues
    # 
    async def receive_message_over_udp(self, addr: str, recv_port: int):
        sock = await asyncudp.create_socket(local_addr=(addr, recv_port))
        while True:
            data, addr = await sock.recvfrom()
            if data:
                print("yo got somethin")
                union_msg = ht_eth_pb2.HT_ETH_Union()
                try:
                    union_msg.ParseFromString(data)
                except union_msg.DecodeError as exp:
                    print('DecodeError: {}'.format(exp))
                    continue
                except:
                    print('** unexpected error')
                    continue
                queue_data = QueueData(union_msg.DESCRIPTOR.name, union_msg)
                await self.queue_manager.append_to_queues(queue_data)
                self.fxglv_event.set()
                self.mcap_event.set()
    
    async def send_message_over_udp(self, remote_addr: str, send_port: int):
        sock = await asyncudp.create_socket(remote_addr=(remote_addr, send_port))
        while True:
            msg_to_send = await self.cmd_q.get()
            sock.sendto(msg_to_send.data)
                