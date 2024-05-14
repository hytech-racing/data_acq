import asyncio
from google.protobuf.message import Message

class QueueData():
    def __init__(self, schema_name: str, msg: Message):
        self.name = schema_name
        self.data = msg.SerializeToString()
        self.pb_msg = msg

class MCAPServerStatusQueueData():
    def __init__(self, writing_status: bool, writing_file: str):
        self.is_writing = writing_status
        self.writing_file = writing_file 

class MCAPFileWriterCommand():
    def __init__(self, write: bool):
        self.writing = write

class SharedQueueManager:
    def __init__(self, param_update_event: asyncio.Event):
        """
        Initializes the SharedQueueManager with two asyncio queues.
        """
        self.mcap_recorder_queue = asyncio.Queue()
        self.foxglove_ws_queue = asyncio.Queue()
        self.param_msg_queue = asyncio.Queue()
        self.shared_param_event = param_update_event
        
    async def append_to_queues(self, queue_data: QueueData):
        """
        Asynchronously append the QueueData to both queues.
        
        :param queue_data: The QueueData object containing the protobuf message and its serialized form.
        """
        
        if(queue_data.pb_msg.HasField('config_')):
            print("got feedback")
            await self.param_msg_queue.put(QueueData(queue_data.pb_msg.config_.DESCRIPTOR.name, queue_data.pb_msg.config_))
            self.shared_param_event.set()    
        await self.mcap_recorder_queue.put(queue_data)
        await self.foxglove_ws_queue.put(queue_data)
    async def get_param_msg(self)-> QueueData:
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