from typing import TypeVar, Generic

from pyminehub.network.address import Address
from pyminehub.network.handler import GameDataHandler

__all__ = [
    'AbstractClient',
    'Client',
    'ClientConnection'
]


class AbstractClient:

    @property
    def handler(self) -> GameDataHandler:
        raise NotImplementedError()

    async def start(self, server_addr: Address) -> None:
        """Start client

        This method is called when connection started.
        """
        raise NotImplementedError()

    async def finished(self) -> None:
        """Callback when client finish

        This method is called when client finish.
        """
        raise NotImplementedError()


Client = TypeVar('Client', bound=AbstractClient)


class ClientConnection(Generic[Client]):

    def __enter__(self) -> Client:
        raise NotImplementedError()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        raise NotImplementedError()

    def start(self) -> Client:
        # noinspection PyTypeChecker
        return self.__enter__()  # FIXME why is type check fail?

    def close(self) -> None:
        self.__exit__(None, None, None)
