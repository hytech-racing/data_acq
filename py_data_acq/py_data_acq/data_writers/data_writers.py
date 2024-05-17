import threading
import time
from mcap_protobuf.writer import Writer
from datetime import datetime
from typing import Any, Optional, Set
import os
import queue
import asyncio

from py_data_acq.data_writers.foxglove_live.foxglove_ws import HTProtobufFoxgloveServer
from py_data_acq.data_writers.mcap_writer.writer import HTPBMcapWriter
from py_data_acq.common.common_types import QueueData, MCAPServerStatusQueueData
from py_data_acq.common.protobuf_helpers import get_msg_names_and_classes


class DataConsumer(threading.Thread):
    def __init__(
        self,
        mcap_base_path: str,
        init_mcap_writer_writing: bool,
        path_to_pb_pin: str,
        path_to_eth_bin: str,
        web_app_queue: queue.Queue[QueueData],
        pb_message_queue: queue.Queue[QueueData],
        mcap_writer_feedback_queue: queue.Queue[MCAPServerStatusQueueData],
    ):
        super().__init__()
        self.web_app_queue = web_app_queue
        self.pb_message_queue = pb_message_queue
        # self.sync_event = threading.Event()
        self.path_to_pb_pin = path_to_pb_pin
        self.path_to_eth_bin = path_to_eth_bin

        list_of_msg_names, msg_pb_classes = get_msg_names_and_classes()
        self.list_of_msg_names = list_of_msg_names
        self.mcap_writer = HTPBMcapWriter(
            mcap_base_path,
            init_mcap_writer_writing,
            status_output_queue=mcap_writer_feedback_queue
        )

        # Create two asyncio queues
        self.mcap_msg_queue_copy = asyncio.Queue()
        self.foxglove_msg_queue_copy = asyncio.Queue()
    def get_current_mcap_writer_filename(self):
        return self.mcap_writer.actual_path

    async def copy_pb_msg_queue_to_asyncio_queue(self):
        loop = asyncio.get_running_loop()
        while True:
            print("copying pb message data to the queues")
            item = await loop.run_in_executor(None, self.pb_message_queue.get)
            print("copied pb data")
            await self.mcap_msg_queue_copy.put(item)
            await self.foxglove_msg_queue_copy.put(item)
            self.pb_message_queue.task_done()

    async def copy_web_app_queue_asyncio_queue(self):
        loop = asyncio.get_running_loop()
        while True:
            print("copying web app data to the queues")
            item = await loop.run_in_executor(None, self.web_app_queue.get)
            print("copied web app data")
            await self.mcap_msg_queue_copy.put(item)
            await self.foxglove_msg_queue_copy.put(item)
            self.web_app_queue.task_done()

    async def run_consumer_tasks(self):
        fx_s = HTProtobufFoxgloveServer(
            "0.0.0.0",
            8765,
            "hytech-foxglove",
            self.path_to_pb_pin,
            self.path_to_eth_bin,
            self.list_of_msg_names,
        )
        await asyncio.gather(
            self.mcap_writer.consume(self.mcap_msg_queue_copy),
            fx_s.consume(self.foxglove_msg_queue_copy),
        )

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Start copying data to asyncio queues and consuming tasks
        asyncio.ensure_future(self.copy_pb_msg_queue_to_asyncio_queue())
        asyncio.ensure_future(self.copy_web_app_queue_asyncio_queue())
        loop.run_until_complete(self.run_consumer_tasks())
        loop.close()
