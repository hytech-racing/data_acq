{ lib, pkgs }:

pkgs.buildGoPackage rec {
  pname = "mcap_cli";
  version = "0.0.44";
  goPackagePath = "github.com/foxglove/mcap";
  src = pkgs.fetchFromGitHub {
    owner = "foxglove";
    repo = "mcap";
    rev = "releases/mcap-cli/v${version}";
    hash = "sha256-OAL2z28FhMXlyVzgmLCzHNCpCeK7hIkQB6jd7v3WHHA=";
  };

  meta = with lib; {
    description = "mcap commandline interface";
    homepage = "https://github.com/foxglove/mcap";
    license = licenses.mit;
  };

  goDeps = ./mcap_go_deps.nix;
}
