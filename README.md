&#x26a0; **This project is finished. There are no plans to update in the future. If you need to update, please use fork.** &#x26a0;

# PyMineHub (PMH)

Multiplay server of Minecraft Pocket Edition

The goal of this project is to make the server small and to work with others.
Extensibility than full spec implementation.
This project will assume that MineCraft is used as an environment of creation, not as a game.

## Target version

- Python 3.5.3
  - 2017-09-07-raspbian-stretch-lite.img
- and later

## Testing environment

- Python 3.6.1
  - macOS High Sierra 10.13
- Python 3.5.3
  - Raspbian stretch lite 2017-09-07

## Demo

[![demo1](http://img.youtube.com/vi/ezoJ7GiG7rQ/0.jpg)](http://www.youtube.com/watch?v=ezoJ7GiG7rQ?loop=1&cc_load_policy=1)

[![demo2](http://img.youtube.com/vi/nPKKtxPtl98/0.jpg)](http://www.youtube.com/watch?v=nPKKtxPtl98?loop=1)

## Trial

First, get the source code and start the server.

```
$ git clone https://github.com/nosix/PyMineHub.git
$ cd PyMineHub
PyMineHub $ bin/run.sh
In your environment, Python 3.6.1 is used.
INFO:pyminehub.config:RAKNET_SERVER_PORT=19132
INFO:pyminehub.config:TCP_SERVER_PORT=19142
INFO:pyminehub.config:WORLD_NAME=PyMineHub
INFO:pyminehub.config:GAME_MODE=SURVIVAL
INFO:pyminehub.config:SPAWN_MOB=True
INFO:pyminehub.config:INIT_SPACE=(32, 32)
INFO:pyminehub.config:PLAYER_SPAWN_POSITION=(256, 56, 256)
INFO:pyminehub.mcpe.plugin.loader:Plugin is loaded from directory "plugin".
INFO:pyminehub.mcpe.plugin.loader:AboutCommandProcessor was registered into CommandRegistry.
INFO:pyminehub.mcpe.plugin.loader:LevelDBChunkGeneratorPlugin overrode ChunkGeneratorPlugin.
INFO:pyminehub.mcpe.plugin.loader:ActionCommandProcessor was registered into CommandRegistry.
INFO:pyminehub.mcpe.plugin.loader:GameEventCommandProcessor was registered into CommandRegistry.
```

Sign-in from Friends tab on MineCraft.
PyMineHub support MineCraft version 1.2.7 (maybe, later versions as well) and protocol version 160.
We have confirmed working at version 1.2.10.

When you start the game, a world of only water is generated.
And, birds move randomly.
If you want to change the generated world and mob movements, use the plugin.
By default, the source code under the `plugin` directory in the current directory is loaded.
If you want to change the plugin directory, specify the directory in the `MPH_PLUGIN_ROOT` environment variable.
To disable the plugin, specify the `MPH_PLUGIN_ROOT` environment variable to be `""`.
Run `run.sh` with the `-d` option to disable the plugin.

```
PyMineHub $ rm PyMineHub-p0.db 
PyMineHub $ bin/run.sh -d
In your environment, Python 3.6.1 is used.
INFO:pyminehub.config:RAKNET_SERVER_PORT=19132
INFO:pyminehub.config:TCP_SERVER_PORT=19142
INFO:pyminehub.config:WORLD_NAME=PyMineHub
INFO:pyminehub.config:GAME_MODE=SURVIVAL
INFO:pyminehub.config:SPAWN_MOB=True
INFO:pyminehub.config:INIT_SPACE=(32, 32)
INFO:pyminehub.config:PLAYER_SPAWN_POSITION=(256, 56, 256)
INFO:pyminehub.mcpe.plugin.loader:PMH_PLUGIN_ROOT=
INFO:pyminehub.mcpe.plugin.loader:Plugin is disabled.
```

`PyMineHub-p0.db` is a data file.
Currently SQLite DB is used, but we might change it (the timing is undecided).
If `INIT_SPACE` is specified,
it creates chunks (parts of terrain data) in the area specified at startup
and duplicates chunks in this area to other area.
If `INIT_SPACE` is `None`, chunks are generated when they are needed.
This is a feature to lower the CPU load during play.

Again, sign-in from Friends tab on MineCraft.
When you start the game, a world of only grass is generated. And, birds move randomly. 
In this example, the plugin directories are not loaded and the default plugins are used.
The default plugins are in `src/pyminehub/mcpe/plugin/default`.
Then, the interface of the plugins are defined in `src/pyminehub/mcpe/plugin`.

- `ChunkGeneratorPlugin`
  - override
- `MobProcessorPlugin`
  - override
- `PlayerConfigPlugin`
  - override
- `WorldExtensionPlugin`
  - append
- `ExtraCommandPlugin`
  - append

When running `run.sh` without the `-d` option (first example),
`LevelDBChunkGeneratorPlugin` in `plugin` directory override the default plugin.
In the case of overloading, the last loaded plugin is enabled.
On the other hand, more than one `ExtraCommandPlugin` will be added, all loaded plugins are enabled.

## Plugin

The plugin loader imports the module directly under the plugin directory,
and it reads the class described in those `__all__`.
Classes need to have plugin's interface in superclass.
Deleting the description of `__all__` will disable the plugin.

```
plugin (or directory specified by MPH_PLUGIN_ROOT)
  xxx_plugin
    __init__.py
      __all__ = [...]
  yyy_plugin
    __init__.py
      __all__ = [...]
```

### ChunkGeneratorPlugin

This plugin is a plugin for generating terrain data.

### MobProcessorPlugin

This plugin is a plugin for controlling the appearance, movement, and extinction of mobs.
The contents that can be done if there is a demand may increase.

### PlayerConfigPlugin

This plugin is a plugin for setting for each player.
Although we have set it for extension, we recommend that you do not want to use the current situation.
The contents that can be done if there is demand may increase.

### WorldExtensionPlugin

This plugin customizes the update of the world.
You will be able to do the following.

- Change or cancel the received update instruction (`filter_action`)
- Change or cancel update notification to be sent (`filter_event`)
- Periodically generate update instructions (`update`)

All update instructions received from the client and all update notifications sent from the world server,
it passes through `filter` of all loaded `WorldExtensionPlugin`.

```
Client -> (action a) -> PluginA.filter_action -> (action a') -> PluginB.filter_action -> (action a') -> World Server
Client <- (event e') <- PluginA.filter_event <- (event e') <- PluginB.filter_event <- (event e) <- World Server

action a : original update instruction
action a' : modified update instruction
event e : original update notification
event e' : modified update notification
```

It can cancel, when `filter` return `None`.

```
Client -> (action a) -> PluginA.filter_action -> (None) -> X
X <- (None) <- PluginB.filter_event <- (event e) <- World Server

action a : original update instruction
event e : original update notification
X : processing exit
```

`update` can generate update instructions.
`update` is executed at the interval set by` WORLD_TICK_TIME`.

### ExtraCommandPlugin

This plugin enables the use of the command.
Commands allow you to operate the server.
The plugin return a command processor.
When the client executes the command, the method of the command processor is executed.

For example, `ActionCommandProcessor` in `plugin/action/main.py` is below.

```python
from binascii import unhexlify
from pickle import loads
from pyminehub.mcpe.command.annotation import String
from pyminehub.mcpe.command.api import CommandContext, command

class ActionCommandProcessor:

    @command
    def perform(self, context: CommandContext, args: str) -> None:
        """Perform action in the world."""
        self._perform(context, String(args))

    @perform.overload
    def _perform(self, context: CommandContext, data: String) -> None:
        action = loads(unhexlify(data))
        context.perform_action(action)
```

`ActionCommandProcessor` provide `/perform data` command.
The command name `perform` is named from method name `perform`.
By applying the `command` decorator to the method, the method name becomes the command name.
The method parameters must be `CommandContext` and `str`.

Use the `overload` decorator to provide the method signature to the client.
Signatures are used to indicate usage of the command.
The parameters of the method with `overload` decorator must be `CommandContext` and
the types defined in `pyminehub.mcpe.command.annotation`.
When calling the method, wrapping in the types in `pyminehub.mcpe.command.annotation` will enable overloading.
For that reason, The method names may be the same.

## Client

Not only servers, we also have a simple client.

For example, `ActionCommandClient` in `plugin/action/client.py` is below.

```python
from binascii import hexlify
from pickle import dumps
from typing import Union
from pyminehub.mcpe.action import Action, ActionType, action_factory
from pyminehub.mcpe.network import MCPEClient
from pyminehub.mcpe.geometry import Vector3
from pyminehub.mcpe.const import MoveMode
from pyminehub.mcpe.main.client import connect

class ActionCommandMixin:

    @property
    def client(self) -> MCPEClient:
        raise NotImplementedError()

    def perform_action(self, action_or_type: Union[Action, ActionType], *args, **kwargs) -> None:
        action = action_factory.create(action_or_type, *args, **kwargs) \
            if isinstance(action_or_type, ActionType) else action_or_type
        data = hexlify(dumps(action)).decode()
        self.client.execute_command('/perform {}'.format(data))

class ActionCommandClient(MCPEClient, ActionCommandMixin):

    @property
    def client(self) -> MCPEClient:
        return self

def run_client():
    with connect('127.0.0.1', player_name='Taro', client_factory=ActionCommandClient) as client:
        client.perform_action(
            ActionType.MOVE_PLAYER, 1, Vector3(256.0, 64.0, 256.0), 0.0, 0.0, 0.0, MoveMode.NORMAL, True, 0, True)
        client.wait_response(timeout=10)
        print(client.get_entity())
```

It connects to the server by method `connect`.
To extend the client, specify the parameter `client_factory`.
For the parameter `client_factory`, specify a function that creates an instance of a class that extends `MCPEClient`.
When the connection to the server is successful,
the generated instance is bound to the variable `client` specified by `as`.

The method `wait_response` waits for something packet.
It does not wait for the response of the packet sent immediately before.
If some packet is received, proceed to the next.

Please see `test/multiplay.py`, too.

## Server Config

If you want to change the setting, edit `src/pyminehub/mcpe/main/server.py`.
For example, the part of `src/pyminehub/mcpe/main/server.py` is below.

```python
if __name__ == '__main__':
    from pyminehub.config import set_config
    set_config(game_mode='CREATIVE', spawn_mob=False)
    set_config(
        world_name='Small',
        init_space=(1, 1),
        player_spawn_position=(0, 56, 0)
    )
    # ... snip ...
```

Calls to `set_config` can be combined in one operation or divided.
The parameter names is defined in `pyminehub.config`.

### Reference

- This project is implemented by referring to [PocketMine-MP](https://github.com/pmmp/PocketMine-MP) source code.
- [RakNet](http://www.raknet.net/raknet/manual/systemoverview.html)
- [Pocket Edition Protocol Documentation](http://wiki.vg/Pocket_Edition_Protocol_Documentation)
- [Java Edition data values](https://minecraft.gamepedia.com/Java_Edition_data_values)
