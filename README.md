# PyMineHub

## Target version

- Python 3.5.3
  - 2017-09-07-raspbian-stretch-lite.img

## Development

### Module design

#### Dependency

Modules depend only on parents or siblings. Siblings depend only on the above siblings.

```
typevar
value
config -> typevar
binutil -> typevar
  converter -> typevar
  instance -> .[converter]
  composite -> typevar, .[converter]
network -> binutil
  address
  codec -> value, binutil.[composite, instance], .[address]
raknet -> value, config, network
  - fragment -> value
  - packet -> value, network.[address]
  - frame -> .[packet]
  - codec -> network.[codec], .[frame, packet]
  - sending -> config, .[codec, frame]
  - session -> .[codec, fragment, frame, packet, queue]
  - server -> config, network.[address, codec], .[codec, packet, frame, session]
mcpe
  const
  geometry -> typevar
  value -> .[const, geometry]
  player -> .[const, geometry, value]
  world -> value, .[const, player]
    - action -> value, mcpe.[player]
    - event -> value, mcpe.[player]
    - proxy -> mcpe.[const], .[action, event]
    - server -> .[proxy]
  network -> typevar, value, config, network, raknet, mcpe.[const, value, player, world]
    - packet -> value, mcpe.[value], network.[address]
    - codec -> typevar, config, network, .[packet]
      - batch -> typevar, network.[codec], mcpe.network.[packet]
      - connection -> config, network.[codec], mcpe.network.[packet]
    - queue -> raknet, network.[address], .[packet, codec]
    - handler -> typevar, raknet, network.[address], mcpe.[const, player, world], .[codec, packet, queue]
  main
    server -> raknet, mcpe.[network, world]

- : Hidden from outside modules
```

### Reference

- This project is implemented by referring to [PocketMine-MP](https://github.com/pmmp/PocketMine-MP) source code.
- [RakNet](http://www.raknet.net/raknet/manual/systemoverview.html)
- [Pocket Edition Protocol Documentation](http://wiki.vg/Pocket_Edition_Protocol_Documentation)
