from py_data_acq.interfaces.interface_producer import InterfaceProducer
from py_data_acq.common.protobuf_helpers import get_msg_names_and_classes
import sys
import os
import can
from can.interfaces.udp_multicast import UdpMulticastBus
import cantools
def find_can_interface():
    """Find a CAN interface by checking /sys/class/net/."""
    for interface in os.listdir("/sys/class/net/"):
        if interface.startswith("can"):
            return interface
    return None


def main():

    # for example, we will have CAN as our only input as of right now but we may need to add in
    # a sensor that inputs over UART or ethernet
    can_interface = find_can_interface()

    if can_interface:
        print(f"Found CAN interface: {can_interface}")
        try:
            # Attempt to initialize the CAN bus
            bus = can.interface.Bus(channel=can_interface, bustype="socketcan")
            print(f"Successfully initialized CAN bus on {can_interface}")
            # Interface exists and bus is initialized, but this doesn't ensure the interface is 'up'
        except can.CanError as e:
            print(f"Failed to initialize CAN bus on {can_interface}: {e}")
    else:
        print("defaulting to using virtual can interface vcan0")
        bus = can.Bus(
            channel=UdpMulticastBus.DEFAULT_GROUP_IPv6, interface="udp_multicast"
        )


    path_to_bin = ""
    path_to_dbc = ""

    if len(sys.argv) > 2:
        path_to_bin = sys.argv[1]
        path_to_dbc = sys.argv[2]
    else:
        path_to_bin = os.environ.get("BIN_PATH")
        path_to_dbc = os.environ.get("DBC_PATH")

    full_path = os.path.join(path_to_bin, "hytech.bin")
    full_path_to_dbc = os.path.join(path_to_dbc, "hytech.dbc")
    db = cantools.db.load_file(full_path_to_dbc)

    list_of_msg_names, msg_pb_classes = get_msg_names_and_classes()


    producer_manager = InterfaceProducer(db, msg_pb_classes, bus)
    consumer_queue = producer_manager.output_queue

    # Start producer manager
    producer_manager.start()

    # Start consumer in another thread
    # consumer = Consumer(consumer_queue)
    # consumer_thread = threading.Thread(target=consumer.consume)
    # consumer_thread.start()

    producer_manager.join()
    # consumer_queue.put(None)  # Signal consumer to stop
    # consumer_thread.join()

if __name__ == "__main__":
    main()