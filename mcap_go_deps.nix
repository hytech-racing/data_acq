[
  #   # goDeps is a list of Go dependencies.
  {
    # goPackagePath specifies Go package import path.
    goPackagePath = "github.com/spf13/cobra";
    fetch = {
      # `fetch type` that needs to be used to get package source.
      # If `git` is used there should be `url`, `rev` and `hash` defined next to it.
      type = "git";
      url = "https://github.com/spf13/cobra";
      rev = "5a1acea3210649f3d70002818ec04b09f6347062";
      sha256= "sha256-i0y1wnj7gfKlsU9cC9Bhj7v6lZBph4Ooa3fcWR4s6YE=";
    };
  }
  {
    # goPackagePath specifies Go package import path.
    goPackagePath = "github.com/spf13/pflag";
    fetch = {
      # `fetch type` that needs to be used to get package source.
      # If `git` is used there should be `url`, `rev` and `hash` defined next to it.
      type = "git";
      url = "https://github.com/spf13/pflag";
      rev = "d5e0c0615acee7028e1e2740a11102313be88de1";
      sha256= "sha256-g5g7TLXxTNlFA48alv5SKUW+YvoLJyV87Bu+Wn3YvC0=";
    };
  }
  {
    # goPackagePath specifies Go package import path.
    goPackagePath = "github.com/spf13/viper";
    fetch = {
      # `fetch type` that needs to be used to get package source.
      # If `git` is used there should be `url`, `rev` and `hash` defined next to it.
      type = "git";
      url = "https://github.com/spf13/viper";
      rev = "v1.18.2";
      sha256= "sha256-MXYbK6w1LEaoZ2/L/STF3WU1tbK+7NwGVxUCLKPkwks=";
    };
  }
  # {
  #   goPackagePath = "google.golang.org/protobuf/encoding/protojson";
  #   fetch = {
  #     type = "git";
  #     url = "https://google.golang.org/protobuf/encoding/protojson";
  #     rev = "784ddc588536785e7299f7272f39101f7faccc3f";
  #     hash = "sha256-Uo89zjE+v3R7zzOq/gbQOHj3SMYt2W1nDHS7RCUin3M=";
  #   };
  # }
  # {
  #   goPackagePath = "google.golang.org/protobuf/reflect/protodesc";
  #   fetch = {
  #     type = "git";
  #     url = "https://google.golang.org/protobuf/reflect/protodesc";
  #     rev = "784ddc588536785e7299f7272f39101f7faccc3f";
  #     hash = "sha256-Uo89zjE+v3R7zzOq/gbQOHj3SMYt2W1nDHS7RCUin3M=";
  #   };
  # }
  # {
  #   goPackagePath = "google.golang.org/protobuf/reflect/protoreflect";
  #   fetch = {
  #     type = "git";
  #     url = "https://google.golang.org/protobuf/reflect/protoreflect";
  #     rev = "784ddc588536785e7299f7272f39101f7faccc3f";
  #     hash = "sha256-Uo89zjE+v3R7zzOq/gbQOHj3SMYt2W1nDHS7RCUin3M=";
  #   };
  # }
  # {
  #   goPackagePath = "google.golang.org/protobuf/types/descriptorpb";
  #   fetch = {
  #     type = "git";
  #     url = "https://google.golang.org/protobuf/types/descriptorpb";
  #     rev = "784ddc588536785e7299f7272f39101f7faccc3f";
  #     hash = "sha256-Uo89zjE+v3R7zzOq/gbQOHj3SMYt2W1nDHS7RCUin3M=";
  #   };
  # }
  # {
  #   goPackagePath = "google.golang.org/protobuf/types/dynamicpb";
  #   fetch = {
  #     type = "git";
  #     url = "https://google.golang.org/protobuf/types/dynamicpb";
  #     rev = "784ddc588536785e7299f7272f39101f7faccc3f";
  #     hash = "sha256-Uo89zjE+v3R7zzOq/gbQOHj3SMYt2W1nDHS7RCUin3M=";
  #   };
  # }
]
