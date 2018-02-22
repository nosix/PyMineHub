import asyncio

from pyminehub.network.handler import GameDataHandler

__all__ = [
    'Server',
    'ServerProcess'
]


class Server:

    def start(self) -> None:
        raise NotImplementedError()

    def terminate(self) -> None:
        raise NotImplementedError()

    def close(self) -> None:
        raise NotImplementedError()


class ServerProcess:

    def __init__(self, handler: GameDataHandler, *servers: Server) -> None:
        self._handler = handler
        self._servers = servers
        self._stopped = False

    def __enter__(self) -> 'ServerProcess':
        for server in self._servers:
            server.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        loop = asyncio.get_event_loop()
        try:
            if exc_type is None and not self._stopped:
                loop.run_forever()  # blocking
        except KeyboardInterrupt:
            pass
        finally:
            self._handler.terminate()
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
            server.close()

    def start(self) -> None:
        self.__enter__()

    def join(self) -> None:
        self.__exit__(None, None, None)

    def stop(self) -> None:
        self._stopped = True
        for task in asyncio.Task.all_tasks():
            task.cancel()
