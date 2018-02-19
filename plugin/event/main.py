from logging import getLogger
from typing import Any

from pyminehub.mcpe.command.annotation import *
from pyminehub.mcpe.command.api import *
from pyminehub.mcpe.const import SoundType, SpaceEventType, EntityEventType
from pyminehub.mcpe.geometry import Vector3
from pyminehub.mcpe.main.client import connect
from pyminehub.mcpe.network import MCPEClient
from pyminehub.mcpe.plugin.command import ExtraCommandPlugin
from pyminehub.mcpe.value import EntityRuntimeID

_logger = getLogger(__name__)


class GameEventCommandProcessor:

    @command
    def sound_event(self, context: CommandContext, args: str) -> None:
        """Generate a sound event."""
        try:
            event_type, x, y, z, data, pitch = args.split()
            self._sound_event(context, context.get_enum_value(event_type), Position(x, y, z), Int(data), Int(pitch))
        except ValueError:
            _logger.error('Failed command: /sound_event %s', args)

    @sound_event.overload
    def _sound_event(
            self,
            context: CommandContext,
            event_type: SoundType,
            position: Position,
            data: Int,
            pitch: Int
    ) -> None:
        context.generate_event(GameEventType.SOUND, event_type, position, data, pitch, False, False)

    @command
    def space_event(self, context: CommandContext, args: str) -> None:
        """Generate a space event."""
        try:
            event_type, x, y, z, data = args.split()
            self._space_event(context, context.get_enum_value(event_type), Position(x, y, z), Int(data))
        except ValueError:
            _logger.error('Failed command: /space_event %s', args)

    @space_event.overload
    def _space_event(self, context: CommandContext, event_type: SpaceEventType, position: Position, data: Int) -> None:
        context.generate_event(GameEventType.SPACE, event_type, position, data)

    @command
    def entity_event(self, context: CommandContext, args: str) -> None:
        """Generate a entity event."""
        try:
            event_type, eid, data = args.split()
            self._entity_event(context, context.get_enum_value(event_type), Int(eid), Int(data))
        except ValueError:
            _logger.error('Failed command: /entity_event %s', args)

    @entity_event.overload
    def _entity_event(self, context: CommandContext, event_type: EntityEventType, eid: Int, data: Int) -> None:
        context.generate_event(GameEventType.ENTITY, eid, event_type, data)


class GameEventCommandPlugin(ExtraCommandPlugin):

    @property
    def processor(self) -> Any:
        return GameEventCommandProcessor()


class GameEventCommandMixin:

    @property
    def client(self) -> MCPEClient:
        raise NotImplementedError()

    def sound_event(
            self,
            event_type: SoundType,
            position: Vector3[float],
            data: int=0,
            pitch: int=0
    ) -> None:
        x, y, z = position
        self.client.execute_command(
            '/sound_event {} {} {} {} {} {}'.format(
                event_type.name.lower(), x, y, z, data, pitch))

    def space_event(
            self,
            event_type: SpaceEventType,
            position: Vector3[float],
            data: int=0
    ) -> None:
        x, y, z = position
        self.client.execute_command(
            '/space_event {} {} {} {} {}'.format(
                event_type.name.lower(), x, y, z, data))

    def entity_event(
            self,
            event_type: EntityEventType,
            entity_runtime_id: EntityRuntimeID,
            data: int=0
    ) -> None:
        self.client.execute_command(
            '/entity_event {} {} {}'.format(
                event_type.name.lower(), entity_runtime_id, data))


class GameEventCommandClient(MCPEClient, GameEventCommandMixin):

    @property
    def client(self) -> MCPEClient:
        return self


if __name__ == '__main__':
    import time

    with connect('127.0.0.1', client_factory=GameEventCommandClient) as _client:
        _entity = _client.get_entity()

        for e in _client.entities:
            if e.entity_runtime_id != _client.entity_runtime_id:
                _entity = e
                break
        else:
            print('Login by other player, please.')

        _client.sound_event(SoundType.HURT, _entity.position)
        time.sleep(1)

        _client.space_event(SpaceEventType.SOUND_GHAST, _entity.position)
        time.sleep(1)

        _client.entity_event(EntityEventType.HURT_ANIMATION, _entity.entity_runtime_id)
        time.sleep(1)
