# PyMineHub

## Development

### Module design

#### Dependency

Modules depend only on parents or siblings. Siblings depend only on the above siblings.

```
typevar
config -> typevar
binutil -> typevar
value
network -> binutil
  address
  codec -> binutil, value, .[address]
raknet -> network
  - fragment -> value
  - packet -> value, network.[address]
  - frame -> .[packet]
  - codec -> network.[codec], .[frame, packet]
  - queue -> config, .[codec, frame]
  - session -> .[codec, fragment, frame, packet, queue]
  - server -> config, network.[address, codec], .[codec, packet, frame, session]
mcpe
  const
  geometry -> typevar
  value -> .[const, geometry]
  world -> config, .[const]
  player -> .[const, geometry, value]
  network
    - packet -> value, mcpe.[value], network.[address]
    - codec -> typevar, config, network, mcpe.network.[packet]
      - common -> network.[codec]
      - batch -> typevar, mcpe.network.[packet], .[common]
      - connection -> config, mcpe.network.[packet], .[common]
    - queue -> raknet, network.[address], .[packet, codec]
    - handler -> typevar, raknet, network.[address], mcpe.[const, player, world], .[codec, packet, queue]
  server -> raknet, .[network]

- : Hidden from outside modules
```

### Reference

This project is implemented by referring to [PocketMine-MP](https://github.com/pmmp/PocketMine-MP) source code.
