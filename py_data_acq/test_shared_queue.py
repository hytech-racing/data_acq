import asyncio
from google.protobuf import message_factory, descriptor_pool
import asyncio
from google.protobuf.message import Message
from typing import Any
from py_data_acq.common.common_types import QueueData, SharedQueueManager
from hytech_np_proto_py import hytech_pb2

class MessageProcessor:
    def __init__(self, queue_manager: SharedQueueManager, role: str, queue1_event, queue2_event):
        self.queue_manager = queue_manager
        self.role = role
        self.queue1_event = queue1_event
        self.queue2_event = queue2_event
        

    async def send_message(self, msg_id):
        example_message = hytech_pb2.em_measurement()
        example_message.em_current = msg_id
        example_message.em_voltage = msg_id
        queue_data = QueueData(example_message.DESCRIPTOR.name, example_message)
        await self.queue_manager.append_to_queues(queue_data)
        self.queue1_event.set()
        self.queue2_event.set()
        print(f"Message with ID {msg_id} sent!")

    async def process_queue1(self):
        while True:
            print("yo reading")
            await asyncio.sleep(1.12) # simulating doing somethin
            await self.queue1_event.wait()  # Wait until there's something in the queue
            while not self.queue_manager.mcap_recorder_queue.empty():
                data = await self.queue_manager.get_from_mcap_recorder_queue()
                print(f"Processed from queue1: Current {data.pb_msg.em_current}, Voltage {data.pb_msg.em_voltage}")
            self.queue1_event.clear()  # Reset event until new data arrives

    async def process_queue2(self):
        while True:
            print("Waiting for items in queue1...")
            await asyncio.sleep(1.4) # simulating doing somethin
            await self.queue2_event.wait()  # Wait until there's something in the queue
            while not self.queue_manager.foxglove_ws_queue.empty():
                data = await self.queue_manager.get_from_foxglove_ws_queue()
                print(f"Processed from queue2: Current {data.pb_msg.em_current}, Voltage {data.pb_msg.em_voltage}")
            self.queue2_event.clear()  # Reset event until new data arrives

    async def run(self):
        if self.role == "sender":
            msg_id = 0
            while True:
                await self.send_message(msg_id)
                msg_id += 1
                await asyncio.sleep(0.1)  # Simulate interval between sends
        elif self.role == "reader1":
            await self.process_queue1()
        elif self.role == "reader2":
            await self.process_queue2()

async def main():
    manager = SharedQueueManager()
    # Create 2 senders and 3 readers
    mcap_recorder_event = asyncio.Event()
    foxglove_ws_event = asyncio.Event()
    sender1 = MessageProcessor(manager, "sender", mcap_recorder_event, foxglove_ws_event)
    sender2 = MessageProcessor(manager, "sender", mcap_recorder_event, foxglove_ws_event)
    reader1 = MessageProcessor(manager, "reader1", mcap_recorder_event, foxglove_ws_event)
    reader2 = MessageProcessor(manager, "reader2", mcap_recorder_event, foxglove_ws_event)

    # Run all processors concurrently
    await asyncio.gather(
        sender1.run(),
        sender2.run(),
        reader1.run(),
        reader2.run()
    )
if __name__ == "__main__":
    asyncio.run(main())
