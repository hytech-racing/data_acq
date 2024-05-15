import asyncio

# socket interface (for parameter server, CASE live output, any other protobuf messages ...)
from py_data_acq.socket_interface.socket_interface import SocketInterface
from py_data_acq.common.common_types import SharedQueueManager
from py_data_acq.foxglove_live.foxglove_ws import HTProtobufFoxgloveServer
from py_data_acq.mcap_writer.writer import HTPBMcapWriter
from py_data_acq.common.common_types import QueueData
import py_data_acq.common.protobuf_helpers as pb_helpers
from py_data_acq.common.common_types import (
    MCAPServerStatusQueueData,
    MCAPFileWriterCommand,
)
from py_data_acq.web_server.web_app import WebApp

from hytech_np_proto_py import hytech_pb2

import sys
import os
import can
from can.interfaces.udp_multicast import UdpMulticastBus
import cantools
import logging


async def recv_f(socket_interface):
    async with socket_interface as si:
        await si.receive_message_over_udp('127.0.0.1', 20001)
async def send_f(socket_interface):
    async with socket_interface as si:
        await si.send_message_over_udp('127.0.0.1', 20002)

async def run(logger):
    queue = asyncio.Queue()
    queue2 = asyncio.Queue()
    init_writing_on_start = True
    mcap_writer_status_queue = asyncio.Queue(maxsize=1)
    mcap_writer_cmd_queue = asyncio.Queue(maxsize=1)
    test_q = asyncio.Queue()    
    socket_send_queue = asyncio.Queue()    
    shared_mcap_write_event = asyncio.Event()
    shared_foxglove_write_event = asyncio.Event()
    shared_param_event = asyncio.Event()
    data_queue_manager = SharedQueueManager(param_update_event=shared_param_event)


    webapp = WebApp(
        writer_command_queue=mcap_writer_cmd_queue,
        writer_status_queue=mcap_writer_status_queue,
        queue_manager=data_queue_manager,
        feedback_event=shared_param_event,
        general_command_queue=socket_send_queue,
        init_writing=init_writing_on_start,
        init_filename=""
    )
    
    socket_interface = SocketInterface(
        shared_fxglv_queue_event=shared_foxglove_write_event, 
        shared_mcap_queue_event=shared_mcap_write_event,
        queue_manager=data_queue_manager, 
        command_queue=socket_send_queue,
        local_addr = '127.0.0.1',
        local_port = 20001,
        remote_addr = '127.0.0.1',
        remote_port = 20002
        )
    
    srv_task = asyncio.create_task(webapp.start_server())
    socket_task = asyncio.create_task(socket_interface.run())
    await asyncio.gather(srv_task, socket_task)

if __name__ == "__main__":
    logging.basicConfig()
    logger = logging.getLogger("data_writer_service")
    logger.setLevel(logging.INFO)
    asyncio.run(run(logger))
