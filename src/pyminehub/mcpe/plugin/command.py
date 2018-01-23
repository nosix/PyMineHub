from typing import Any


__all__ = [
    'ExtraCommandPlugin'
]


class ExtraCommandPlugin:

    @property
    def processor(self) -> Any:
        raise NotImplementedError()
