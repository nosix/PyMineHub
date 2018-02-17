import asyncio
import re
import time
from logging import getLogger
from typing import Dict, Optional, Tuple

from pyminehub.config import ConfigKey, get_value
from pyminehub.mcpe.action import Action, ActionType, action_factory
from pyminehub.mcpe.attribute import create_attribute
from pyminehub.mcpe.chunk import encode_chunk
from pyminehub.mcpe.const import *
from pyminehub.mcpe.datastore import DataStore
from pyminehub.mcpe.event import *
from pyminehub.mcpe.geometry import Vector3, revise_angle
from pyminehub.mcpe.plugin.loader import PluginLoader
from pyminehub.mcpe.plugin.mob import *
from pyminehub.mcpe.plugin.player import PlayerConfigPlugin
from pyminehub.mcpe.value import *
from pyminehub.mcpe.world.clock import Clock
from pyminehub.mcpe.world.entity import EntityPool, PlayerEntity
from pyminehub.mcpe.world.generator import SpaceGenerator
from pyminehub.mcpe.world.interface import WorldEditor
from pyminehub.mcpe.world.item import get_item_spec
from pyminehub.mcpe.world.proxy import WorldProxy
from pyminehub.mcpe.world.space import Space
from pyminehub.value import LogString

__all__ = [
    'run'
]


_logger = getLogger(__name__)


def _camel_to_snake(s: str) -> str:
    return re.sub(r'([A-Z])', r'_\1', s).lower().lstrip('_')


class _World(WorldEditor):

    def __init__(
            self,
            game_mode: GameMode,
            generator: SpaceGenerator,
            store: DataStore,
            mob_processor: MobProcessorPlugin,
            player_config: PlayerConfigPlugin
    ) -> None:
        self._game_mode = game_mode
        self._space = Space(generator, store)
        self._entity = EntityPool(store)
        self._mob_processor = mob_processor
        self._player_config = player_config
        self._event_queue = asyncio.Queue()
        self._mob_id_to_entity_id = {}  # type: Dict[MobID, EntityRuntimeID]
        asyncio.get_event_loop().call_soon(self._space.init_space)
        self._clock = Clock(self._notify_time)
        self._update_task = self._start_loop_to_update()
        self._clock_task = self._start_clock()

    def _start_loop_to_update(self) -> asyncio.Task:
        async def loop_to_update():
            while True:
                await self._next_moment()
        return asyncio.ensure_future(loop_to_update())

    def _start_clock(self) -> asyncio.Task:
        return asyncio.ensure_future(self._clock.run_loop())

    # WorldProxy methods

    def terminate(self) -> None:
        self._clock_task.cancel()
        self._update_task.cancel()
        self._space.save()

    def perform(self, action: Action) -> None:
        _logger.debug('>> %s', LogString(action))
        asyncio.get_event_loop().call_soon(
            getattr(self, '_process_' + action.type.name.lower()), action)

    async def next_event(self) -> Optional[Event]:
        event = await self._event_queue.get()
        _logger.debug('<< %s', LogString(event))
        return event

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
        slot_item = player.get_item(inventory_slot)
        self._notify_event(event_factory.create(
            EventType.INVENTORY_UPDATED,
            player.player_id,
            inventory_slot,
            slot_item
        ))

    # local methods

    def _notify_event(self, event: Event) -> None:
        self._event_queue.put_nowait(event)

    def _notify_time(self, mc_time: int) -> None:
        self._notify_event(event_factory.create(EventType.TIME_UPDATED, mc_time))

    async def _next_moment(self) -> None:
        start_time = time.time()
        if get_value(ConfigKey.SPAWN_MOB):
            self._update_mob()
        run_time = time.time() - start_time
        tick_time = get_value(ConfigKey.WORLD_TICK_TIME)
        if run_time < tick_time:
            await asyncio.sleep(tick_time - run_time)

    def _update_mob(self) -> None:
        actions = self._mob_processor.update(
            self._get_player_info(),
            self._get_mob_info()
        )
        for action in actions:
            getattr(self, '_process_' + _camel_to_snake(action.__class__.__name__))(action)

    def _get_player_info(self) -> Tuple[PlayerInfo, ...]:
        def to_plugin_id(player: PlayerEntity):
            return player.entity_runtime_id  # TODO change other ID
        return tuple(
            PlayerInfo(to_plugin_id(p), p.position, p.pitch, p.yaw, p.head_yaw)
            for p in self._entity.players)

    def _get_mob_info(self) -> Tuple[MobInfo, ...]:
        return tuple(
            MobInfo(mob_id, self._entity.get_mob(entity_runtime_id).position, tuple())  # TODO pass chunk data
            for mob_id, entity_runtime_id in self._mob_id_to_entity_id.items())

    # action handling methods

    def _process_login_player(self, action: Action) -> None:
        entity_runtime_id = self._entity.load_player(action.player_id)
        entity = self._entity.get_player(entity_runtime_id)
        height = self._space.get_height(entity.spawn_position)
        if not entity.is_living:
            entity.spawn(height)

        self._notify_event(event_factory.create(
            EventType.PLAYER_LOGGED_IN,
            entity.player_id,
            entity.entity_unique_id,
            entity_runtime_id,
            self._player_config.get_game_mode(self._game_mode, entity.player_id),
            entity.position,
            entity.pitch,
            entity.yaw,
            entity.spawn_position,
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
            ),
            self._clock.time
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
            entity.get_inventory_slot(entity.hotbar_slot),
            entity.hotbar_slot,
            entity.equipped_item
        ))

    def _process_logout_player(self, action: Action) -> None:
        self._entity.remove(action.entity_runtime_id)

    def _process_request_chunk(self, action: Action) -> None:
        for request in action.positions:
            chunk = self._space.get_chunk(request)
            self._notify_event(event_factory.create(
                EventType.FULL_CHUNK_LOADED, request.position, encode_chunk(chunk)))

    def _process_request_entity(self, action: Action) -> None:
        player = self._entity.get_player(action.player_runtime_id)
        events = []
        events.extend(event_factory.create(
            EventType.ITEM_SPAWNED,
            item.entity_unique_id,
            item.entity_runtime_id,
            item.item,
            item.position,
            Vector3(0.0, 0.0, 0.0),
            tuple()
        ) for item in self._entity.items)
        events.extend(event_factory.create(
            EventType.MOB_SPAWNED,
            mob.entity_unique_id,
            mob.entity_runtime_id,
            mob.type,
            mob.position,
            mob.pitch,
            mob.yaw,
            mob.name,
            None  # TODO set owner
        ) for mob in self._entity.mobs)
        self._notify_event(event_factory.create(
            EventType.ENTITY_LOADED,
            player.player_id,
            tuple(events)
        ))

    def _process_move_player(self, action: Action) -> None:
        player = self._entity.get_player(action.entity_runtime_id)
        player.position = action.position
        player.pitch = revise_angle(action.pitch)
        player.yaw = revise_angle(action.yaw)
        player.head_yaw = revise_angle(action.head_yaw)
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
        updated_blocks, items = self._space.break_block(action.position)
        if len(updated_blocks) > 0:
            self._notify_event(event_factory.create(
                EventType.BLOCK_UPDATED,
                tuple(updated_blocks)
            ))
        if self._game_mode == GameMode.CREATIVE:
            return
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
        inventory_slot = player.get_inventory_slot(action.hotbar_slot)
        assert inventory_slot is not None
        if self._game_mode != GameMode.CREATIVE:
            old_slot, new_slot = player.spend_item(inventory_slot, action.item)
        else:
            old_slot = player.get_item(inventory_slot)
            new_slot = old_slot
            assert action.item == new_slot, '{}, {}'.format(action.item, new_slot)
        block = get_item_spec(old_slot.type).to_block(
            old_slot.data, action.face, player.yaw, action.click_position)
        if block is not None:
            updated = self._space.put_block(action.position, action.face, block)
            if len(updated) > 0:
                self._notify_event(event_factory.create(
                    EventType.BLOCK_UPDATED,
                    tuple(updated)
                ))
        self._notify_event(event_factory.create(
            EventType.INVENTORY_UPDATED,
            player.player_id,
            inventory_slot,
            new_slot
        ))

    def _process_equip(self, action: Action) -> None:
        player = self._entity.get_player(action.entity_runtime_id)
        player.equip(action.hotbar_slot, action.inventory_slot)
        if self._game_mode != GameMode.CREATIVE:
            assert action.item == player.equipped_item, '{}, {}'.format(action.item, player.equipped_item)
        self._notify_event(event_factory.create(
            EventType.EQUIPMENT_UPDATED,
            player.entity_runtime_id,
            player.get_inventory_slot(player.hotbar_slot),
            action.hotbar_slot,
            action.item
        ))

    def _process_set_hotbar(self, action: Action) -> None:
        player = self._entity.get_player(action.entity_runtime_id)
        player.hotbar = action.hotbar
        player.hotbar_slot = action.hotbar_slot

    def _process_spawn_mob(self, action: Action, mob_id: Optional[MobID]=None) -> None:
        entity_runtime_id = self._entity.create_mob(action.entity_type)
        if mob_id is not None:
            self._mob_id_to_entity_id[mob_id] = entity_runtime_id
        mob = self._entity.get_mob(entity_runtime_id)
        mob.name = action.name
        mob.position = self._space.revise_position(action.position)
        mob.pitch = revise_angle(action.pitch)
        mob.yaw = revise_angle(action.yaw)
        # TODO set monitor_nearby_chunks
        self._notify_event(event_factory.create(
            EventType.MOB_SPAWNED,
            mob.entity_unique_id,
            mob.entity_runtime_id,
            mob.type,
            mob.position,
            mob.pitch,
            mob.yaw,
            mob.name,
            action.owner_runtime_id
        ))

    def _process_move_mob(self, action: Action) -> None:
        mob = self._entity.get_mob(action.entity_runtime_id)
        mob.position = self._space.revise_position(action.position)
        mob.pitch = revise_angle(action.pitch)
        mob.yaw = revise_angle(action.yaw)
        self._notify_event(event_factory.create(
            EventType.MOB_MOVED,
            mob.entity_runtime_id,
            mob.position,
            mob.pitch,
            mob.yaw,
            mob.on_ground
        ))

    def _process_set_inventory(self, action: Action) -> None:
        player = self._entity.get_player(action.entity_runtime_id)
        inventory_slot = action.inventory_slot
        player.set_item(inventory_slot, action.item)
        self._notify_event(event_factory.create(
            EventType.INVENTORY_UPDATED,
            player.player_id,
            inventory_slot,
            player.get_item(inventory_slot)
        ))

    # mob action handle methods

    def _process_mob_spawn(self, action: MobSpawn) -> None:
        self._process_spawn_mob(
            action_factory.create(
                ActionType.SPAWN_MOB,
                action.type,
                action.position,
                action.pitch,
                action.yaw,
                action.name,
                None
            ),
            action.mob_id,
            # TODO pass action.monitor_nearby_chunks
        )

    def _process_mob_move(self, action: MobMove) -> None:
        entity_runtime_id = self._mob_id_to_entity_id[action.mob_id]
        self._process_move_mob(
            action_factory.create(
                ActionType.MOVE_MOB,
                entity_runtime_id,
                action.position,
                action.pitch,
                action.yaw
            )
        )


class _WorldProxyImpl(WorldProxy):

    def __init__(
            self,
            generator: SpaceGenerator,
            store: DataStore,
            mob_processor: MobProcessorPlugin,
            player_config: PlayerConfigPlugin
    ) -> None:
        self._world = _World(self.get_game_mode(), generator, store, mob_processor, player_config)

    def terminate(self) -> None:
        self._world.terminate()

    def perform(self, action: Action) -> None:
        self._world.perform(action)

    async def next_event(self) -> Optional[Event]:
        return await self._world.next_event()

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

    def get_adventure_settings(self) -> AdventureSettings:
        return AdventureSettings(32, 4294967295)


def run(store: DataStore, plugin: PluginLoader) -> WorldProxy:
    from pyminehub.mcpe.world.generator import BatchSpaceGenerator, OnDemandSpaceGenerator
    space_size = get_value(ConfigKey.INIT_SPACE)
    generator = OnDemandSpaceGenerator(plugin.generator, store) if space_size is None \
        else BatchSpaceGenerator(plugin.generator, store, *space_size)
    world = _WorldProxyImpl(
        generator,
        store,
        plugin.mob_processor,
        plugin.player_config
    )
    return world
