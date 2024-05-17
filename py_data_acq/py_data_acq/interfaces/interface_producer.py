import asyncio
import threading
import queue
import cantools

import threading
import can


from py_data_acq.common.protobuf_helpers import pack_protobuf_msg
from py_data_acq.common.common_types import QueueData, DataInputType
from hytech_eth_np_proto_py import ht_eth_pb2

class UDPServerProtocol:
    def __init__(self, output_queue: queue.Queue[QueueData], config_output_queue: queue.Queue[QueueData]):
        self.output_queue = output_queue
        self.config_output_queue = config_output_queue
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        union_msg = ht_eth_pb2.HT_ETH_Union()
        message = union_msg.ParseFromString(data)

        try:
            for field_desc, value in union_msg.ListFields():
                # Check if the field is a composite message
                if field_desc.message_type is not None:
                    # Get the composite message from the populated field
                    composite_msg = getattr(union_msg, field_desc.name)
                    queue_data = QueueData(composite_msg.DESCRIPTOR.name, composite_msg, DataInputType.ETHERNET_DATA)
                    print(f"Received message from {addr}: {message}")
                    if composite_msg.DESCRIPTOR.name == 'config':
                        print('got response config msg')
                        self.config_output_queue.put(queue_data)
                    self.output_queue.put(queue_data)
        except Exception as e:
            # print(id)
            print(e)
            pass


class UDPInterface:
    def __init__(self, output_queue: queue.Queue[QueueData], config_output_queue: queue.Queue[QueueData], recv_ip: str, recv_port: int):
        self.output_queue = output_queue
        self.config_output_queue = config_output_queue
        self.recv_ip = recv_ip
        self.recv_port = recv_port
    async def produce(self):
        # Creating a UDP server to receive data
        transport, protocol = await asyncio.get_event_loop().create_datagram_endpoint(
            lambda: UDPServerProtocol(self.output_queue, self.config_output_queue),
            local_addr=(self.recv_ip, self.recv_port)
        )
        try:
            # Run until producer task is cancelled
            await asyncio.Event().wait()
        finally:
            transport.close()


class CANInterface:
    def __init__(self, can_msg_decoder: cantools.db.Database, message_classes, queue: queue.Queue[QueueData], can_bus):
        self.can_msg_decoder = can_msg_decoder
        self.message_classes = message_classes
        self.out_queue = queue
        self.can_bus = can_bus

    async def produce(self):
        loop = asyncio.get_event_loop()
        reader = can.AsyncBufferedReader()
        notifier = can.Notifier(self.can_bus, [reader], loop=loop)

        while True:
            # Wait for the next message from the buffer
            msg = await reader.get_message()
            # print("got msg")
            id = msg.arbitration_id
            try:
                decoded_msg = self.can_msg_decoder.decode_message(
                    msg.arbitration_id, msg.data, decode_containers=True
                )
                print("decoded CAN msg")
                msg = self.can_msg_decoder.get_message_by_frame_id(msg.arbitration_id)
                # print("got msg by id")
                msg = pack_protobuf_msg(
                    decoded_msg, msg.name.lower(), self.message_classes
                )
                # print("created pb msg successfully")
                data = QueueData(msg.DESCRIPTOR.name, msg, DataInputType.CAN_DATA)
                self.out_queue.put(data)
                
            except Exception as e:
                # print(id)
                # print(e)
                pass

        # Don't forget to stop the notifier to clean up resources.
        notifier.stop()

class InterfaceProducer(threading.Thread):
    def __init__(self, can_msg_db: cantools.db.Database, message_classes, can_bus, recv_ip, recv_port):
        super().__init__()
        self.output_queue = queue.Queue()
        self.config_output_queue = queue.Queue()
        self.can_interface_producer = CANInterface(can_msg_db, message_classes, self.output_queue, can_bus)
        self.udp_interface_producer = UDPInterface(self.output_queue, self.config_output_queue, recv_ip, recv_port)

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tasks = [
            asyncio.ensure_future(self.udp_interface_producer.produce()),
            asyncio.ensure_future(self.can_interface_producer.produce())
        ]
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()