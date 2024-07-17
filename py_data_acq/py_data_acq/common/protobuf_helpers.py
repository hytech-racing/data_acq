from hytech_np_proto_py import hytech_pb2
import google.protobuf.message_factory
from cantools.database import *
from aero_sensor_protos_np_proto_py.aero_sensor import aero_sensor_pb2
from foxglove_schemas_protobuf.CompressedImage_pb2 import CompressedImage
from foxglove_schemas_protobuf import CompressedImage_pb2 

def get_msg_names_and_classes():
    message_names = []
    message_classes = {}

    def add_messages_from_module(module):
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and hasattr(attr, "DESCRIPTOR"):
                message_names.append(attr.DESCRIPTOR.name)
                message_classes[
                    attr.DESCRIPTOR.name
                ] = google.protobuf.message_factory.GetMessageClass(
                    module.DESCRIPTOR.message_types_by_name.get(attr.DESCRIPTOR.name)
                )
    add_messages_from_module(hytech_pb2)
    #add_messages_from_module(aero_sensor_pb2)
    add_messages_from_module(CompressedImage_pb2)


    
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