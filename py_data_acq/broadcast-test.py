#!/usr/bin/env python
import socket
import time
import can
from py_data_acq.common import protobuf_helpers
from can.interfaces.udp_multicast import UdpMulticastBus
import cantools
from pprint import pprint
import os, sys
from mcap_protobuf.reader import read_protobuf_messages
from hytech_np_proto_py import hytech_pb2

# Define the IP and port for the UDP socket
bus1 = can.interface.Bus(channel=UdpMulticastBus.DEFAULT_GROUP_IPv6, interface="udp_multicast")
# bus1 = can.Bus(channel="can0", interface='socketcan')
def main():
    path_to_dbc = os.environ.get('DBC_PATH')
    full_path = os.path.join(path_to_dbc, "hytech.dbc") 
    # Serialize the message to bytes
    db = cantools.database.load_file(full_path)
    while(1):
        try:
            for msg in read_protobuf_messages(sys.argv[1], log_time_order=True):
                # print(f"{msg.topic}: {msg.proto_msg}")
                # print(msg.topic[:-5])
                can_msg, can_msg_data = protobuf_helpers.pack_cantools_msg(msg.proto_msg, msg.topic[:-5], db)
                msg_out = can.Message(arbitration_id=can_msg.frame_id, is_extended_id=False, data=can_msg_data)
                bus1.send(msg_out)
                # time.sleep(0.00001)
                # print("Message sent on {}".format(bus1.channel_info))
        except can.CanError:
            print("Message NOT sent!  Please verify can0 is working first")

if __name__ == "__main__":
    main()
