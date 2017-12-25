import asyncio
import socket
from asyncio import subprocess
from collections import deque
from pkgutil import get_data
from typing import List

from pyminehub.mcpe.world import WorldProxy
from pyminehub.mcpe.world.action import Action, ActionType
from pyminehub.mcpe.world.event import *
from pyminehub.network.address import Address


class MockEventLoop(asyncio.events.AbstractEventLoop):

    def run_forever(self):
        pass

    def run_until_complete(self, future):
        pass

    def stop(self):
        pass

    def is_running(self):
        pass

    def is_closed(self):
        pass

    def close(self):
        pass

    def shutdown_asyncgens(self):
        pass

    def _timer_handle_cancelled(self, handle):
        pass

    def call_later(self, delay, callback, *args):
        pass

    def call_at(self, when, callback, *args):
        pass

    def time(self):
        pass

    def create_future(self):
        pass

    def create_task(self, coro):
        pass

    def call_soon_threadsafe(self, callback, *args):
        pass

    def run_in_executor(self, executor, func, *args):
        pass

    def set_default_executor(self, executor):
        pass

    def getaddrinfo(self, host, port, *, family=0, type_=0, proto=0, flags=0):
        pass

    def getnameinfo(self, sockaddr, flags=0):
        pass

    def create_connection(self, protocol_factory, host=None, port=None, *, ssl=None, family=0, proto=0, flags=0,
                          sock=None, local_addr=None, server_hostname=None):
        pass

    def create_server(self, protocol_factory, host=None, port=None, *, family=socket.AF_UNSPEC, flags=socket.AI_PASSIVE,
                      sock=None, backlog=100, ssl=None, reuse_address=None, reuse_port=None):
        pass

    def create_unix_connection(self, protocol_factory, path, *, ssl=None, sock=None, server_hostname=None):
        pass

    def create_unix_server(self, protocol_factory, path, *, sock=None, backlog=100, ssl=None):
        pass

    def create_datagram_endpoint(self, protocol_factory, local_addr=None, remote_addr=None, *, family=0, proto=0,
                                 flags=0, reuse_address=None, reuse_port=None, allow_broadcast=None, sock=None):
        pass

    def connect_read_pipe(self, protocol_factory, pipe):
        pass

    def connect_write_pipe(self, protocol_factory, pipe):
        pass

    def subprocess_shell(self, protocol_factory, cmd, *, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, **kwargs):
        pass

    def subprocess_exec(self, protocol_factory, *args, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE, **kwargs):
        pass

    def add_reader(self, fd, callback, *args):
        pass

    def remove_reader(self, fd):
        pass

    def add_writer(self, fd, callback, *args):
        pass

    def remove_writer(self, fd):
        pass

    def sock_recv(self, sock, nbytes):
        pass

    def sock_sendall(self, sock, data):
        pass

    def sock_connect(self, sock, address):
        pass

    def sock_accept(self, sock):
        pass

    def add_signal_handler(self, sig, callback, *args):
        pass

    def remove_signal_handler(self, sig):
        pass

    def set_task_factory(self, factory):
        pass

    def get_task_factory(self):
        pass

    def get_exception_handler(self):
        pass

    def set_exception_handler(self, handler):
        pass

    def default_exception_handler(self, context):
        pass

    def call_exception_handler(self, context):
        pass

    def get_debug(self):
        pass

    def set_debug(self, enabled):
        pass


class MockTransport(asyncio.transports.DatagramTransport):

    def __init__(self, queue: List[Tuple[Address, bytes]]):
        super().__init__()
        self._queue = queue

    def sendto(self, data: bytes, addr: Address=None) -> None:
        self._queue.append((addr, data))

    def abort(self):
        pass

    def is_closing(self):
        pass

    def close(self):
        pass

    def set_protocol(self, protocol):
        pass

    def get_protocol(self):
        pass


class MockWorldProxy(WorldProxy):

    def __init__(self) -> None:
        self._event_queue = deque()
        self._chunk_data = get_data(__package__, 'chunk_data.dat')

    def perform(self, action: Action) -> None:
        if ActionType(action.id) == ActionType.LOGIN_PLAYER:
            self._event_queue.append(
                event_factory.create(
                    EventType.PLAYER_LOGGED_IN,
                    action.player_id,
                    1,
                    1,
                    GameMode.SURVIVAL,
                    Vector3(256.0, 57.625, 256.0),
                    0.0,
                    358.0,
                    Vector3(512, 56, 512),
                    PlayerPermission.MEMBER
                ))
            return
        if ActionType(action.id) == ActionType.UNKNOWN1:
            self._event_queue.append(
                event_factory.create(EventType.UNKNOWN1, action.player_id))
            return
        if ActionType(action.id) == ActionType.UNKNOWN2:
            self._event_queue.append(
                event_factory.create(EventType.UNKNOWN2, action.player_id))
            return
        if ActionType(action.id) == ActionType.REQUEST_CHUNK:
            for position in action.positions:
                self._event_queue.append(event_factory.create(
                    EventType.FULL_CHUNK_LOADED, position.position, self._chunk_data))
            return

    def next_event(self) -> Optional[Event]:
        try:
            return self._event_queue.popleft()
        except IndexError:
            return None

    def get_seed(self) -> int:
        return -1

    def get_game_mode(self) -> GameMode:
        return GameMode.SURVIVAL

    def get_difficulty(self) -> Difficulty:
        return Difficulty.NORMAL

    def get_rain_level(self) -> float:
        return 0.0

    def get_lightning_level(self) -> float:
        return 0.0

    def get_world_name(self) -> str:
        return 'PyMineHub Server'

    def get_time(self) -> int:
        return 4800
