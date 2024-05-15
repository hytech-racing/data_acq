import asyncio
import asyncudp
from hytech_eth_np_proto_py import ht_eth_pb2

from typing import Any
from py_data_acq.common.common_types import QueueData, SharedQueueManager

class SocketInterface:
    def __init__(self, shared_fxglv_queue_event: asyncio.Event, shared_mcap_queue_event: asyncio.Event, queue_manager: SharedQueueManager, command_queue: asyncio.Queue[QueueData], local_addr: str, local_port: int, remote_addr: str, remote_port: int):
        self.fxglv_event = shared_fxglv_queue_event
        self.mcap_event = shared_mcap_queue_event
        self.queue_manager = queue_manager
        self.cmd_q = command_queue
        self.local_addr = local_addr
        self.local_port = local_port
        self.remote_addr = remote_addr
        self.remote_port = remote_port

    async def run(self):
        # Setup both receive and send tasks to run concurrently
        receiver_task = asyncio.create_task(self.receive_message_over_udp())
        sender_task = asyncio.create_task(self.send_message_over_udp())

        # Wait for both tasks to complete
        await asyncio.gather(receiver_task, sender_task)

    async def receive_message_over_udp(self):
        sock = await asyncudp.create_socket(local_addr=(self.local_addr, self.local_port))
        print(f"Listening on UDP port {self.local_port}")
        while True:
            try:
                data, addr = await sock.recvfrom()  # Define a buffer size if needed
                if data:
                    print("recvd")
                    union_msg = ht_eth_pb2.HT_ETH_Union()
                    try:
                        union_msg.ParseFromString(data)
                    except Exception as exp:
                        print(f'DecodeError: {exp}')
                        continue
                    # if(union_msg.HasField('config_')):
                    #     queue.put(QueueData(union_msg.config_DESCRIPTOR.name, union_msg.config_))
                    queue_data = QueueData(union_msg.DESCRIPTOR.name, union_msg)
                    await self.queue_manager.append_to_queues(queue_data)
                    self.fxglv_event.set()
                    self.mcap_event.set()
                
            except asyncio.CancelledError:
                break  # Allows the task to be cancelled gracefully

    async def send_message_over_udp(self):
        sock = await asyncudp.create_socket(remote_addr=(self.remote_addr, self.remote_port))
        print(f"Ready to send to {self.remote_addr}:{self.remote_port}")
        while True:
            try:
                msg_to_send = await self.cmd_q.get()
                sock.sendto(msg_to_send.data)
                print(f"Sent message to {self.remote_addr}:{self.remote_port}")
            except asyncio.CancelledError:
                break  # Allows the task to be cancelled gracefully
