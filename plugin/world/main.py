import random
from typing import Optional

from pyminehub.mcpe.action import Action, ActionType
from pyminehub.mcpe.block import FunctionalBlock
from pyminehub.mcpe.const import EntityType
from pyminehub.mcpe.event import Event, EventType
from pyminehub.mcpe.geometry import Vector3
from pyminehub.mcpe.plugin.world import WorldExtensionPlugin, PerformAction

try:
    from RPi import GPIO
except ImportError:
    from world.mock import GPIO


_RANGE = 16


class GPIOExtensionPlugin(WorldExtensionPlugin):

    def __init__(self) -> None:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(12, GPIO.OUT)
        GPIO.setup(13, GPIO.IN)
        self._prev_13pin_state = False

    def update(self, perform_action: PerformAction) -> None:
        value = GPIO.input(13)
        if value != self._prev_13pin_state:
            self._prev_13pin_state = value
            x = random.randint(-_RANGE, _RANGE)
            z = random.randint(-_RANGE, _RANGE)
            perform_action(ActionType.SPAWN_MOB, EntityType.CHICKEN, Vector3(x, 64.0, z), 0.0, 0.0, 'GPIO MOB', None)

    def filter_action(self, action: Action) -> Optional[Action]:
        if action.type is ActionType.MOVE_PLAYER:
            position = action.position
            if position.distance(Vector3(0.0, position.y, 0.0)) > _RANGE:
                # noinspection PyProtectedMember
                return action._replace(position=Vector3(0.0, position.y, 0.0), need_response=True)
        return action

    def filter_event(self, event: Event) -> Optional[Event]:
        if event.type is EventType.BLOCK_UPDATED:
            for updated in event.updated:
                block = FunctionalBlock(updated.block)
                if block.is_switchable:
                    print('switchable', block.is_on)
                    GPIO.output(12, GPIO.HIGH if block.is_on else GPIO.LOW)
        return event

    def terminate(self) -> None:
        GPIO.cleanup()
