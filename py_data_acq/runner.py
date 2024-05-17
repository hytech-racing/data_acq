#!/usr/bin/env python
from py_data_acq.interfaces.interface_producer import InterfaceProducer
from py_data_acq.interfaces.interface_consumer import InterfaceConsumer
from py_data_acq.data_writers.data_writers import DataConsumer
from py_data_acq.common.protobuf_helpers import get_msg_names_and_classes
from py_data_acq.web_server.web_app_v2 import WebApp
import sys
import os
import can
from can.interfaces.udp_multicast import UdpMulticastBus
import cantools
import threading
import queue


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
        path_to_eth_bin = sys.argv[3]
    else:
        path_to_bin = os.environ.get("BIN_PATH")
        path_to_dbc = os.environ.get("DBC_PATH")
        path_to_eth_bin = os.environ.get("HT_ETH_BIN_PATH")

    full_path_to_bin = os.path.join(path_to_bin, "hytech.bin")
    path_to_eth_bin = os.path.join(path_to_eth_bin, "ht_eth.bin")
    full_path_to_dbc = os.path.join(path_to_dbc, "hytech.dbc")
    db = cantools.db.load_file(full_path_to_dbc)

    list_of_msg_names, msg_pb_classes = get_msg_names_and_classes()

    producer_manager = InterfaceProducer(db, msg_pb_classes, bus)
    consumer_queue = producer_manager.output_queue
    webapp_consumer_queue = producer_manager.config_output_queue
    webapp_mcap_writer_command_queue = queue.Queue()  # command queue to the mcap writer
    mcap_writer_feedback_queue = (
        queue.Queue()
    )  # feedback queue from the mcap writer about status / file names
    webapp_output_queue = (
        queue.Queue()
    )  # webapp message queue for outputting commands directly over the UDP consumer interface (config updates at first)
    # Start producer manager
    producer_manager.start()

    # Start consumer in another thread
    consumer = DataConsumer(
        ".",
        True,
        full_path_to_bin,
        path_to_eth_bin,
        webapp_mcap_writer_command_queue,
        consumer_queue,
        mcap_writer_feedback_queue,
    )
    web_app = WebApp(
        mcap_writer_feedback_queue,
        webapp_consumer_queue,
        webapp_mcap_writer_command_queue,
        webapp_output_queue,
        init_writing=True,
        init_filename=consumer.get_current_mcap_writer_filename(),
        host="127.0.0.1",
        port=8888,
    )

    output_consumer = InterfaceConsumer(webapp_output_queue, "127.0.0.1", 20002)
    msg_out_thread = threading.Thread(target=output_consumer.run)
    consumer_thread = threading.Thread(target=consumer.run)
    web_app_thread = threading.Thread(target=web_app.start_server)
    web_app_thread.start()
    consumer_thread.start()
    msg_out_thread.start()

    producer_manager.join()
    # consumer_queue.put(None)  # Signal consumer to stop
    consumer_thread.join()


if __name__ == "__main__":
    main()
