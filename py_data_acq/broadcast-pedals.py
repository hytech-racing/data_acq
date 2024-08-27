#!/usr/bin/env python
import socket
import time
import can
from can.interfaces.udp_multicast import UdpMulticastBus
import cantools
from pprint import pprint
import os

from hytech_np_proto_py import hytech_pb2

# Define the IP and port for the UDP socket
# bus1 = can.interface.Bus(channel=UdpMulticastBus.DEFAULT_GROUP_IPv6, interface="udp_multicast")
bus1 = can.Bus(channel="vcan0", interface='socketcan')
def main():
    path_to_dbc = os.environ.get('DBC_PATH')
    full_path = os.path.join(path_to_dbc, "hytech.dbc") 
    # Serialize the message to bytes
    db = cantools.database.load_file(full_path)
 
    msg = db.get_message_by_name("MCU_PEDAL_READINGS")
    # rpm = db.get_message_by_name("MC4_SETPOINTS_COMMAND")
    data = msg.encode({'accel_percent_float': 100.0, 'brake_percent_float': 0.0, 'mechanical_brake_percent_float': 40.0})
    
    can_msg = can.Message(arbitration_id=msg.frame_id, is_extended_id=False, data=data)
    while(1):
        try:
            bus1.send(can_msg)
            print("Message sent on {}".format(bus1.channel_info))
        except can.CanError:
            print("Message NOT sent!  Please verify can0 is working first")
        time.sleep(0.001)

if __name__ == "__main__":
    main()
