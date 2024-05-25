import asyncio

from py_data_acq.common.common_types import QueueData, DataInputType
from py_data_acq.common.protobuf_helpers import get_oneof_msg_names_and_classes
from typing import Any

from foxglove_websocket import run_cancellable
from foxglove_websocket.types import ChannelId
from foxglove_websocket.server import FoxgloveServer, FoxgloveServerListener
import threading
from base64 import standard_b64encode
import time
import queue

# what I want to do with this class is extend the foxglove server to make it where it creates a protobuf schema
# based foxglove server that serves data from an asyncio queue.
class Listener(FoxgloveServerListener):
    async def on_subscribe(self, server: FoxgloveServer, channel_id: ChannelId):
        print("First client subscribed to", channel_id)
    async def on_unsubscribe(self, server: FoxgloveServer, channel_id: ChannelId):
        print("Last client unsubscribed from", channel_id)


class HTProtobufFoxgloveServer(threading.Thread):
    def __init__(self, host: str, port: int, name: str, pb_bin_file_path: str, path_to_eth_bin: str, can_pb_msg_schema_names: list[str], msg_input_queue: queue.Queue[QueueData]):
        super().__init__()
        self.host = host
        self.port = port
        self.name = name
        self.path = pb_bin_file_path
        self.can_pb_msg_schema_names = can_pb_msg_schema_names
        eth_pb_names, eth_pb_classes = get_oneof_msg_names_and_classes()
        self.eth_pb_msg_schema_names =  eth_pb_names
        self.can_bin_schema = standard_b64encode(open(pb_bin_file_path, "rb").read()).decode("ascii")
        self.eth_bin_schema = standard_b64encode(open(path_to_eth_bin, "rb").read()).decode("ascii")
        self.can_chan_id_dict = {}
        self.eth_chan_id_dict = {}
        self.msg_input_queue = msg_input_queue
        
    # async def setup_foxglove_server(self, fxglv_server):
        
    #     for name in self.can_pb_msg_schema_names:
    #         self.can_chan_id_dict[name] = await fxglv_server.add_channel(
    #         {
    #             "topic": "CAN/"+name +"_data",
    #             "encoding": "protobuf",
    #             "schemaName": "hytech."+name,
    #             "schema": self.can_bin_schema,
    #         }
    #     )
    #     for name in self.eth_pb_msg_schema_names:
    #         self.eth_chan_id_dict[name] = await fxglv_server.add_channel(
    #         {
    #             "topic": "ETH/"+name +"_data",
    #             "encoding": "protobuf",
    #             "schemaName": name,
    #             "schema": self.eth_bin_schema,
    #         }
    #     )
            
    async def send_msgs_from_queue(self, fxglv_server):
        try:
            data = self.msg_input_queue.get()
            if data is not None:
                if data.data_type is DataInputType.CAN_DATA:
                    await fxglv_server.send_message(self.can_chan_id_dict[data.name], time.time_ns(), data.data)
                if data.data_type is DataInputType.ETHERNET_DATA:
                    await fxglv_server.send_message(self.eth_chan_id_dict[data.name], time.time_ns(), data.data)
        except asyncio.CancelledError:
            pass

    async def consume(self):
            async with FoxgloveServer("0.0.0.0", 8765, "example server") as server:
                server.set_listener(Listener())
                for name in self.can_pb_msg_schema_names:
                    self.can_chan_id_dict[name] = await server.add_channel(
                    {
                        "topic": "CAN/"+name +"_data",
                        "encoding": "protobuf",
                        "schemaName": "hytech."+name,
                        "schema": self.can_bin_schema,
                    }
                )
                for name in self.eth_pb_msg_schema_names:
                    self.eth_chan_id_dict[name] = await server.add_channel(
                    {
                        "topic": "ETH/"+name +"_data",
                        "encoding": "protobuf",
                        "schemaName": name,
                        "schema": self.eth_bin_schema,
                    }
                )

                # i = 0
                
                while True:
                    await self.send_msgs_from_queue(server)
                    
                    # await self.send_msgs_from_queue(server)

    def run(self):
        print("yo running ws")
        with asyncio.Runner() as runner:
            runner.run(self.consume())

    