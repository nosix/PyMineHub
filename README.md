# PyMineHub

Multiplay server of Minecraft Pocket Edition

The goal of this project is to make the server small and to work with others.
Extensibility than full spec implementation.

## Target version

- Python 3.5.3
  - 2017-09-07-raspbian-stretch-lite.img

## Development

### Data Length

| Mark | Part | Length [bytes] | Note |
|:---:|:---|---:|:---:|
| A | MTU | 1492 | B + D + E |
| B | OpenConnectionRequest1 | 1464 | |
| C | OpenConnectionRequest1 zero padding | 1446 | |
| D | IP header | 20 | |
| E | UDP header | 8 | |
| F | RakNet weird | 8 | ? | 
| G | RakNet packet (datagram) header | 4 | |
| H | Max frame header | 20 | |
| I | All header | 60 | D + E + F + G + H |
| J | Max frame payload | 1432 | A - I |

The length of A,B,C,J is an example.

### Module design

#### Dependency

Modules depend only on parents or siblings. Siblings depend only on the above siblings.

```
typevar
enum
queue
config -> typevar
value -> config
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
  - channel -> .[frame]
  - handler -> network.[address], .[frame]
  - codec -> network.[codec], .[frame, packet]
  - sending -> config, value, queue, .[codec, frame]
  - session -> value, .[channel, codec, fragment, frame, packet, sending]
  - server -> config, value, network.[address, codec], .[handler, codec, packet, frame, session]
mcpe
  const -> enum
  geometry -> typevar
  value -> binutil.[converter], .[const, geometry]
  resource
    - loader
  attribute -> .[const, value]
  metadata -> .[const, geometry, value]
  inventory -> .[const, value]
  command -> .[const, value]
  chunk -> binutil.[composite, instance], mcpe.[const, geometry]
  player -> .[value, world]
  action -> value, .[player]
  event -> value, .[player]
  plugin
    generator -> mcpe.[geometry, chunk]
    default
      - generator -> mcpe.[chunk], mcpe.plugin.[generator]
    loader -> .[generator, default]
  world -> value, .[const, player]
    - interface -> mcpe.[value]
    - database -> config, mcpe.[geometry, chunk]
    - generator -> mcpe.[geometry, chunk, plugin], .[database]
    - entity -> mcpe.[const, geometry, inventory, resource, value]
      - spec -> mcpe.[const, geometry]
      - instance -> mcpe.[const, geometry, inventory, resource, value], .[spec]
      - collision -> mcpe.[event], mcpe.world.[interface], .[instance]
      - pool -> mcpe.[value], mcpe.world.[database], .[collision, instance]
    - space -> mcpe.[const, value, geometry, chunk], .[database, generator]
    - proxy -> mcpe.[const, value, resource], .[action, event]
    - server -> config, value, mcpe.[action, attribute, event, chunk],
                .[interface, database, entity, generator, space, proxy]
  network -> typevar, value, config, network, raknet, mcpe.[const, value, metadata, player, world]
    - packet -> value, mcpe.[value], network.[address]
    - codec -> typevar, config, network, .[packet]
      - batch -> typevar, network.[codec], mcpe.network.[packet]
      - connection -> config, network.[codec], mcpe.network.[packet]
    - session -> raknet, networkd.[address], mcpe.[value, player]
    - queue -> value, raknet, network.[address], .[packet, codec]
    - login -> network.[address], mcpe.[command, metadata, player, world], .[packet, session]
    - handler -> typevar, value, raknet, network.[address],
                 mcpe.[const, world], .[codec, packet, session, queue, login]
  main
    server -> raknet, mcpe.[network, world]

- : Hidden from outside modules
```

#### Codecs for packet

- Packet class definition (immutable value object by NamedTuple)
  - `raknet.packet` module
  - `raknet.frame` module
  - `mcpe.network.packet` module
  - These are based on
    - `value` module
- Codec object definition
  - `raknet.codec` module
  - `mcpe.network.codec.connection` module
  - `mcpe.network.codec.batch` module
  - These are based on
    - `binutil` module
    - `network.codec` module
- Testcase (in test directory)
  - `codec_*` module
- Tool (in tool directory)
  - `tool.decoding` module

### Reference

- This project is implemented by referring to [PocketMine-MP](https://github.com/pmmp/PocketMine-MP) source code.
- [RakNet](http://www.raknet.net/raknet/manual/systemoverview.html)
- [Pocket Edition Protocol Documentation](http://wiki.vg/Pocket_Edition_Protocol_Documentation)
- [Java Edition data values](https://minecraft.gamepedia.com/Java_Edition_data_values)