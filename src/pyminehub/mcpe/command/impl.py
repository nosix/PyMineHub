from typing import Callable, Union

from pyminehub.mcpe.action import Action
from pyminehub.mcpe.command.api import GameEventType, CommandContext, CommandRegistry
from pyminehub.typevar import ET

__all__ = [
    'CommandContextImpl'
]


class CommandContextImpl(CommandContext):

    def __init__(
            self,
            registry: CommandRegistry,
            send_text: Callable[[str, bool], None],
            generate_event: Callable[..., None],
            perform_action: Callable[[Action], None]
    ) -> None:
        self._registry = registry
        self._send_text = send_text
        self._generate_event = generate_event
        self._perform_action = perform_action

    def get_enum_value(self, name: str) -> Union[ET, Callable]:
        return self._registry.get_enum_value(name)

    def send_text(self, text: str, broadcast: bool=False) -> None:
        self._send_text(text, broadcast)

    def generate_event(self, event_type: GameEventType, *args, **kwargs) -> None:
        self._generate_event(event_type, *args, **kwargs)

    def perform_action(self, action: Action) -> None:
        self._perform_action(action)
