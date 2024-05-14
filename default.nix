{ lib
, python311Packages
, mcap_support_pkg
, py_mcap_pkg
, py_foxglove_websocket_pkg
, asyncudp_pkg
, hytech_np_proto_py
, proto_gen_pkg
, hytech_eth_np_proto_py
}:

python311Packages.buildPythonApplication {
  pname = "py_data_acq";
  version = "1.0.1";

  propagatedBuildInputs = [
    python311Packages.cantools
    python311Packages.systemd
    python311Packages.websockets
    python311Packages.pprintpp
    python311Packages.can
    asyncudp_pkg
    python311Packages.lz4
    python311Packages.zstandard
    py_foxglove_websocket_pkg
    python311Packages.protobuf
    mcap_support_pkg
    py_mcap_pkg
    hytech_np_proto_py
    proto_gen_pkg
    python311Packages.flask
    python311Packages.flask-cors
    python311Packages.hypercorn
    python311Packages.asgiref # required for flask async 
    hytech_eth_np_proto_py
  ];

  src = ./py_data_acq;
}
