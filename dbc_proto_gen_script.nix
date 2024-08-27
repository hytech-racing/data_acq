{ lib, python311Packages }:

python311Packages.buildPythonApplication {
  pname = "py_dbc_proto_gen";
  version = "1.0.0";

  nativeBuildInputs = [ python311Packages.cantools ];
  propagatedBuildInputs = [ python311Packages.cantools python311Packages.protobuf python311Packages.requests ];
  buildInputs = [ python311Packages.cantools ];
  src = ./py_dbc_proto_gen;
}