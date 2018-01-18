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
queue
config -> typevar
value -> config
binutil
  converter -> typevar
  instance -> .[converter]
  composite -> typevar, .[converter]
network
  address
  codec -> value, binutil.[composite, instance], .[address]
raknet
  - fragment -> value
  - packet -> value, network.[address]
  - frame -> .[packet]
  - channel -> .[frame]
  - handler -> network.[address], .[frame]
  - codec -> network.[codec], .[frame, packet]
  - sending -> config, value, queue, .[codec, frame]
  - session -> value, .[channel, codec, fragment, frame, packet, sending]
  - protocol -> value, binutil.[composite], network.[address],
                .[codec, handler, packet, session]
  - server -> config, network.[address], .[handler, packet, protocol, session]
  - client -> config, network.[address], .[handler, packet, protocol, session]
mcpe
  const -> enum
  geometry -> typevar
  value -> binutil.[converter], .[const, geometry]
  resource
    - loader
  attribute -> .[const, value]
  metadata -> .[const, geometry, value]
  command -> typevar, .[action, const, geometry, value]
  chunk -> binutil.[composite, instance], mcpe.[const, geometry, value]
  action -> value, mcpe.[value]
  event -> value, mcpe.[value]
  datastore -> config, mcpe.[geometry, chunk]
  plugin
    generator -> mcpe.[geometry, chunk]
    mob -> mcpe.[const, geometry, chunk]
    player -> mcpe.[const, value]
    default
      - generator -> mcpe.[geometry, chunk], mcpe.plugin.[generator]
      - mob -> mcpe.plugin.[mob]
      - player -> mcpe.plugin.[player]
    loader -> .[default, generator, mob, player]
  world
    - interface -> mcpe.[value]
    - item -> mcpe.[const]
    - block -> mcpe.[const, value]
    - inventory -> .[const, value, item]
    - entity
      - spec -> mcpe.[const, geometry]
      - instance -> mcpe.[const, geometry, resource, value], mcpe.world.[inventory], .[spec]
      - collision -> mcpe.[event], mcpe.world.[interface], .[instance]
      - pool -> mcpe.[const, value, datastore], .[collision, instance]
    - generator -> mcpe.[geometry, chunk, datastore], mcpe.plugin.[generator]
    - space -> mcpe.[const, value, geometry, chunk, datastore], .[block, generator]
    - proxy -> mcpe.[const, value, resource], .[action, event]
    - server -> config, value,
                mcpe.[action, attribute, chunk, datastore, event],
                mcpe.plugin.[loader, mob, player],
                .[entity, generator, interface, item, proxy, space]
  network
    - packet
      - connection -> value, network.[address]
      - game -> value, mcpe.[value]
    - codec
      - connection -> config, network.[codec], mcpe.network.[packet]
      - game -> network.[codec], mcpe.[value], mcpe.network.[packet]
    - player -> .[value, event]
    - session -> raknet, networkd.[address], mcpe.[value] .[player]
    - queue -> value, raknet, network.[address], .[packet, codec]
    - login -> network.[address], mcpe.[command, event, metadata, value, world], .[packet, player, session]
    - handler -> value, raknet, network.[address], .[codec, packet, queue, reliability]
    - server -> config, raknet, network.[address], mcpe.[action, command, event, metadata, value, world],
                .[handler, login, packet, reliability, session]
    - client -> raknet, network.[address], mcpe.[const, value], .[handler, packet, reliability] 
  main
    server -> raknet, mcpe.[network, datastore, command, world], mcpe.plugin.[loader]
    client -> raknet, mcpe.[network]

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