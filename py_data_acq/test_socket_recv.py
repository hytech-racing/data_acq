#!/usr/bin/env python

import socket
from hytech_eth_np_proto_py import ht_eth_pb2
import select
import time
def start_udp_server(ip, port, send_port):
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"UDP server listening on {ip}:{port}")
    current_config = ht_eth_pb2.config()
    current_config.AbsoluteTorqueLimit = 1.9
    try:
        while True:                
            send_union_msg = ht_eth_pb2.HT_ETH_Union()
            send_union_msg.config_.CopyFrom(current_config)
            
            send_sock.sendto(send_union_msg.SerializeToString(), ('127.0.0.1', send_port))
            time.sleep(0.2)
    finally:
        
        send_sock.close()

if __name__ == "__main__":
    start_udp_server('127.0.0.1', 20002, 20001)  # Use the correct IP and port
