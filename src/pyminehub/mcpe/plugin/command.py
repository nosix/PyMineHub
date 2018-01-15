from typing import Any


class ExtraCommandPlugin:

    @property
    def processor(self) -> Any:
        raise NotImplementedError()
