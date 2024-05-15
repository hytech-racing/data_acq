# #!/usr/bin/env python
# import asyncio

# # socket interface (for parameter server, CASE live output, any other protobuf messages ...)
# from py_data_acq.socket_interface.socket_interface import SocketInterface
# from py_data_acq.common.common_types import SharedQueueManager
# from py_data_acq.data_writers.foxglove_live.foxglove_ws import HTProtobufFoxgloveServer
# from py_data_acq.data_writers.mcap_writer.writer import HTPBMcapWriter
# from py_data_acq.common.common_types import QueueData
# import py_data_acq.common.protobuf_helpers as pb_helpers
# from py_data_acq.common.common_types import (
#     MCAPServerStatusQueueData,
#     MCAPFileWriterCommand,
# )
# from py_data_acq.web_server.web_app import WebApp

# from hytech_np_proto_py import hytech_pb2

# import sys
# import os
# import can
# from can.interfaces.udp_multicast import UdpMulticastBus
# import cantools
# import logging

# # TODO
# # - [ ] async udp socket receive handling
# #   - [x] add in the HT_params flake as an input to this flake
# #   - [x] add in the generated python library from the HT_params flake
# #   - [x] add the socket interface python code for receiving the protobuf messages
# #   - [x] add ability to the socket interface for handling sending of config to the MCU
# # - [x] add in the parameter list creation using type inflection with the config protobuf message
# #   - [x] test out website creation
# # - [x] add in ability to easily kill the python script lol
# # - [ ] add in enqueue / dequeue of config message to the param msg queue for the frontend updating
# #   - [x] enqueue happens in the shared queue manager
# #   - [ ] add params update from MCU in web_app: 
# #       - [x] await dequeue of the config message after the user requests to get the latest config
# #       - [x] enqueue config message in the sharedqueuemanager
# # - [ ] test out the socket interface comms task for parameter protocol
# # - [ ] port existing queue-using apps to use the queue manager
# # - [ ] add required tasks (maybe look into task groups?)
# #       - [x] (NEW) udp socket receive task
# #       - [x] (CHANGED) web app task
# #       - [ ] (NEW) udp socket sending task
# # - [ ] add nix run ability for local testing

# def find_can_interface():
#     """Find a CAN interface by checking /sys/class/net/."""
#     for interface in os.listdir("/sys/class/net/"):
#         if interface.startswith("can"):
#             return interface
#     return None

# async def continuous_can_receiver(
#     can_msg_decoder: cantools.db.Database, message_classes, queue, q2, can_bus
# ):
#     loop = asyncio.get_event_loop()
#     reader = can.AsyncBufferedReader()
#     notifier = can.Notifier(can_bus, [reader], loop=loop)

#     while True:
#         # Wait for the next message from the buffer
#         msg = await reader.get_message()

#         # print("got msg")
#         id = msg.arbitration_id
#         try:
#             decoded_msg = can_msg_decoder.decode_message(
#                 msg.arbitration_id, msg.data, decode_containers=True
#             )
#             # print("decoded msg")
#             msg = can_msg_decoder.get_message_by_frame_id(msg.arbitration_id)
#             # print("got msg by id")
#             msg = pb_helpers.pack_protobuf_msg(
#                 decoded_msg, msg.name.lower(), message_classes
#             )
#             # print("created pb msg successfully")
#             data = QueueData(msg.DESCRIPTOR.name, msg)
#             await queue.put(data)
#             await q2.put(data)
#         except Exception as e:
#             # print(id)
#             # print(e)
#             pass

#     # Don't forget to stop the notifier to clean up resources.
#     notifier.stop()

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


# async def fxglv_websocket_consume_data(queue, foxglove_server):
#     async with foxglove_server as fz:
#         while True:
#             await fz.send_msgs_from_queue(queue)

# async def recv_f(socket_interface):
#     async with socket_interface as si:
#         await si.receive_message_over_udp('127.0.0.1', 20001)
# async def send_f(socket_interface):
#     async with socket_interface as si:
#         await si.send_message_over_udp('127.0.0.1', 20002)
# async def run(logger):
#     # for example, we will have CAN as our only input as of right now but we may need to add in
#     # a sensor that inputs over UART or ethernet
#     can_interface = find_can_interface()

#     if can_interface:
#         print(f"Found CAN interface: {can_interface}")
#         try:
#             # Attempt to initialize the CAN bus
#             bus = can.interface.Bus(channel=can_interface, bustype="socketcan")
#             print(f"Successfully initialized CAN bus on {can_interface}")
#             # Interface exists and bus is initialized, but this doesn't ensure the interface is 'up'
#         except can.CanError as e:
#             print(f"Failed to initialize CAN bus on {can_interface}: {e}")
#     else:
#         print("defaulting to using virtual can interface vcan0")
#         bus = can.Bus(
#             channel=UdpMulticastBus.DEFAULT_GROUP_IPv6, interface="udp_multicast"
#         )

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
#     queue_params = asyncio.Queue()
#     socket_send_queue = asyncio.Queue()    
#     shared_mcap_write_event = asyncio.Event()
#     shared_foxglove_write_event = asyncio.Event()
#     shared_param_event = asyncio.Event()
#     data_queue_manager = SharedQueueManager(param_update_event=shared_param_event)

#     mcap_writer = HTPBMcapWriter(path_to_mcap, init_writing_on_start)
#     webapp = WebApp(
#         writer_command_queue=mcap_writer_cmd_queue,
#         writer_status_queue=mcap_writer_status_queue,
#         queue_manager=data_queue_manager,
#         feedback_event=shared_param_event,
#         general_command_queue=socket_send_queue,
#         init_writing=init_writing_on_start,
#         init_filename=mcap_writer.actual_path
#     )
    
#     socket_interface = SocketInterface(
#         shared_fxglv_queue_event=shared_foxglove_write_event, 
#         shared_mcap_queue_event=shared_mcap_write_event,
#         queue_manager=data_queue_manager, 
#         command_queue=socket_send_queue,
#         local_addr = '127.0.0.1',
#         local_port = 20001,
#         remote_addr = '127.0.0.1',
#         remote_port = 20002
#         )

#     can_receiver_task = asyncio.create_task(
#         continuous_can_receiver(db, msg_pb_classes, queue, queue2, bus)
#     )
#     fx_task = asyncio.create_task(fxglv_websocket_consume_data(queue, fx_s))
#     mcap_task = asyncio.create_task(write_data_to_mcap(mcap_writer_cmd_queue, mcap_writer_status_queue, queue2, mcap_writer, init_writing_on_start))
#     srv_task = asyncio.create_task(webapp.start_server(queue_params))
#     # socket_recv_task = asyncio.create_task(recv_f(socket_interface))
#     # socket_send_task = asyncio.create_task(send_f(socket_interface))

#     socket_task = asyncio.create_task(socket_interface.run(queue_params))
#     logger.info("created tasks")
#     # print("yooo")
#     # in the mcap task I actually have to deserialize the any protobuf msg into the message ID and
#     # the encoded message for the message id. I will need to handle the same association of message id
#     # and schema in the foxglove websocket server.

#     # await asyncio.gather(can_receiver_task, socket_recv_task, fx_task, mcap_task, srv_task)
#     await asyncio.gather(srv_task)
#     # await asyncio.gather(socket_recv_task)

# if __name__ == "__main__":
#     logging.basicConfig()
#     logger = logging.getLogger("data_writer_service")
#     logger.setLevel(logging.INFO)
#     asyncio.run(run(logger))
