from pyminehub.mcpe.command import *
from pyminehub.mcpe.plugin.command import *


class AboutCommandProcessor:

    @command
    def about(self) -> CommandReturnValue:
        """Show about server."""
        def show_about(context: CommandContext) -> None:
            context.send_text('This is about description.')  # TODO implement this
        return show_about


class AboutCommandPlugin(ExtraCommandPlugin):

    @property
    def processor(self) -> Any:
        return AboutCommandProcessor()
