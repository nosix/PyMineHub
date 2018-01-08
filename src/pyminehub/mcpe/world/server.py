import asyncio
from logging import getLogger

from pyminehub.config import ConfigKey, get_value
from pyminehub.mcpe.action import Action, ActionType
from pyminehub.mcpe.attribute import create_attribute
from pyminehub.mcpe.chunk import encode_chunk
from pyminehub.mcpe.event import *
from pyminehub.mcpe.world.database import DataBase
from pyminehub.mcpe.world.entity import EntityPool
from pyminehub.mcpe.world.generator import SpaceGenerator
from pyminehub.mcpe.world.interface import WorldEditor
from pyminehub.mcpe.world.proxy import WorldProxy
from pyminehub.mcpe.world.space import Space
from pyminehub.value import LogString

_logger = getLogger(__name__)


class _World(WorldProxy, WorldEditor):

    def __init__(self, loop: asyncio.AbstractEventLoop, generator: SpaceGenerator, db: DataBase) -> None:
        self._loop = loop
        self._space = Space(generator, db)
        self._entity = EntityPool()
        self._event_queue = asyncio.Queue()
        loop.call_soon(self._space.init_space)

    # WorldProxy methods

    def perform(self, action: Action) -> None:
        _logger.debug('>> %s', LogString(action))
        self._loop.call_soon(
            getattr(self, '_process_' + ActionType(action.id).name.lower()), action)

    async def next_event(self) -> Optional[Event]:
        event = await self._event_queue.get()
        _logger.debug('<< %s', LogString(event))
        return event

    def get_seed(self) -> int:
        return get_value(ConfigKey.SEED)

    def get_game_mode(self) -> GameMode:
        return GameMode[get_value(ConfigKey.GAME_MODE)]

    def get_difficulty(self) -> Difficulty:
        return Difficulty[get_value(ConfigKey.DIFFICULTY)]

    def get_rain_level(self) -> float:
        return get_value(ConfigKey.RAIN_LEVEL)

    def get_lightning_level(self) -> float:
        return get_value(ConfigKey.LIGHTNING_LEVEL)

    def get_world_name(self) -> str:
        return get_value(ConfigKey.WORLD_NAME)

    def get_time(self) -> int:
        return 4800

    def get_adventure_settings(self) -> AdventureSettings:
        return AdventureSettings(32, 4294967295)

    # WorldEditor methods

    def remove_entity(self, entity_runtime_id: EntityRuntimeID) -> None:
        self._entity.remove(entity_runtime_id)
        self._notify_event(event_factory.create(
            EventType.ENTITY_REMOVED,
            entity_runtime_id
        ))

    def append_into_player_inventory(self, entity_runtime_id: EntityRuntimeID, item: Item) -> None:
        player = self._entity.get_player(entity_runtime_id)
        inventory_slot = player.append_item(item)
        slot = player.get_item(inventory_slot)
        self._notify_event(event_factory.create(
            EventType.INVENTORY_UPDATED,
            player.player_id,
            inventory_slot,
            slot
        ))

    # local methods

    def _notify_event(self, event: Event) -> None:
        self._event_queue.put_nowait(event)

    # action handling methods

    def _process_login_player(self, action: Action) -> None:
        entity_runtime_id = self._entity.load_player(action.player_id)
        entity = self._entity.get_player(entity_runtime_id)
        height = self._space.get_height(entity.spawn_position)
        entity.spawn(height)

        self._notify_event(event_factory.create(
            EventType.PLAYER_LOGGED_IN,
            entity.player_id,
            entity.entity_unique_id,
            entity_runtime_id,
            GameMode.SURVIVAL,
            entity.position,
            entity.pitch,
            entity.yaw,
            entity.sapwn_position,
            Vector3(0, 0, 0),
            PlayerPermission.MEMBER,
            (
                create_attribute(AttributeType.HEALTH, entity.health),
                create_attribute(AttributeType.FOLLOW_RANGE, 16.0),
                create_attribute(AttributeType.KNOCKBACK_RESISTANCE, 0.0),
                create_attribute(AttributeType.MOVEMENT, 0.10000000149011612),
                create_attribute(AttributeType.ATTACK_DAMAGE, 1.0),
                create_attribute(AttributeType.ABSORPTION, 0.0),
                create_attribute(AttributeType.PLAYER_SATURATION, 10.0),
                create_attribute(AttributeType.PLAYER_EXHAUSTION, 0.8000399470329285),
                create_attribute(AttributeType.PLAYER_HUNGER, entity.hunger),
                create_attribute(AttributeType.PLAYER_LEVEL, 0.0),
                create_attribute(AttributeType.PLAYER_EXPERIENCE, 0.0)
            ),
            EntityMetaDataFlagValue.create(
                always_show_nametag=True,
                immobile=True,
                swimmer=True,
                affected_by_gravity=True,
                fire_immune=True
            )
        ))
        self._notify_event(event_factory.create(
            EventType.INVENTORY_LOADED,
            entity.player_id,
            (
                entity.get_inventory(WindowType.INVENTORY),
                entity.get_inventory(WindowType.ARMOR),
                entity.get_inventory(WindowType.CREATIVE)
            )
        ))
        self._notify_event(event_factory.create(
            EventType.SLOT_INITIALIZED,
            entity.player_id,
            Item(ItemType.AIR, None, None, None, None),
            0,
            0
        ))

    def _process_request_chunk(self, action: Action) -> None:
        for request in action.positions:
            chunk = self._space.get_chunk(request)
            self._notify_event(event_factory.create(
                EventType.FULL_CHUNK_LOADED, request.position, encode_chunk(chunk)))

    def _process_move_player(self, action: Action) -> None:
        player = self._entity.get_player(action.entity_runtime_id)
        player.position = action.position
        player.pitch = action.pitch
        player.yaw = action.yaw
        player.head_yaw = action.head_yaw
        player.on_ground = action.on_ground

        collisions = self._entity.detect_collision(player.entity_runtime_id)
        for collision in collisions:
            collision.update(self)

        self._notify_event(event_factory.create(
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

        for collision in collisions:
            self._notify_event(collision.event)

    def _process_break_block(self, action: Action) -> None:
        items = self._space.break_block(action.position)
        if items is None:
            return
        self._notify_event(event_factory.create(
            EventType.BLOCK_BROKEN,
            action.position,
            BlockType.AIR,
            BlockData.create(0, neighbors=True, network=True, priority=True)
        ))
        for item in items:
            entity_runtime_id = self._entity.create_item(item)
            entity = self._entity.get_item(entity_runtime_id)
            entity.spawn_position = action.position
            height = self._space.get_height(entity.spawn_position)
            entity.spawn(height)
            self._notify_event(event_factory.create(
                EventType.ITEM_SPAWNED,
                entity.entity_unique_id,
                entity_runtime_id,
                entity.item,
                entity.position,
                Vector3(0.0, 0.0, 0.0),
                tuple()
            ))

    def _process_put_item(self, action: Action) -> None:
        player = self._entity.get_player(action.entity_runtime_id)
        inventory_slot = player.to_inventory_slot(action.hotbar_slot)
        old_slot, new_slot = player.spend_item(inventory_slot, action.item)
        position = action.position + action.face.direction
        block_type = self._item_to_block(old_slot)
        if block_type is not None:
            self._space.put_block(position, block_type)
            self._notify_event(event_factory.create(
                EventType.BLOCK_PUT,
                position,
                block_type,
                BlockData.create(0, neighbors=True, network=True, priority=True)
            ))
        self._notify_event(event_factory.create(
            EventType.ITEM_SPENT,
            player.entity_runtime_id,
            inventory_slot,
            action.hotbar_slot,
            new_slot
        ))

    @staticmethod
    def _item_to_block(item: Item) -> Optional[BlockType]:
        try:
            return BlockType[item.type.name]
        except KeyError:
            return None


def run(loop: asyncio.AbstractEventLoop) -> WorldProxy:
    from pyminehub.mcpe.world.database import DataBase
    from pyminehub.mcpe.world.generator import BatchSpaceGenerator
    from pyminehub.mcpe.plugin import get_generator
    db = DataBase()
    world = _World(loop, BatchSpaceGenerator(get_generator()), db)
    return world
