from pyminehub.mcpe.command import *
from pyminehub.mcpe.plugin.command import *


class AboutCommandProcessor:

    @command
    def about(self) -> None:
        """Show about server."""
        raise NotImplementedError()  # TODO implement this


class AboutCommandPlugin(ExtraCommandPlugin):

    @property
    def processor(self) -> Any:
        return AboutCommandProcessor()
