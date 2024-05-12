import asyncio
import socket
import asyncudp

from py_data_acq.common.common_types import QueueData
from hytech_eth_np_proto_py import ht_eth_pb2

# from vn_protos_np_proto_py.vectornav_proto import wrapper_pb2
class ParamInterface:
    def __init__(self, addr, port):
        self.addr = addr
        self.port = port


async def receive_message_over_udp(addr, port, mcap_data_out_queue, fxglv_data_out_queue, can_out_q):
    sock = await asyncudp.create_socket(local_addr=(addr, port))
    while True:
        data, addr = await sock.recvfrom()
        
        # print(wrapper)
        # data_arr = []

        # for data in data_arr:
        await mcap_data_out_queue.put(data)
        await fxglv_data_out_queue.put(data)
