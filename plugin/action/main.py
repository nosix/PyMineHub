from binascii import unhexlify
from pickle import loads
from typing import Any

from pyminehub.mcpe.command.annotation import String
from pyminehub.mcpe.command.api import *
from pyminehub.mcpe.plugin.command import *


class ActionCommandProcessor:

    @command
    def perform(self, context: CommandContext, args: str) -> None:
        """Perform action in the world."""
        self._perform(context, String(args))

    @perform.overload
    def _perform(self, context: CommandContext, data: String) -> None:
        action = loads(unhexlify(data))
        context.perform_action(action)


class ActionCommandPlugin(ExtraCommandPlugin):

    @property
    def processor(self) -> Any:
        return ActionCommandProcessor()
