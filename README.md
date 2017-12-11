# PyMineHub

## Development

### Module design

#### Dependency

Modules depend only on parents or siblings.

```
mcpe
  network
    - codec
      - batch -> typing, mcpe.network.packet, .common
      - common -> network.codec
      - connection -> config, mcpe.network.packet, .common
    - handler -> typing, raknet, network.[address], mcpe.[const, player, world], .codec, .packet
    - packet -> mcpe.[value, geometry], network.[address, packet]
  const
  geometry -> typing
  player -> .const, .geometry, .value
  server -> raknet, .network
  value -> .const .geometry
  world -> config, .const
network -> binutil
  address
  codec -> binutil, .address
  packet
raknet -> network
  - codec -> network.[codec], .encapsulation, .packet
  - encapsulation -> .packet
  - fragment
  - packet -> network.[address, packet]
  - server -> network.[address, codec], .codec, .packet, .session
  - session -> .codec, .encapsulation, .fragment, .packet
binutil -> typing
config
typing

- : Hidden from outside modules
```

### Reference

This project is implemented by referring to [PocketMine-MP](https://github.com/pmmp/PocketMine-MP) source code.
