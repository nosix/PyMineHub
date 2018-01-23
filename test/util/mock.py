import asyncio
from collections import deque
from pkgutil import get_data
from typing import Callable, Optional, Tuple, Union

from pyminehub.mcpe.action import Action, ActionType
from pyminehub.mcpe.chunk import Chunk
from pyminehub.mcpe.command import *
from pyminehub.mcpe.const import GameMode, Difficulty
from pyminehub.mcpe.datastore import DataStore
from pyminehub.mcpe.event import *
from pyminehub.mcpe.geometry import *
from pyminehub.mcpe.value import *
from pyminehub.mcpe.world import WorldProxy
from pyminehub.network.address import Address
from pyminehub.typevar import ET

CHUNK_DATA = get_data(__package__, 'chunk_data.dat')


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

    def perform_action(self, action: Action) -> None:
        raise NotImplementedError()
