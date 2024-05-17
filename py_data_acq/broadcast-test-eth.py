import socket
from hytech_eth_np_proto_py import ht_eth_pb2
import select
import time
def start_udp_server(ip, port, send_port):
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"UDP server listening on {ip}:{port}")
    CASE_msg= ht_eth_pb2.CASE_msg()
    CASE_msg.vehm_fl_slip = 6969.0
    
    try:
        while True:
            print("sending")                
            send_sock.sendto(CASE_msg.SerializeToString(), ('127.0.0.1', send_port))
            time.sleep(0.2)
    finally:
        
        send_sock.close()

if __name__ == "__main__":
    start_udp_server('127.0.0.1', 20002, 20001)  # Use the correct IP and port

