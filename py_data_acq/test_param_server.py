#!/usr/bin/env python

import socket
from hytech_eth_np_proto_py import ht_eth_pb2
import select
import time
def start_udp_server(ip, recv_port, send_port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((ip, recv_port))
    # send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"UDP server listening on {ip}:{recv_port}")
    current_config = ht_eth_pb2.config()
    CASE_msg= ht_eth_pb2.CASE_msg()
    CASE_msg.vehm_fl_slip = 6969.3
    try:
        while True:
            ready = select.select([server_socket], [], [])
            if ready[0]:
                data, addr = server_socket.recvfrom(1024)
                print(f"Received message from {addr}")
                
                try:
                    union_msg = ht_eth_pb2.HT_ETH_Union()
                    union_msg.ParseFromString(data)
                    
                    if union_msg.HasField('get_config_'):
                        print("yo")
                        # send_union_msg = ht_eth_pb2.HT_ETH_Union()
                        # send_union_msg.config_.CopyFrom(current_config)

                        # send_union_msg_p2 = ht_eth_pb2.HT_ETH_Union()
                        # send_union_msg_p2.case_msg_.CopyFrom(CASE_msg)
                        # send_sock.sendto(send_union_msg.SerializeToString(), ('127.0.0.1', send_port))
                        # send_sock.sendto(send_union_msg_p2.SerializeToString(), ('127.0.0.1', send_port))
                        # print(f"Sent config response to {addr}")
                    else:
                        print("receiving config")
                        current_config = union_msg.config_
                except Exception as e:
                    print(f"Error processing message: {e}")
    finally:
        server_socket.close()
        send_sock.close()

if __name__ == "__main__":
    start_udp_server('192.168.1.69', 20001, 20001)  # Use the correct IP and port
