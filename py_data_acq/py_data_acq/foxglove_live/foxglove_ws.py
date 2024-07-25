import asyncio

from py_data_acq.common.common_types import QueueData
from typing import Any

from foxglove_websocket import run_cancellable

from foxglove_websocket.server import FoxgloveServer

from base64 import standard_b64encode
import time


from base64 import b64encode
import google.protobuf.message
from typing import Set, Type
from foxglove_schemas_protobuf.CompressedImage_pb2 import CompressedImage
from foxglove_schemas_protobuf import CompressedImage_pb2 
from google.protobuf.descriptor_pb2 import FileDescriptorSet
from google.protobuf.descriptor import FileDescriptor
from google.protobuf.message import Message


from aero_sensor_protos_np_proto_py.aero_sensor import aero_sensor_pb2
from aero_sensor_protos_np_proto_py.aero_sensor.aero_sensor_pb2 import aero_data

#WRONG import!
#from aero_sensor_protos_np_proto_py.aero_sensor_pb2 import aero_data

# what I want to do with this class is extend the foxglove server to make it where it creates a protobuf schema
# based foxglove server that serves data from an asyncio queue.

# Make proto file descriptor
def build_file_descriptor_set(
    message_class: Type[google.protobuf.message.Message],
) -> FileDescriptorSet:
    """
    Build a FileDescriptorSet representing the message class and its dependencies.
    """
    file_descriptor_set = FileDescriptorSet()
    seen_dependencies: Set[str] = set()

    def append_file_descriptor(file_descriptor: FileDescriptor):
        for dep in file_descriptor.dependencies:
            if dep.name not in seen_dependencies:
                seen_dependencies.add(dep.name)
                append_file_descriptor(dep)
        file_descriptor.CopyToProto(file_descriptor_set.file.add())  # type: ignore

    append_file_descriptor(message_class.DESCRIPTOR.file)
    return file_descriptor_set

class HTProtobufFoxgloveServer(FoxgloveServer):
    def __init__(self, host: str, port: int, name: str, pb_bin_file_path: str, schema_names: list[str]):
        super().__init__(host, port, name)
        self.path = pb_bin_file_path
        self.schema_names = schema_names
        self.schema = standard_b64encode(open(pb_bin_file_path, "rb").read()).decode("ascii")
        self.chan_id_dict = {}
        self.filepath = pb_bin_file_path
        
    # this is run when we use this in a with statement for context management
    
    
    async def __aenter__(self): 
        await super().__aenter__()
        # TODO add channels for all of the msgs that are in the protobuf schema!
        for name in self.schema_names:
            self.chan_id_dict[name] = await super().add_channel(
            {
                "topic": name +"_data",
                "encoding": "protobuf",
                "schemaName": name,
                "schema": self.schema,
            }
        )
        # Adding schema to channel example
        '''self.chan_id_dict["foxglove.CompressedImage"] = await super().add_channel(
            {
                "topic": CompressedImage.DESCRIPTOR.name,
                "encoding": "protobuf",
                "schemaName": "foxglove.CompressedImage",
                "schema": b64encode(
                    build_file_descriptor_set(CompressedImage).SerializeToString()
                ).decode("ascii"),
                "schemaEncoding": "protobuf",
            }
        ) ''' 
        self.chan_id_dict["aero_data_ttyACM0"]  = await super().add_channel(
            {
                "topic": "aero_data_ttyACM0_data",
                "encoding": "protobuf",
                "schemaName": "aero_sensor.aero_data",
                "schema": b64encode(
                    build_file_descriptor_set(aero_data).SerializeToString()
                ).decode("ascii"),
                "schemaEncoding": "protobuf",
            }
        )
        self.chan_id_dict["aero_data_ttyACM1"]  = await super().add_channel(
            {
                "topic": "aero_data_ttyACM1_data",
                "encoding": "protobuf",
                "schemaName": "aero_sensor.aero_data",
                "schema": b64encode(
                    build_file_descriptor_set(aero_data).SerializeToString()
                ).decode("ascii"),
                "schemaEncoding": "protobuf",
            }
        )

        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, traceback: Any):
        return await super().__aexit__(exc_type, exc_val, traceback)

    async def send_msgs_from_queue(self, queue: asyncio.Queue[QueueData]):
        try:
            data = await queue.get()
            if data is not None:
                # send data to channel
                await super().send_message(self.chan_id_dict[data.name + data.portname], time.time_ns(), data.data)
        except asyncio.CancelledError:
            pass
