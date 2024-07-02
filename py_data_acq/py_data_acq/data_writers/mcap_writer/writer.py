import cv2
import asyncio
import time
import os
from datetime import datetime
from typing import Any, Optional, Set
from mcap_protobuf.writer import Writer


from foxglove_schemas_protobuf.CompressedImage_pb2 import CompressedImage
 
class HTPBMcapWriter:
    def __init__(self, mcap_base_path, init_writing: bool):
        self.base_path = mcap_base_path
        self.video_capture = cv2.VideoCapture(0)
        if init_writing:
            now = datetime.now()
            date_time_filename = now.strftime("%m_%d_%Y_%H_%M_%S" + ".mcap")
            self.actual_path = os.path.join(mcap_base_path, date_time_filename)
            self.writing_file = open(self.actual_path, "wb")
            self.mcap_writer_class = Writer(self.writing_file)
            self.is_writing = True
            
        else:
            self.is_writing = False
            self.actual_path = None
            self.writing_file = None
            self.mcap_writer_class = None
 
    def __await__(self):
        async def closure():
            print("await")
            return self
 
        return closure().__await__()
 
    def __enter__(self):
        return self
 
    def __exit__(self, exc_, exc_type_, tb_):
        self.close_writer()
 
    def __aenter__(self):
        return self
 
    async def __aexit__(self, exc_type: Any, exc_val: Any, traceback: Any):
        self.close_writer()
 
    async def close_writer(self):
        if self.is_writing:
            self.is_writing = False
            self.mcap_writer_class.finish()
            self.writing_file.close()
 
    async def open_new_writer(self):
        if self.is_writing:
            self.close_writer()
 
        now = datetime.now()
        date_time_filename = now.strftime("%m_%d_%Y_%H_%M_%S" + ".mcap")
        self.actual_path = os.path.join(self.base_path, date_time_filename)
        self.writing_file = open(self.actual_path, "wb")
        self.mcap_writer_class = Writer(self.writing_file)
        self.is_writing = True
 
   
     async def write_video_msg(self):
         while True:
            ret, frame = self.video_capture.read()
            if not ret:
                break
            compressed_image = self.compress_frame_to_protobuf(frame)
            await self.mcap_writer_class.write_message(
                topic=compressed_image.DESCRIPTOR.name + "_data",
                message=compressed_image,
                log_time=int(time.time_ns()),
                publish_time=int(time.time_ns()),
            )
            await asyncio.sleep(0)

    def compress_frame_to_protobuf(self, frame):
        ret, compressed_frame = cv2.imencode(".jpg", frame)
        if not ret:
            raise ValueError("Failed to compress frame")
        compressed_image = CompressedImage()
        compressed_image.format = "jpeg"
        compressed_image.data = compressed_frame.tobytes()
        return compressed_image
    async def write_msg(self, msg):
        if self.is_writing:
            self.mcap_writer_class.write_message(
                topic=msg.DESCRIPTOR.name + "_data",
                message=msg,
                log_time=int(time.time_ns()),
                publish_time=int(time.time_ns()),
            )
            self.writing_file.flush()
 
    async def write_data(self, queue):
        await self.write_video_msg()
        msg = await queue.get()
        if msg is not None:
            await self.write_msg(msg.pb_msg)
 
