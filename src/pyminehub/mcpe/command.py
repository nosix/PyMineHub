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
        name='kill',
        description='Commit suicide or kill other players',
        flags=0, permission=0, aliases=0,
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
        name='tell',
        description='Sends a private message to the given player',
        flags=0, permission=0, aliases=2,
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
