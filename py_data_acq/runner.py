#!/usr/bin/env python
import asyncio

from py_data_acq.foxglove_live.foxglove_ws import HTProtobufFoxgloveServer
from py_data_acq.mcap_writer.writer import HTPBMcapWriter
from py_data_acq.common.common_types import QueueData
import py_data_acq.common.protobuf_helpers as pb_helpers
from py_data_acq.common.common_types import (
    MCAPServerStatusQueueData,
    MCAPFileWriterCommand,
)
from py_data_acq.web_server.mcap_server import MCAPServer
from hytech_np_proto_py import hytech_pb2
import concurrent.futures
import sys
import os
import can
from can.interfaces.udp_multicast import UdpMulticastBus
import cantools
import logging
#aero
import struct
import serial
import serial_asyncio

from aero_sensor_protos_np_proto_py.aero_sensor import aero_sensor_pb2
from aero_sensor_protos_np_proto_py.aero_sensor.aero_sensor_pb2 import aero_data

from foxglove_schemas_protobuf.CompressedImage_pb2 import CompressedImage
import cv2



# TODO we may want to have a config file handling to set params such as:
#      - foxglove server port
#      - foxglove server ip
#      - config to inform io handler (say for different CAN baudrates)

can_methods = {
    "debug": [UdpMulticastBus.DEFAULT_GROUP_IPv4, "udp_multicast"],
    "local_can_usb_KV": [0, "kvaser"],
    "local_debug": ["vcan0", "socketcan"],
}


def find_can_interface():
    """Find a CAN interface by checking /sys/class/net/."""
    for interface in os.listdir("/sys/class/net/"):
        if interface.startswith("can"):
            return interface
    return None


#add aero data to q
async def append_sensor_data(queue, q2, data, port_name):
    msg = aero_sensor_pb2.aero_data()
    msg.readings_pa.extend(data)
    sensor_name = port_name.split("/")[-1]
    msg.DESCRIPTOR.name = msg.DESCRIPTOR.name + "_" + sensor_name
    msg = QueueData(msg.DESCRIPTOR.name, msg)
    await queue.put(msg)
    await q2.put(msg)

#Listener class
class Listener(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport
        self.logging_enabled = True
        self.transport.write(b"@")
        print(f"Successfully wrote '@'")
        self.transport.write(b"D")
        print(f"Successfully wrote 'D'")

        print("Connection made")
        
    def data_received(self, data):
        # print(data)
        self.buffer += data
        if b"#" in self.buffer:
            parts = self.buffer.split(b"#", 1)
            before_hash = parts[0]
            after_hash = parts[1]

            if len(after_hash) >= 46:
                floats = process_buffer(after_hash[:32])
                if self.logging_enabled:
                    asyncio.get_event_loop().create_task(append_sensor_data(self.queue, self.q2, floats, self.port_name))
                    
                    # log_sensor_data(self.queue, floats, self.port_name)
                    # print(floats)
                self.buffer = after_hash[46:]
            else:
                self.buffer = b"#" + after_hash
    def connection_lost(self, exc):
        print("Connection lost")

    def setup_listener(self, queue, q2, port_name):
        self.buffer = b""
        self.queue = queue
        self.q2 = q2
        self.port_name = port_name

    def enable_queue(self):
        self.logging_enabled = True

    def disable_queue(self):
        self.logging_enabled = False

#Aero sensor listener
async def continuous_aero_receiver(queue, q2):
    loop = asyncio.get_event_loop()
    ports = ['/dev/ttyACM0', '/dev/ttyACM1']
    coro1 = serial_asyncio.create_serial_connection(loop, Listener, ports[0], baudrate=500000)
    coro2 = serial_asyncio.create_serial_connection(loop, Listener, ports[1], baudrate=500000)
    transport1, listener = await coro1
    transport2, listener2 = await coro2
    listener.setup_listener(queue, q2, ports[0])
    listener2.setup_listener(queue, q2, ports[1])

# Packing frames in protobuf
def compress_frame_to_protobuf(frame):
    ret, compressed_frame = cv2.imencode(".jpg", frame)
    if not ret:
        raise ValueError("Failed to compress frame")
    
    compressed_image = CompressedImage()
    compressed_image.format = "jpeg"
    compressed_image.data = compressed_frame.tobytes()
    
    return compressed_image
    
async def open_camera(loop, device, formats):
    cap = None
    for fmt in formats:
        cap = await loop.run_in_executor(None, cv2.VideoCapture, device, cv2.CAP_V4L2)
        if not cap.isOpened():
            logger.error(f"Failed to open {device}")
            continue
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*fmt))
        if check_format(cap, fmt):
            logger.info(f"{device} opened successfully with {fmt}")
            return cap
        else:
            logger.error(f"Failed to set format {fmt} on {device}")
            cap.release()
    return None

def check_format(cap, fmt):
    actual_fmt = int(cap.get(cv2.CAP_PROP_FOURCC))
    return actual_fmt == cv2.VideoWriter_fourcc(*fmt)
    
# Webcam frame receiver
async def continuous_video_receiver(queue, q2):
    loop = asyncio.get_event_loop()
    #sudo rmmod uvcvideo
    #sudo modprobe uvcvideo nodrop=1 timeout=5000 quirks=0xC0
    formats = [('M', 'J', 'P', 'G')]

    cap = await open_camera(loop, "/dev/video1", formats)
    if not cap:
        cap = await open_camera(loop, "/dev/video0", formats)
        if not cap:
            logger.error("Failed to open any video device")

    while True:
        ret, frame = await loop.run_in_executor(None, cap.read)
        if not ret:
            logger.error("Failed to read frame from video capture device")
            continue
        
        try:
            compressed_image = compress_frame_to_protobuf(frame)
            if compressed_image:
                # Foxglove schemas names must match documentation!
                await queue.put(QueueData("foxglove.CompressedImage", compressed_image))
                await q2.put(QueueData("foxglove.CompressedImage", compressed_image))
            else:
                logger.error("Failed to compress frame")
        except Exception as e:
            logger.error(f"Error processing frame: {e}")


async def continuous_can_receiver(
    can_msg_decoder: cantools.db.Database, message_classes, queue, q2, can_bus
):
    loop = asyncio.get_event_loop()
    reader = can.AsyncBufferedReader()
    notifier = can.Notifier(can_bus, [reader], loop=loop)
    
    while True:
        # Wait for the next message from the buffer
        msg = await reader.get_message()

        # print("got msg")
        id = msg.arbitration_id
        try:
            decoded_msg = can_msg_decoder.decode_message(
                msg.arbitration_id, msg.data, decode_containers=True
            )
            # print("decoded msg")
            msg = can_msg_decoder.get_message_by_frame_id(msg.arbitration_id)
            # print("got msg by id")
            msg = pb_helpers.pack_protobuf_msg(
                decoded_msg, msg.name.lower(), message_classes
            )
            # print("created pb msg successfully")
            data = QueueData(msg.DESCRIPTOR.name, msg)
            await queue.put(data)
            await q2.put(data)
            


        except Exception as e:
            # print(id)
            # print(e)
            pass

    # Don't forget to stop the notifier to clean up resources.
    notifier.stop()


async def write_data_to_mcap(
    writer_cmd_queue: asyncio.Queue,
    writer_status_queue: asyncio.Queue,
    data_queue: asyncio.Queue,
    mcap_writer: HTPBMcapWriter,
    write_on_init: bool,
):
    writing = write_on_init
    async with mcap_writer as mcw:
        while True:
            response_needed = False
            if not writer_cmd_queue.empty():
                cmd_msg = writer_cmd_queue.get_nowait()
                writing = cmd_msg.writing
                response_needed = True

            if writing:
                if response_needed:
                    await mcw.open_new_writer()
                    await writer_status_queue.put(MCAPServerStatusQueueData(True, mcw.actual_path))
                try:
                    await mcw.write_data(data_queue)
                except:
                    logger.info(data_queue)
                    logger.info('mcap write data error!')
            else:
                if response_needed:
                    await writer_status_queue.put(MCAPServerStatusQueueData(False, mcw.actual_path))
                    await mcw.close_writer()
                # still keep getting the msgs from queue so it doesnt fill up
                trash_msg = await data_queue.get()


async def fxglv_websocket_consume_data(queue, foxglove_server):
    async with foxglove_server as fz:
        while True:
            try: 
                logger.info(queue.qsize())
                await fz.send_msgs_from_queue(queue)
            except:
                logger.info("fxglv error write data")


async def run(logger):
    # for example, we will have CAN as our only input as of right now but we may need to add in
    # a sensor that inputs over UART or ethernet
    
    can_interface = find_can_interface()

    if can_interface:
        print(f"Found CAN interface: {can_interface}")
        try:
            # Attempt to initialize the CAN bus
            bus = can.interface.Bus(channel=can_interface, bustype="socketcan")
            print(f"Successfully initialized CAN bus on {can_interface}")
            # Interface exists and bus is initialized, but this doesn't ensure the interface is 'up'
        except can.CanError as e:
            print(f"Failed to initialize CAN bus on {can_interface}: {e}")
    else:
        print("defaulting to using virtual can interface vcan0")
        bus = can.Bus(
            channel=UdpMulticastBus.DEFAULT_GROUP_IPv6, interface="udp_multicast"
        )
    
    queue = asyncio.Queue()
    queue2 = asyncio.Queue()
    path_to_bin = ""
    path_to_dbc = ""

    if len(sys.argv) > 2:
        path_to_bin = sys.argv[1]
        path_to_dbc = sys.argv[2]
    else:
        path_to_bin = os.environ.get("BIN_PATH")
        path_to_dbc = os.environ.get("DBC_PATH")

    full_path = os.path.join(path_to_bin, "hytech.bin")
    full_path_to_dbc = os.path.join(path_to_dbc, "hytech.dbc")
    db = cantools.db.load_file(full_path_to_dbc)

    list_of_msg_names, msg_pb_classes = pb_helpers.get_msg_names_and_classes()

    fx_s = HTProtobufFoxgloveServer(
        "0.0.0.0", 8765, "hytech-foxglove", full_path, list_of_msg_names
    )
    path_to_mcap = "."
    if os.path.exists("/etc/nixos"):
        logger.info("detected running on nixos")
        path_to_mcap = "/home/nixos/recordings"

    init_writing_on_start = True
    mcap_writer_status_queue = asyncio.Queue(maxsize=1)
    mcap_writer_cmd_queue = asyncio.Queue(maxsize=1)
    mcap_writer = HTPBMcapWriter(path_to_mcap, init_writing_on_start)
    mcap_web_server = MCAPServer(
        writer_command_queue=mcap_writer_cmd_queue,
        writer_status_queue=mcap_writer_status_queue,
        init_writing=init_writing_on_start,
        init_filename=mcap_writer.actual_path
    )
    logger.info("mcao")
    #receiver_task = asyncio.create_task(
    #        continuous_can_receiver(db, msg_pb_classes, queue, queue2, bus)                      
    #)

    #testing these two tasks
    aero_receiver_task = asyncio.create_task(continuous_aero_receiver(queue, queue2))
    #video_task = asyncio.create_task(continuous_video_receiver(queue, queue2))

    fx_task = asyncio.create_task(fxglv_websocket_consume_data(queue, fx_s))
    mcap_task = asyncio.create_task(write_data_to_mcap(mcap_writer_cmd_queue, mcap_writer_status_queue, queue2, mcap_writer, init_writing_on_start))
    srv_task = asyncio.create_task(mcap_web_server.start_server())
    logger.info("created tasks")
    # in the mcap task I actually have to deserialize the any protobuf msg into the message ID and
    # the encoded message for the message id. I will need to handle the same association of message id
    # and schema in the foxglove websocket server.

#edited tasks
    await asyncio.gather(aero_receiver_task, fx_task, mcap_task, srv_task)

if __name__ == "__main__":
    logging.basicConfig()
    logger = logging.getLogger("data_writer_service")
    logger.setLevel(logging.INFO)
    asyncio.run(run(logger))
