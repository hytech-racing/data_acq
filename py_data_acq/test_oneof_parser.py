from py_data_acq.common.protobuf_helpers import get_oneof_msg_names_and_classes


names, classes = get_oneof_msg_names_and_classes()

print(names)
print(classes)