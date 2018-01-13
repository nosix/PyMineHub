import asyncio
import socket
from asyncio import subprocess
from collections import deque
from pkgutil import get_data

from pyminehub.mcpe.action import Action, ActionType
from pyminehub.mcpe.chunk import Chunk
from pyminehub.mcpe.datastore import DataStore
from pyminehub.mcpe.event import *
from pyminehub.mcpe.resource import INVENTORY_CONTENT_ITEMS121
from pyminehub.mcpe.world import WorldProxy
from pyminehub.mcpe.world.inventory import MutableInventory
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
        self._waiting_queue = deque()
        self._event_queue = asyncio.Queue()
        self._chunk_data = get_data(__package__, 'chunk_data.dat')
        self._player_id = None

    def terminate(self) -> None:
        pass

    def perform(self, action: Action) -> None:
        if action.type == ActionType.LOGIN_PLAYER:
            self._player_id = action.player_id
            self._waiting_queue.append(
                event_factory.create(
                    EventType.PLAYER_LOGGED_IN,
                    action.player_id,
                    2,
                    2,
                    GameMode.SURVIVAL,
                    Vector3(256.0, 64.0, 256.0),
                    0.0,
                    358.0,
                    Vector3(512, 56, 512),
                    Vector3(0, 0, 0),
                    PlayerPermission.MEMBER,
                    (
                        Attribute(0.0, 20.0, 20.0, 20.0, 'minecraft:health'),
                        Attribute(0.0, 2048.0, 16.0, 16.0, 'minecraft:follow_range'),
                        Attribute(0.0, 1.0, 0.0, 0.0, 'minecraft:knockback_resistance'),
                        Attribute(
                            0.0, 3.4028234663852886e+38, 0.10000000149011612, 0.10000000149011612, 'minecraft:movement'
                        ),
                        Attribute(0.0, 3.4028234663852886e+38, 1.0, 1.0, 'minecraft:attack_damage'),
                        Attribute(0.0, 3.4028234663852886e+38, 0.0, 0.0, 'minecraft:absorption'),
                        Attribute(0.0, 20.0, 10.0, 20.0, 'minecraft:player.saturation'),
                        Attribute(0.0, 5.0, 0.8000399470329285, 0.0, 'minecraft:player.exhaustion'),
                        Attribute(0.0, 20.0, 20.0, 20.0, 'minecraft:player.hunger'),
                        Attribute(0.0, 24791.0, 0.0, 0.0, 'minecraft:player.level'),
                        Attribute(0.0, 1.0, 0.0, 0.0, 'minecraft:player.experience')
                    ),
                    EntityMetaDataFlagValue.create(
                        always_show_nametag=True,
                        immobile=True,
                        swimmer=True,
                        affected_by_gravity=True,
                        fire_immune=True
                    )
                ))
            self._waiting_queue.append(
                event_factory.create(
                    EventType.INVENTORY_LOADED,
                    action.player_id,
                    (
                        MutableInventory(WindowType.INVENTORY).to_value(),
                        MutableInventory(WindowType.ARMOR).to_value(),
                        Inventory(WindowType.CREATIVE, INVENTORY_CONTENT_ITEMS121)
                    )
                ))
            self._waiting_queue.append(
                event_factory.create(
                    EventType.SLOT_INITIALIZED,
                    action.player_id,
                    0,
                    0,
                    Item(ItemType.AIR, None, None, None, None)
                ))
            return
        if action.type == ActionType.REQUEST_CHUNK:
            for position in action.positions:
                self._waiting_queue.append(event_factory.create(
                    EventType.FULL_CHUNK_LOADED, position.position, self._chunk_data))
            return
        if action.type == ActionType.REQUEST_ENTITY:
            self._waiting_queue.append(event_factory.create(
                EventType.ENTITY_LOADED,
                self._player_id,
                tuple()
            ))
            return
        if action.type == ActionType.MOVE_PLAYER:
            self._waiting_queue.append(event_factory.create(
                EventType.PLAYER_MOVED,
                action.entity_runtime_id,
                action.position,
                action.pitch,
                action.yaw,
                action.head_yaw,
                action.mode,
                action.on_ground,
                action.riding_eid
            ))
            if action.position == Vector3(x=256.5497741699219, y=63.62001037597656, z=258.473876953125):
                self._waiting_queue.append(event_factory.create(
                    EventType.INVENTORY_UPDATED,
                    self._player_id,
                    0,
                    Item.create(ItemType.DIRT, 1)
                ))
                self._waiting_queue.append(event_factory.create(
                    EventType.ENTITY_REMOVED,
                    3
                ))
                self._waiting_queue.append(event_factory.create(
                    EventType.ITEM_TAKEN,
                    3,
                    2
                ))
            return
        if action.type == ActionType.BREAK_BLOCK:
            self._waiting_queue.append(event_factory.create(
                EventType.BLOCK_UPDATED,
                action.position,
                Block.create(BlockType.AIR, 0, neighbors=True, network=True, priority=True)
            ))
            self._waiting_queue.append(event_factory.create(
                EventType.ITEM_SPAWNED,
                3,
                3,
                Item.create(ItemType.DIRT, 1),
                action.position,
                Vector3(0.0, 0.0, 0.0),
                tuple()
            ))
            return
        if action.type == ActionType.PUT_ITEM:
            self._waiting_queue.append(event_factory.create(
                EventType.BLOCK_UPDATED,
                Vector3(x=256, y=62, z=258),
                Block.create(BlockType.DIRT, 0, neighbors=True, network=True, priority=True)
            ))
            self._waiting_queue.append(event_factory.create(
                EventType.INVENTORY_UPDATED,
                self._player_id,
                0,
                Item.create(ItemType.AIR, 0)
            ))
            return
        if action.type == ActionType.EQUIP:
            self._waiting_queue.append(event_factory.create(
                EventType.EQUIPMENT_UPDATED,
                2,
                0,
                0,
                action.item
            ))
            return
        if action.type == ActionType.LOGOUT_PLAYER:
            # TODO
            raise NotImplementedError()
        if action.type == ActionType.SET_HOTBAR:
            # TODO
            raise NotImplementedError()

    def put_next_event(self) -> None:
        if len(self._waiting_queue) > 0:
            self._event_queue.put_nowait(self._waiting_queue.popleft())

    async def next_event(self) -> Optional[Event]:
        return await self._event_queue.get()

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
