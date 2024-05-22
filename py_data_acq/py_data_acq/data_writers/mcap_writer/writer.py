import asyncio

import time
from mcap_protobuf.writer import Writer
from py_data_acq.common.common_types import QueueData, DataInputType, MCAPServerStatusQueueData
from datetime import datetime
from typing import Any, Optional, Set
import os
import queue
import threading


class HTPBMcapWriter(threading.Thread):
    def __init__(self, mcap_base_path, init_writing: bool, status_output_queue: queue.Queue[MCAPServerStatusQueueData], combined_msg_queue: queue.Queue[QueueData]):
        super().__init__()
        self.base_path = mcap_base_path
        self.status_output_queue = status_output_queue
        self.combined_msg_queue = combined_msg_queue
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

    def close_writer(self):
        if self.is_writing:
            self.is_writing = False
            self.mcap_writer_class.finish()
            self.writing_file.close()

        return True

    def open_new_writer(self):
        if not self.is_writing:
            now = datetime.now()
            date_time_filename = now.strftime("%m_%d_%Y_%H_%M_%S" + ".mcap")
            self.actual_path = os.path.join(self.base_path, date_time_filename)
            self.writing_file = open(self.actual_path, "wb")
            self.mcap_writer_class = Writer(self.writing_file)
            self.is_writing = True
        return True

    def write_msg(self, msg, data_type: DataInputType):
        if self.is_writing:
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
        
        if data_type is DataInputType.WEB_APP_DATA:
            
            writing_command_input = msg.writing
            
            if writing_command_input:
                self.open_new_writer()
                self.status_output_queue.put(MCAPServerStatusQueueData(True, self.actual_path))
            else:
                self.close_writer()
                self.status_output_queue.put(MCAPServerStatusQueueData(False, self.actual_path))
        return True
        
    def run(self):
        while True:
            print(self.combined_msg_queue.qsize())
            msg = self.combined_msg_queue.get()
            if msg is not None:
                return self.write_msg(msg.pb_msg, msg.data_type)