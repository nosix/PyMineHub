import asyncio
import socket
from asyncio import subprocess
from collections import deque
from pkgutil import get_data

from pyminehub.mcpe.action import Action, ActionType
from pyminehub.mcpe.chunk import Chunk
from pyminehub.mcpe.command import *
from pyminehub.mcpe.datastore import DataStore
from pyminehub.mcpe.event import *
from pyminehub.mcpe.world import WorldProxy
from pyminehub.network.address import Address

CHUNK_DATA = get_data(__package__, 'chunk_data.dat')


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

    def sendto(self, data: bytes, addr: Address=None) -> None:
        pass

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


class MockDataStore(DataStore):

    def __init__(self) -> None:
        self._chunk = {}
        self._player = {}

    def delete_all(self) -> None:
        self.__init__()

    @staticmethod
    def _save(key, value, dictionary: dict, insert_only: bool) -> None:
        if not insert_only or key not in dictionary:
            dictionary[key] = value

    @staticmethod
    def _load(key, dictionary: dict):
        return dictionary.get(key, None)

    def save_chunk(self, position: ChunkPosition, chunk: Chunk, insert_only=False) -> None:
        self._save(position, chunk, self._chunk, insert_only)

    def load_chunk(self, position: ChunkPosition) -> Optional[Chunk]:
        return self._load(position, self._chunk)

    def count_chunk(self) -> int:
        return len(self._chunk)

    def save_player(self, player_id: str, player: PlayerState, insert_only=False) -> None:
        self._save(player_id, player, self._player, insert_only)

    def load_player(self, player_id: str) -> Optional[PlayerState]:
        return self._load(player_id, self._player)


class MockWorldProxy(WorldProxy):

    def __init__(self) -> None:
        self._action_map = {}
        self._waiting_queue = deque()
        self._event_queue = asyncio.Queue()
        self._player_id = None

    def terminate(self) -> None:
        pass

    def push_event(self, action_type: ActionType, events: Tuple[Event, ...]) -> None:
        self._action_map[action_type] = events

    def perform(self, action: Action) -> None:
        actions = self._action_map[action.type]
        del self._action_map[action.type]
        self._waiting_queue.extend(actions)

    def put_next_event(self) -> None:
        if len(self._waiting_queue) > 0:
            self._event_queue.put_nowait(self._waiting_queue.popleft())

    async def next_event(self) -> Optional[Event]:
        try:
            return await self._event_queue.get()
        except AssertionError as exc:
            if exc.args[0].startswith('yield from'):
                raise AssertionError('no more event') from None

    def get_seed(self) -> int:
        return 0

    def get_game_mode(self) -> GameMode:
        return GameMode.SURVIVAL

    def get_difficulty(self) -> Difficulty:
        return Difficulty.NORMAL

    def get_rain_level(self) -> float:
        return 0.0

    def get_lightning_level(self) -> float:
        return 0.0

    def get_world_name(self) -> str:
        return 'PyMineHub'

    def get_time(self) -> int:
        return 4800

    def get_adventure_settings(self) -> AdventureSettings:
        return AdventureSettings(32, 4294967295)


class MockCommandProcessor:

    @command
    def ban(self, context: CommandContext, args: str) -> None:
        """Prevents the specified player from using this server"""
        pass

    @ban.overload
    def _ban(self, args: Message= '') -> None:
        pass

    @command
    def kill(self, context: CommandContext, args: str) -> None:
        """Commit suicide or kill other players"""
        pass

    @kill.overload
    def _kill(self, args: Message= '') -> None:
        pass

    @command
    def plugins(self, context: CommandContext, args: str) -> None:
        """Gets a list of plugins running on the server"""
        pass

    @plugins.overload
    def _plugins(self, args: Message= '') -> None:
        pass

    @command
    def tell(self, context: CommandContext, args: str) -> None:
        """Sends a private message to the given player"""
        pass

    @tell.overload
    def _tell(self, args: Message= '') -> None:
        pass

    @command
    def version(self, context: CommandContext, args: str) -> None:
        """Gets the version of this server including any plugins in use"""
        pass

    @version.overload
    def _version(self, args: Message= '') -> None:
        """Gets the version of this server including any plugins in use"""
        pass

    suicide = kill
    pl = plugins
    w = tell
    msg = tell
    ver = version
    about = version


class MockCommandContext(CommandContext):

    def __init__(self, registry: CommandRegistry) -> None:
        self._registry = registry
        self.text = None

    def get_enum_value(self, name: str) -> Union[ET, Callable]:
        return self._registry.get_enum_value(name)

    def send_text(self, text: str, broadcast: bool = False) -> None:
        self.text = text
