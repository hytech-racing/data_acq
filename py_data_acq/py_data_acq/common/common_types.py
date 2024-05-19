import asyncio
from google.protobuf.message import Message
from enum import Enum

# need this to see which bin / schema to put into the 
class DataInputType(Enum):
    CAN_DATA = 1
    ETHERNET_DATA = 2
    WEB_APP_DATA = 3

class QueueData:
    def __init__(self, schema_name: str, msg: Message, data_type: DataInputType):
        self.name = schema_name
        self.data = msg.SerializeToString()
        self.pb_msg = msg
        self.data_type = data_type

class MCAPServerStatusQueueData:
    def __init__(self, writing_status: bool, writing_file: str):
        self.is_writing = writing_status
        self.writing_file = writing_file

class SharedQueueManager:
    def __init__(self, param_update_event: asyncio.Event):
        """
        Initializes the SharedQueueManager with two asyncio queues.
        """
        self.mcap_recorder_queue = asyncio.Queue()
        self.foxglove_ws_queue = asyncio.Queue()
        self.param_msg_queue = asyncio.Queue(maxsize=1)
        self.shared_param_event = param_update_event

    def param_queue_has_data(self):
        return not self.param_msg_queue.empty()

    async def append_to_queues(self, queue_data: QueueData):
        """
        Asynchronously append the QueueData to both queues.

        :param queue_data: The QueueData object containing the protobuf message and its serialized form.
        """

        if queue_data.pb_msg.HasField("config_"):
            await self.param_msg_queue.put(
                QueueData(
                    queue_data.pb_msg.config_.DESCRIPTOR.name, queue_data.pb_msg.config_
                )
            )
            self.shared_param_event.set()
        await self.mcap_recorder_queue.put(queue_data)
        await self.foxglove_ws_queue.put(queue_data)

    async def get_param_msg(self) -> QueueData:
        return await self.param_msg_queue.get()

    async def get_from_mcap_recorder_queue(self) -> QueueData:
        """
        Asynchronously get an item from mcap_recorder_queue.

        :return: QueueData object from mcap_recorder_queue.
        """
        return await self.mcap_recorder_queue.get()

    async def get_from_foxglove_ws_queue(self) -> QueueData:
        """
        Asynchronously get an item from foxglove_ws_queue.

        :return: QueueData object from foxglove_ws_queue.
        """
        return await self.foxglove_ws_queue.get()
