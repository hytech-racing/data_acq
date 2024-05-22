from hytech_np_proto_py import hytech_pb2
import google.protobuf.message_factory
from cantools.database import *

from hytech_eth_np_proto_py import ht_eth_pb2

def get_msg_names_and_classes():
    message_names = []
    message_classes = {}
    # Iterate through all attributes in the generated module
    for attr_name in dir(hytech_pb2):
        # Check if the attribute is a class and if it's a message type
        attr = getattr(hytech_pb2, attr_name)
        if isinstance(attr, type) and hasattr(attr, "DESCRIPTOR"):
            message_names.append(attr.DESCRIPTOR.name)
            message_classes[
                attr.DESCRIPTOR.name
            ] = google.protobuf.message_factory.GetMessageClass(
                hytech_pb2.DESCRIPTOR.message_types_by_name.get(attr.DESCRIPTOR.name)
            )
    return message_names, message_classes

def get_oneof_msg_names_and_classes():
    message_names = []
    message_classes = {}
    # Iterate through all fields in the oneof message
    oneof_message = ht_eth_pb2.HT_ETH_Union()
    for field in oneof_message.DESCRIPTOR.fields:
        # Check if the field is a message type
        if field.message_type is not None:
            message_names.append(field.message_type.name)
            message_classes[field.message_type.name] = field.message_type._concrete_class
    return message_names, message_classes

def pack_protobuf_msg(cantools_dict: dict, msg_name: str, message_classes):
    if msg_name in message_classes:
        pb_msg = message_classes[msg_name]()
    for key in cantools_dict.keys():
        if(type(cantools_dict[key]) is namedsignalvalue.NamedSignalValue):
            setattr(pb_msg, key, str(cantools_dict[key].value))
        else:
            setattr(pb_msg, key, cantools_dict[key])
    return pb_msg

def pack_cantools_msg(pb_msg_in, msg_name: str, cantools_db):
    # get the un-populated message by its name
    try:
        msg_out = cantools_db.get_message_by_name(msg_name.upper())
        # now we need to iterate through all of the message member variables
        #  and set dictionary values in the can msg
        
        # 1. need to get the signals dictionary for this CAN msg
        msg_sigs = msg_out.signals
        # each signal name is an attribute within the protobuf message and we can populate 

        # 2. populate dict with values 
        msg_dict = {}
        for sig in msg_sigs:

            if type(getattr(pb_msg_in, sig.name)) == str:
                msg_dict[sig.name] = sig.choices[int(getattr(pb_msg_in, sig.name))]
            else:
                msg_dict[sig.name] = getattr(pb_msg_in, sig.name)
        
        
        out_data = msg_out.encode(msg_dict)
        return msg_out, out_data
    except:
        return None, None