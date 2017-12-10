# PyMineHub

## Development

### Module design

#### Dependency

Modules depend only on parents or siblings.

```
binutil -> typing
config
typing
mcpe
  const
  handler -> .network.[codec, packet], network.[address], raknet, .player
  player
  geometry -> typing
  server -> .handler, raknet
  network
    codec
      batch -> typing mcpe.network.packet, .common
      common -> network.codec
      packet -> config, mcpe.network.packet, .common
    packet -> mcpe.[value, geometry], network.[address, packet]
  value -> .const .geometry
network -> binutil
  address
  codec -> binutil, .address
  packet
raknet -> network
  codec -> network.[codec], .encapsulation, .packet
  encapsulation -> .packet
  fragment
  packet -> network.[address, packet]
  server -> network.[address, codec], .codec, .packet, .session
  session -> .codec, .encapsulation, .fragment, .packet
```

### Reference

This project is implemented by referring to [PocketMine-MP](https://github.com/pmmp/PocketMine-MP) source code.
