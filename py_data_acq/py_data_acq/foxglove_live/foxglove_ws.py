import asyncio

from py_data_acq.common.common_types import QueueData
from typing import Any

from foxglove_websocket import run_cancellable

from foxglove_websocket.server import FoxgloveServer

from base64 import standard_b64encode
import time
from aero_sensor_protos_np_proto_py.aero_sensor import aero_sensor_pb2
from foxglove_schemas_protobuf.CompressedImage_pb2 import CompressedImage

# what I want to do with this class is extend the foxglove server to make it where it creates a protobuf schema
# based foxglove server that serves data from an asyncio queue.
class HTProtobufFoxgloveServer(FoxgloveServer):
    def __init__(self, host: str, port: int, name: str, pb_bin_file_path: str, schema_names: list[str]):
        super().__init__(host, port, name)
        self.path = pb_bin_file_path
        self.schema_names = schema_names
        self.schema = standard_b64encode(open(pb_bin_file_path, "rb").read()).decode("ascii")
        self.chan_id_dict = {}
        
    # this is run when we use this in a with statement for context management
    async def __aenter__(self): 
        await super().__aenter__()
        # TODO add channels for all of the msgs that are in the protobuf schema
        for name in self.schema_names:
            if name == "aero_data_ttyACM0" or name == "aero_data_ttyACM1":
                schema_encoded = standard_b64encode(aero_sensor_pb2.DESCRIPTOR.serialized_pb).decode("ascii")
                self.chan_id_dict[name] = await super().add_channel(
                {
                    "topic": name + "_data",
                    "encoding": "protobuf",
                    "schemaName": "aero_data",
                    "schema": schema_encoded,
                }
            )
            elif name == "CompressedImage":
                schema_encoded = standard_b64encode(CompressedImage.DESCRIPTOR.serialized_pb).decode("ascii")
                self.chan_id_dict[name] = await super().add_channel(
                {
                    "topic": name + "_data",
                    "encoding": "protobuf",
                    "schemaName": name,
                    "schema": schema_encoded,
                }
            )
            else:
                self.chan_id_dict[name] = await super().add_channel(
                {
                    "topic": name +"_data",
                    "encoding": "protobuf",
                    "schemaName": name,
                    "schema": self.schema,
                }
            )
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, traceback: Any):
        return await super().__aexit__(exc_type, exc_val, traceback)

    async def send_msgs_from_queue(self, queue: asyncio.Queue[QueueData]):
        try:
            print("waiting for data")
            data = await queue.get()
            
            if data is not None:
                print("Data received")
                await super().send_message(self.chan_id_dict[data.name], time.time_ns(), data.data)
                print("send data success")
        except asyncio.CancelledError:
            pass
