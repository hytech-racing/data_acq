import asyncio

import time
from mcap_protobuf.writer import Writer
from py_data_acq.common.common_types import QueueData, DataInputType, MCAPServerStatusQueueData
from datetime import datetime
from typing import Any, Optional, Set
import os
import queue


class HTPBMcapWriter:
    def __init__(self, mcap_base_path, init_writing: bool, status_output_queue: queue.Queue[MCAPServerStatusQueueData]):
        self.base_path = mcap_base_path
        self.status_output_queue = status_output_queue
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
        self.mcap_writer_class.finish()
        self.writing_file.close()

    def __aenter__(self):
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, traceback: Any):
        
        self.mcap_writer_class.finish()
        self.writing_file.close()

    async def close_writer(self):
        if self.is_writing:
            self.is_writing = False
            self.mcap_writer_class.finish()
            self.writing_file.close()

        return True

    async def open_new_writer(self):
        if not self.is_writing:
            now = datetime.now()
            date_time_filename = now.strftime("%m_%d_%Y_%H_%M_%S" + ".mcap")
            self.actual_path = os.path.join(self.base_path, date_time_filename)
            self.writing_file = open(self.actual_path, "wb")
            self.mcap_writer_class = Writer(self.writing_file)
            self.is_writing = True

        return True

    async def write_msg(self, msg, data_type: DataInputType):
        if self.is_writing:
            # print(msg)
            if data_type is DataInputType.CAN_DATA:
                self.mcap_writer_class.write_message(
                    topic="CAN/"+msg.DESCRIPTOR.name + "_data",
                    message=msg,
                    log_time=int(time.time_ns()),
                    publish_time=int(time.time_ns()),
                )
            if data_type is DataInputType.ETHERNET_DATA:
                self.mcap_writer_class.write_message(
                    topic="ETH/"+msg.DESCRIPTOR.name + "_data",
                    message=msg,
                    log_time=int(time.time_ns()),
                    publish_time=int(time.time_ns()),
                )
            self.writing_file.flush()
        else:
            print("not writing msg")
        if data_type is DataInputType.WEB_APP_DATA:
            print(msg)
            writing_command_input = msg.writing
            print("got cmd from web app ",msg)
            if writing_command_input:
                await self.open_new_writer()
                self.status_output_queue.put(MCAPServerStatusQueueData(True, self.actual_path))
            else:
                await self.close_writer()
                self.status_output_queue.put(MCAPServerStatusQueueData(False, self.actual_path))
            
        return True

    async def handle_data(self, queue):
        msg = await queue.get()
        if msg is not None:
            # print(msg.pb_msg)
            return await self.write_msg(msg.pb_msg, msg.data_type)
        else:
            print("error, not actually")
    async def consume(self, asyncio_msg_queue):
        async with self as writer:
            while True:
                await writer.handle_data(asyncio_msg_queue)