from typing import Any


__all__ = [
    'ExtraCommandPlugin'
]


class ExtraCommandPlugin:

    @property
    def processor(self) -> Any:
        """Return command processor.

        See `plugin/about`, `plugin/action` and/or `plugin/event`.

        :return: command processor that has methods with command decorator (see `pyminehub.mcpe.command`)
        """
        raise NotImplementedError()
