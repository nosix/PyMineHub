# PyMineHub

## Development

### Module design

#### Dependency

Modules depend only on parents or siblings. Siblings depend only on the above siblings.

```
config
typing
binutil -> typing
network -> binutil
  address
  packet
  codec -> binutil, .[address, packet]
raknet -> network
  - fragment
  - packet -> network.[address, packet]
  - encapsulation -> .[packet]
  - codec -> network.[codec], .[encapsulation, packet]
  - session -> network.[packet], .[codec, encapsulation, fragment, packet, encapsulation]
  - server -> network.[address, packet, codec], .[codec, packet, encapsulation, session]
mcpe
  const
  geometry -> typing
  value -> .[const, geometry]
  world -> config, .[const]
  player -> .[const, geometry, value]
  network
    - packet -> mcpe.[value, geometry], network.[address, packet]
    - codec -> typing, config, network, mcpe.network.[packet]
      - common -> network.[codec]
      - batch -> typing, mcpe.network.[packet], .[common]
      - connection -> config, mcpe.network.[packet], .[common]
    - queue -> raknet, network.[address, packet], .[packet, codec]
    - handler -> typing, raknet, network.[address, packet], mcpe.[const, player, world], .[codec, packet, queue]
  server -> raknet, .[network]

- : Hidden from outside modules
```

### Reference

This project is implemented by referring to [PocketMine-MP](https://github.com/pmmp/PocketMine-MP) source code.
