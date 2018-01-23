from typing import Any

from pyminehub.mcpe.command import *
from pyminehub.mcpe.plugin.command import ExtraCommandPlugin


class AboutCommandProcessor:

    @command
    def about(self, context: CommandContext, args: str) -> None:
        """Show about server."""
        try:
            self._about(context, Int(args))
        except ValueError:
            self._about(context, Message(args))

    @about.overload
    def _about(self, context: CommandContext, info_type: Int) -> None:
        context.send_text('This is about description by int {}.'.format(info_type))  # TODO implement this

    @about.overload
    def _about(self, context: CommandContext, info_type: Message= '') -> None:
        context.send_text('This is about description by message {}.'.format(info_type))  # TODO implement this


class AboutCommandPlugin(ExtraCommandPlugin):

    @property
    def processor(self) -> Any:
        return AboutCommandProcessor()
