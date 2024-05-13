import asyncio
import socket
import asyncudp

from typing import Any
from py_data_acq.common.common_types import QueueData
# from hytech_eth_np_proto_py import ht_eth_pb2

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
        print("Exit from the Context Manager...")
        # await self.close_sockets()
    def __init__(self, port_to_pb_map) -> None:
        self.port_to_type_map = port_to_pb_map
    async def receive_message_over_udp(self, addr: str, port: int, output_queues: list[asyncio.Queue[QueueData]]):
        sock = await asyncudp.create_socket(local_addr=(addr, port))
        while True:
            data, addr = await sock.recvfrom()
            self.port_to_type_map[port].
            # print(wrapper)
            # data_arr = []

            # for data in data_arr:
            for queue in output_queues:
                await queue.put(data)
