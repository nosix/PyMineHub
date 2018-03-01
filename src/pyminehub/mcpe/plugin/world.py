from typing import Callable, Optional

from pyminehub.mcpe.action import Action
from pyminehub.mcpe.event import Event

__all__ = [
    'WorldExtensionPlugin',
    'PerformAction'
]

PerformAction = Callable[..., None]  # perform_action(action_type: ActionType, *args, **kwargs)


class WorldExtensionPlugin:

    def update(self, perform_action: PerformAction) -> None:
        raise NotImplementedError()

    # noinspection PyMethodMayBeStatic
    def filter_action(self, action: Action) -> Optional[Action]:
        return action

    # noinspection PyMethodMayBeStatic
    def filter_event(self, event: Event) -> Optional[Event]:
        return event

    def terminate(self) -> None:
        raise NotImplementedError()
