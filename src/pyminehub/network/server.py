import asyncio
import logging

from pyminehub.network.address import Address
from pyminehub.network.handler import GameDataHandler, SessionNotFound

__all__ = [
    'Server',
    'ServerProcess'
]


_logger = logging.getLogger(__name__)


class Server:

    def start(self) -> None:
        raise NotImplementedError()

    def terminate(self) -> None:
        raise NotImplementedError()

    async def close(self) -> None:
        raise NotImplementedError()

    def remove_session(self, addr: Address) -> bool:
        """Remove the session with the specified address

        :param addr: target address
        :return: True if session is removed
        """
        raise NotImplementedError()


class ServerProcess:

    def __init__(self, handler: GameDataHandler, *servers: Server) -> None:
        self._handler = handler
        self._servers = servers
        self._stopped = False
        self._update_task = None

    def __enter__(self) -> 'ServerProcess':
        for server in self._servers:
            server.start()
        self._update_task = self._start_loop_to_update()
        return self

    def _start_loop_to_update(self) -> asyncio.Task:
        async def loop_to_update():
            while True:
                await self._next_moment()
        return asyncio.ensure_future(loop_to_update())

    async def _next_moment(self) -> None:
        try:
            await self._handler.update()
        except SessionNotFound as exc:
            if exc.addr is not None:
                _logger.info('%s session is not found.', exc.addr)
                for server in self._servers:
                    if server.remove_session(exc.addr):
                        break

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        loop = asyncio.get_event_loop()
        try:
            if exc_type is None and not self._stopped:
                loop.run_forever()  # blocking
        except KeyboardInterrupt:
            pass
        finally:
            self._handler.terminate()
            self._update_task.cancel()
            for server in self._servers:
                server.terminate()
            pending = asyncio.Task.all_tasks()
            try:
                loop.run_until_complete(asyncio.gather(*pending))
            except asyncio.CancelledError:
                pass
            finally:
                loop.run_until_complete(self._close())  # sock.close() is called with loop.call_soon()

    async def _close(self) -> None:
        for server in self._servers:
            await server.close()

    def start(self) -> None:
        self.__enter__()

    def join(self) -> None:
        self.__exit__(None, None, None)

    def stop(self) -> None:
        self._stopped = True
        for task in asyncio.Task.all_tasks():
            task.cancel()
