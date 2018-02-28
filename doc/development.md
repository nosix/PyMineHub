# Development

## Test

Run `bin/test.sh` and run `test/multiplay.py`.
When running `test/multiplay.py`, run `bin/run.sh` first.

## Module design

### Dependency

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
  address -> config
  codec -> value, binutil.*, .[address]
  handler -> .[address]
  server -> .[address, handler]
  client -> .[address, handler]
raknet
  - fragment
  - frame -> value
  - packet -> value, network.[address]
  - channel -> .[frame]
  - codec -> binutil.*, network.[codec, const], .[frame, packet]
  - sending -> config, queue, value, network.[handler], .[codec, frame]
  - session -> value, network.[const, handler], .[channel, codec, fragment, frame, packet, sending]
  - protocol -> value, network.[address, handler], .[codec, packet, session]
  - server -> config, network.[address, handler, server], .[packet, protocol, session]
  - client -> config, network.[address, handler, client], .[packet, protocol, session]
tcp
  - protocol -> binutil.[converter, instance], network.[address, handler]
  - server -> config, network.[address, handler, server], .[protocol]
  - client -> config, network.[address, handler, client], .[protocol]
mcpe
  const
  geometry -> typevar
  value -> binutil.[converter], .[const, geometry]
  resource
    - loader
  attribute -> .[const, value]
  metadata -> .[const, geometry, value]
  action -> value, mcpe.[const, geometry, value]
  event -> value, mcpe.[const, geometry, value]
  chunk -> binutil.*, mcpe.[const, geometry, value]
  datastore -> config, mcpe.[chunk, geometry, value]
  command
    const
    annotation -> mcpe.[geometry]
    value -> .[const]
    api -> typevar, mcpe.[action], .[annotation, const, value]
    impl -> typevar, mcpe.[action], .[api]
  plugin
    command
    generator -> mcpe.[chunk, geometry]
    mob -> mcpe.[chunk, const, geometry]
    player -> mcpe.[const, value]
    default
      - generator -> mcpe.[chunk, const, geometry, value], mcpe.plugin.[generator]
      - mob -> mcpe.[const], mcpe.plugin.[mob]
      - player -> mcpe.[const, value], mcpe.plugin.[player]
    loader -> mcpe.command.[api], .[command, default, generator, mob, player]
  world
    - clock -> config
    - interface -> mcpe.[value]
    - proxy -> mcpe.[action, const, event, resource, value]
    - item
      - spec -> mcpe.[const, geometry, value]
      - catalog -> mcpe.[const], .[spec]
    - block
      - spec -> mcpe.[const, geometry, value]
      - catalog -> mcpe.[const, geometry, value] .[spec]
      - functional -> mcpe.[const, geometry, value] .[catalog]
    - generator -> mcpe.[chunk, datastore, geometry], mcpe.plugin.[generator]
    - inventory -> .[const, value], .[item]
    - space -> mcpe.[chunk, const, datastore, geometry, value], .[block, generator]
    - entity
      - spec -> mcpe.[const, geometry]
      - instance -> config, mcpe.[action, const, geometry, resource, value], mcpe.world.[inventory], .[spec]
      - collision -> mcpe.[event], mcpe.world.[interface], .[instance]
      - pool -> mcpe.[const, datastore, value], .[collision, instance]
    - server -> config, value,
                mcpe.[action, attribute, chunk, const, datastore, event, geometry, value],
                mcpe.plugin.[loader, mob, player],
                .[clock, entity, generator, interface, item, proxy, space]
  network
    - skin
    - const
    - value -> binutil.[converter], mcpe.[geometry, value], .[const]
    - packet
      - connection -> value, network.[address]
      - game -> value, mcpe.[const, geometry, value], mcpe.command.[const, value], .[const, value]
    - reliability -> config, network.[handler], mcpe.network.[packet]
    - codec
      - connection -> config, binutil.*, network.*, mcpe.network.[packet]
      - game -> binutil.*, network.*, mcpe.[const, geometry, value], mcpe.command.[const, value],
                mcpe.network.[const, packet, value]
    - player -> mcpe.[const, event, geometry, value], .[value]
    - session -> networkd.[address, handler], mcpe.[value] .[player]
    - queue -> value, network.[address, handler], .[codec, packet, reliabiliry]
    - login -> network.[address], mcpe.[const, event, geometry, metadata, world], mcpe.command.[api]
               .[const, packet, player, session, value]
    - handler -> value, network.[address, handler], .[codec, packet, queue, reliability]
    - server -> config, network.[address, handler], mcpe.[action, const, event, geometry, metadata, value, world],
                mcpe.command.[api, impl], .[const, handler, login, packet, player, reliability, session, value]
    - client -> network.[address, client], mcpe.[chunk, const, geometry, value], mcpe.command.[api, const, value],
                .[const, handler, packet, reliability, skin, value] 
  main
    server -> config, raknet, tcp, network.[server],
              mcpe.[network, datastore, world], mcpe.command.[api], mcpe.plugin.[loader]
    client -> raknet, tcp, mcpe.[network, client]

- : Hidden from outside modules
```

### Codecs for packet

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

## Data Length

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
