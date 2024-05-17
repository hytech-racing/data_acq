import asyncio

from py_data_acq.common.common_types import QueueData, DataInputType
from py_data_acq.common.protobuf_helpers import get_oneof_msg_names_and_classes
from typing import Any

from foxglove_websocket import run_cancellable

from foxglove_websocket.server import FoxgloveServer

from base64 import standard_b64encode
import time


# what I want to do with this class is extend the foxglove server to make it where it creates a protobuf schema
# based foxglove server that serves data from an asyncio queue.
class HTProtobufFoxgloveServer(FoxgloveServer):
    def __init__(self, host: str, port: int, name: str, pb_bin_file_path: str, path_to_eth_bin: str, can_pb_msg_schema_names: list[str]):
        super().__init__(host, port, name)
        self.path = pb_bin_file_path
        self.can_pb_msg_schema_names = can_pb_msg_schema_names
        eth_pb_names, eth_pb_classes = get_oneof_msg_names_and_classes()
        self.eth_pb_msg_schema_names =  eth_pb_names
        self.can_bin_schema = standard_b64encode(open(pb_bin_file_path, "rb").read()).decode("ascii")
        self.eth_bin_schema = standard_b64encode(open(path_to_eth_bin, "rb").read()).decode("ascii")
        self.can_chan_id_dict = {}
        self.eth_chan_id_dict = {}
        
    # this is run when we use this in a with statement for context management
    async def __aenter__(self):
        await super().__aenter__()
        # TODO add channels for all of the msgs that are in the protobuf schema
        for name in self.can_pb_msg_schema_names:
            self.can_chan_id_dict[name] = await super().add_channel(
            {
                "topic": "CAN/"+name +"_data",
                "encoding": "protobuf",
                "schemaName": name,
                "schema": self.can_bin_schema,
            }
        )
        for name in self.eth_pb_msg_schema_names:
            self.eth_chan_id_dict[name] = await super().add_channel(
            {
                "topic": "ETH/"+name +"_data",
                "encoding": "protobuf",
                "schemaName": name,
                "schema": self.eth_bin_schema,
            }
        )
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, traceback: Any):
        return await super().__aexit__(exc_type, exc_val, traceback)
    
    async def send_msgs_from_queue(self, queue: asyncio.Queue[QueueData]):
        try:
            data = await queue.get()
            if data is not None:
                # print(data)
                if data.data_type is DataInputType.CAN_DATA:
                    await super().send_message(self.can_chan_id_dict[data.name], time.time_ns(), data.data)
                if data.data_type is DataInputType.ETHERNET_DATA:
                    await super().send_message(self.eth_chan_id_dict[data.name], time.time_ns(), data.data)
        except asyncio.CancelledError:
            pass

    async def consume(self, input_queue):
        async with self as fz:
            while True:
                await fz.send_msgs_from_queue(input_queue)