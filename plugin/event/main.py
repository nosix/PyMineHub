from logging import getLogger
from typing import Any

from pyminehub.mcpe.command.annotation import *
from pyminehub.mcpe.command.api import *
from pyminehub.mcpe.const import SoundType, SpaceEventType, EntityEventType
from pyminehub.mcpe.plugin.command import ExtraCommandPlugin

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
