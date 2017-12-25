from typing import Tuple

from pyminehub.mcpe.const import CommandPermission
from pyminehub.mcpe.value import CommandData, CommandParameter, CommandEnum

_ENUM_VALUES = ('suicide', 'pl', 'w', 'msg', 'ver', 'about')

_POSTFIXES = ()

_ENUMS = (
    CommandEnum(name='KillAliases', index=(0,)),
    CommandEnum(name='PluginsAliases', index=(1,)),
    CommandEnum(name='TellAliases', index=(2, 3)),
    CommandEnum(name='VersionAliases', index=(4, 5))
)

_COMMAND_DATA = (
    CommandData(
        name='ban',
        description='Prevents the specified player from using this server',
        flags=0, permission=0, aliases=-1,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),
            ),
        )
    ),
    CommandData(
        name='ban-ip',
        description='Prevents the specified IP address from using this server',
        flags=0, permission=0, aliases=-1,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    ),
    CommandData(
        name='banlist',
        description='View all players banned from this server',
        flags=0, permission=0, aliases=-1,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    ),
    CommandData(
        name='defaultgamemode',
        description='Set the default gamemode',
        flags=0, permission=0, aliases=-1,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    ),
    CommandData(
        name='deop',
        description="Takes the specified player's operator status",
        flags=0, permission=0, aliases=-1,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    ),
    CommandData(
        name='difficulty',
        description='Sets the game difficulty',
        flags=0, permission=0, aliases=-1,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    ),
    CommandData(
        name='effect',
        description='Adds/Removes effects on players',
        flags=0, permission=0, aliases=-1,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    ),
    CommandData(
        name='enchant',
        description='Adds enchantments on items',
        flags=0, permission=0, aliases=-1,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    ),
    CommandData(
        name='gamemode',
        description='Changes the player to a specific game mode',
        flags=0, permission=0, aliases=-1,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    ),
    CommandData(
        name='give',
        description='Gives the specified player a certain amount of items',
        flags=0, permission=0, aliases=-1,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    ),
    CommandData(
        name='kick',
        description='Removes the specified player from the server',
        flags=0, permission=0, aliases=-1,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    ),
    CommandData(
        name='kill',
        description='Commit suicide or kill other players',
        flags=0, permission=0, aliases=0,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    ),
    CommandData(
        name='list',
        description='Lists all online players',
        flags=0, permission=0, aliases=-1,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    ),
    CommandData(
        name='me',
        description='Performs the specified action in chat',
        flags=0, permission=0, aliases=-1,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    ),
    CommandData(
        name='op',
        description='Gives the specified player operator status',
        flags=0, permission=0, aliases=-1,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    ),
    CommandData(
        name='pardon',
        description='Allows the specified player to use this server',
        flags=0, permission=0, aliases=-1,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    ),
    CommandData(
        name='pardon-ip',
        description='Allows the specified IP address to use this server',
        flags=0, permission=0, aliases=-1,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    ),
    CommandData(
        name='particle',
        description='Adds particles to a world',
        flags=0, permission=0, aliases=-1,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    ),
    CommandData(
        name='plugins',
        description='Gets a list of plugins running on the server',
        flags=0, permission=0, aliases=1,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    ),
    CommandData(
        name='reload',
        description='Reloads the server configuration and plugins',
        flags=0, permission=0, aliases=-1,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    ),
    CommandData(
        name='save-all',
        description='Saves the server to disk',
        flags=0, permission=0, aliases=-1,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    ),
    CommandData(
        name='save-off',
        description='Disables server autosaving',
        flags=0, permission=0, aliases=-1,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    ),
    CommandData(
        name='save-on',
        description='Enables server autosaving',
        flags=0, permission=0, aliases=-1,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    ),
    CommandData(
        name='say',
        description='Broadcasts the given message as the sender',
        flags=0, permission=0, aliases=-1,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    ),
    CommandData(
        name='seed',
        description='Shows the world seed',
        flags=0, permission=0, aliases=-1,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    ),
    CommandData(
        name='setworldspawn',
        description="Sets a worlds's spawn point. If no coordinates are specified, the player's coordinates will be used.",
        flags=0, permission=0, aliases=-1,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    ),
    CommandData(
        name='spawnpoint',
        description="Sets a player's spawn point",
        flags=0, permission=0, aliases=-1,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    ),
    CommandData(
        name='stop',
        description='Stops the server',
        flags=0, permission=0, aliases=-1,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    ),
    CommandData(
        name='tp',
        description='Teleports the given player (or yourself) to another player or coordinates',
        flags=0, permission=0, aliases=-1,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    ),
    CommandData(
        name='tell',
        description='Sends a private message to the given player',
        flags=0, permission=0, aliases=2,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    ),
    CommandData(
        name='time',
        description='Changes the time on each world',
        flags=0, permission=0, aliases=-1,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    ),
    CommandData(
        name='timings',
        description='Records timings to see performance of the server.',
        flags=0, permission=0, aliases=-1,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    ),
    CommandData(
        name='title',
        description='Controls screen titles',
        flags=0, permission=0, aliases=-1,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    ),
    CommandData(
        name='transferserver',
        description='Transfer yourself to another server',
        flags=0, permission=0, aliases=-1,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    ),
    CommandData(
        name='version',
        description='Gets the version of this server including any plugins in use',
        flags=0, permission=0, aliases=3,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    ),
    CommandData(
        name='whitelist',
        description='Manages the list of players allowed to use this server',
        flags=0, permission=0, aliases=-1,
        overloads=(
            (
                CommandParameter(name='args', type=1048593, is_optional=True),),)
    )
)


class CommandSpec:

    @property
    def enum_values(self) -> Tuple[str, ...]:
        return _ENUM_VALUES

    @property
    def postfixes(self) -> Tuple[str, ...]:
        return _POSTFIXES

    @property
    def enums(self) -> Tuple[CommandEnum, ...]:
        return _ENUMS

    @property
    def command_data(self) -> Tuple[CommandData, ...]:
        return _COMMAND_DATA

    @property
    def permission(self) -> CommandPermission:
        return CommandPermission.NORMAL


_INSTANCE = CommandSpec()


def get_command_spec() -> CommandSpec:
    return _INSTANCE
