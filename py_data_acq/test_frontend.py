#!/usr/bin/env python
# import asyncio

# from py_data_acq.data_writers.foxglove_live.foxglove_ws import HTProtobufFoxgloveServer
# from py_data_acq.data_writers.mcap_writer.writer import HTPBMcapWriter
# from py_data_acq.common.common_types import QueueData
# import py_data_acq.common.protobuf_helpers as pb_helpers
# from py_data_acq.common.common_types import (
#     MCAPServerStatusQueueData,
#     MCAPFileWriterCommand,
# )
# from hytech_np_proto_py import hytech_pb2
# import concurrent.futures
# import sys
# import os
# import can
# from can.interfaces.udp_multicast import UdpMulticastBus
# import cantools
# import logging

# from py_data_acq.web_server.web_app import WebApp
# async def write_data_to_mcap(
#     writer_cmd_queue: asyncio.Queue,
#     writer_status_queue: asyncio.Queue,
#     data_queue: asyncio.Queue,
#     mcap_writer: HTPBMcapWriter,
#     write_on_init: bool,
# ):
#     writing = write_on_init
#     async with mcap_writer as mcw:
#         while True:
#             response_needed = False
#             if not writer_cmd_queue.empty():
#                 cmd_msg = writer_cmd_queue.get_nowait()
#                 writing = cmd_msg.writing
#                 response_needed = True

#             if writing:
#                 if response_needed:
#                     await mcw.open_new_writer()
#                     await writer_status_queue.put(MCAPServerStatusQueueData(True, mcw.actual_path))
#                 await mcw.write_data(data_queue)
#             else:
#                 if response_needed:
#                     await writer_status_queue.put(MCAPServerStatusQueueData(False, mcw.actual_path))
#                     await mcw.close_writer()
#                 # still keep getting the msgs from queue so it doesnt fill up
#                 trash_msg = await data_queue.get()

# async def run(logger):
#     # for example, we will have CAN as our only input as of right now but we may need to add in
#     # a sensor that inputs over UART or ethernet
#     queue = asyncio.Queue()
#     queue2 = asyncio.Queue()
#     path_to_bin = ""
#     path_to_dbc = ""

#     if len(sys.argv) > 2:
#         path_to_bin = sys.argv[1]
#         path_to_dbc = sys.argv[2]
#     else:
#         path_to_bin = os.environ.get("BIN_PATH")
#         path_to_dbc = os.environ.get("DBC_PATH")

#     full_path = os.path.join(path_to_bin, "hytech.bin")
#     full_path_to_dbc = os.path.join(path_to_dbc, "hytech.dbc")
#     db = cantools.db.load_file(full_path_to_dbc)

#     list_of_msg_names, msg_pb_classes = pb_helpers.get_msg_names_and_classes()
#     fx_s = HTProtobufFoxgloveServer(
#         "0.0.0.0", 8765, "hytech-foxglove", full_path, list_of_msg_names
#     )
#     path_to_mcap = "."
#     if os.path.exists("/etc/nixos"):
#         logger.info("detected running on nixos")
#         path_to_mcap = "/home/nixos/recordings"

#     init_writing_on_start = True
#     mcap_writer_status_queue = asyncio.Queue(maxsize=1)
#     mcap_writer_cmd_queue = asyncio.Queue(maxsize=1)
#     mcap_writer = HTPBMcapWriter(path_to_mcap, init_writing_on_start)
#     mcap_web_server = WebApp(
#         writer_command_queue=mcap_writer_cmd_queue,
#         writer_status_queue=mcap_writer_status_queue,
#         init_writing=init_writing_on_start,
#         init_filename=mcap_writer.actual_path
#     )

#     # mcap_task = asyncio.create_task(write_data_to_mcap(mcap_writer_cmd_queue, mcap_writer_status_queue, queue2, mcap_writer, init_writing_on_start))
#     srv_task = asyncio.create_task(mcap_web_server.start_server())
#     logger.info("created tasks")
#     # in the mcap task I actually have to deserialize the any protobuf msg into the message ID and
#     # the encoded message for the message id. I will need to handle the same association of message id
#     # and schema in the foxglove websocket server.

#     # await asyncio.gather(mcap_task, srv_task)
#     await asyncio.gather(srv_task)

# if __name__ == "__main__":
#     logging.basicConfig()
#     logger = logging.getLogger("data_writer_service")
#     logger.setLevel(logging.INFO)
#     asyncio.run(run(logger))