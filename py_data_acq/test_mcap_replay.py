
from py_data_acq.common.protobuf_helpers import pack_cantools_msg
from hytech_np_proto_py import hytech_pb2
import time
import can
from can.interfaces.udp_multicast import UdpMulticastBus
import sys
import os
from mcap_protobuf.decoder import DecoderFactory
import cantools

from mcap.reader import make_reader


def main():
    bus1 = can.interface.Bus(channel=UdpMulticastBus.DEFAULT_GROUP_IPv6, interface="udp_multicast")
    path_to_dbc = os.environ.get('DBC_PATH')
    full_path = os.path.join(path_to_dbc, "hytech.dbc") 
    db = cantools.database.load_file(full_path)

    
    with open(sys.argv[1], "rb") as f:
        while True:
            last_log_time = 0
            msg_time_diff_sec = 0
            last_send_time = 0
            reader = make_reader(f, decoder_factories=[DecoderFactory()])
            for schema, channel, message, proto_msg in reader.iter_decoded_messages():
                print(proto_msg.DESCRIPTOR.name)
                msg, data = pack_cantools_msg(proto_msg, proto_msg.DESCRIPTOR.name, db)
                print(message.log_time / 1e9)
                curr_log_time = message.log_time / 1e9
                if last_log_time !=0:
                    msg_time_diff = curr_log_time - last_log_time 
                else:
                    msg_time_diff = 0

                time.sleep(msg_time_diff)
                if msg is not None:
                    msg_out = can.Message(arbitration_id=msg.frame_id, is_extended_id=False, data=data)
                    bus1.send(msg_out)
                
                
                
            # print(f"{channel.topic} {schema.name} [{message.log_time}]: {proto_msg}")



if __name__ == "__main__":
    main()