import collections
import functools
import inspect
from enum import Enum
from typing import Any, Callable, Dict, List, NamedTuple, Sequence, Tuple, Type, Union

from pyminehub.mcpe.action import Action
from pyminehub.mcpe.command.annotation import *
from pyminehub.mcpe.command.const import CommandPermission, CommandArgType
from pyminehub.mcpe.command.value import CommandEnum, CommandParameter, CommandData, CommandSpec
from pyminehub.typevar import ET

__all__ = [
    'to_signature',
    'GameEventType',
    'CommandContext',
    'DuplicateDefinitionError',
    'command',
    'CommandRegistry'
]

_FLAG_STATIC_TYPE = 0x100000
_FLAG_ENUM_TYPE = 0x200000
_FLAG_DYNAMIC_TYPE = 0x1000000
_MASK_TYPE_DATA = 0xfffff

_BASIC_TYPES = {
    Int: CommandArgType.INT.value,
    Float: CommandArgType.FLOAT.value,
    Value: CommandArgType.VALUE.value,
    Target: CommandArgType.TARGET.value,
    Position: CommandArgType.POSITION.value,
    String: CommandArgType.STRING.value,
    Message: CommandArgType.MESSAGE.value,
    Text: CommandArgType.TEXT.value,
    JSON: CommandArgType.JSON.value,
    Command: CommandArgType.COMMAND.value
}


def to_signature(command_data: CommandData, enums: Tuple[CommandEnum, ...]) -> Tuple[str, ...]:
    """
    >>> enums = (CommandEnum('EventType', (0, 1)),)
    >>> to_signature(\
        CommandData(name='entity_event', description='Generate a entity event.', flags=0, permission=0, aliases=-1,\
            overloads=((\
                CommandParameter(name='event_type', type=3145728, is_optional=False),\
                CommandParameter(name='eid', type=1048577, is_optional=False),\
                CommandParameter(name='data', type=1048577, is_optional=False)),)), enums)
    ('/entity_event event_type:EventType eid:int data:int',)
    """
    signatures = []
    for overload in command_data.overloads:
        param = ' '.join('{}:{}'.format(
            param.name, _type_to_str(param.type, param.is_optional, enums)) for param in overload)
        signatures.append('/{} {}'.format(command_data.name, param))
    return tuple(signatures)


def _type_to_str(type_value: int, is_optional: bool, enums: Tuple[CommandEnum, ...]) -> str:
    """
    >>> enums = (CommandEnum('EventType', (0, 1)),)
    >>> _type_to_str(3145728, False, enums)
    'EventType'
    >>> _type_to_str(1048577, False, enums)
    'int'
    >>> _type_to_str(1048577, True, enums)
    'Optional[int]'
    """
    def to_optional(base_type: str) -> str:
        return 'Optional[{}]'.format(base_type) if is_optional else base_type
    type_data = type_value & _MASK_TYPE_DATA
    if type_value & _FLAG_STATIC_TYPE:
        if type_value & _FLAG_ENUM_TYPE:
            return to_optional(enums[type_data].name)
        else:
            return to_optional(CommandArgType(type_data).name.lower())
    else:
        raise NotImplementedError()


class GameEventType(Enum):
    SOUND = 0
    SPACE = 1
    BLOCK = 2
    ENTITY = 3


class CommandContext:

    def get_enum_value(self, name: str) -> Union[ET, Callable]:
        raise NotImplementedError()

    def send_text(self, text: str, broadcast: bool=False) -> None:
        raise NotImplementedError()

    def generate_event(self, event_type: GameEventType, *args, **kwargs) -> None:
        raise NotImplementedError()

    def perform_action(self, action: Action) -> None:
        raise NotImplementedError()


class DuplicateDefinitionError(Exception):
    pass


def command(func):
    # noinspection PyUnusedLocal
    """Decorate the function that execute command.

    >>> @command
    ... def foo():
    ...    print('foo() is called')
    >>> @foo.overload
    ... def _foo(n: Int):
    ...    print('foo({}) is called'.format(n))
    >>> @foo.overload
    ... def _bar(n: Int):
    ...    print('bar({}) is called'.format(n))
    Traceback (most recent call last):
      ...
    DuplicateDefinitionError: foo.by(int) is duplicate.
    >>> foo()
    foo() is called
    >>> foo.by(1)
    foo(1) is called
    >>> foo.by(1.2)
    Traceback (most recent call last):
      ...
    TypeError: foo(float) is not found.
    >>> _foo(1)
    foo(1) is called
    """

    is_method = 'self' in inspect.signature(func).parameters
    first_argument_index = 1 if is_method else 0  # exclude self when func is method

    @functools.wraps(func)
    def command_func(*args):
        func(*args)

    def call_overload(*args):
        arguments = tuple(
            type(arg) if not isinstance(arg, CommandContext) else CommandContext
            for arg in args[first_argument_index:])
        _func = command_func.redirect.get(arguments, None)
        if _func is not None:
            _func(*args)
        else:
            raise TypeError(
                '{}({}) is not found.'.format(
                    command_func.__name__, ', '.join(t.__name__ for t in arguments)))

    def append_overload(_func):
        command_func.overloads.append(_func)
        parameters = get_parameters(_func)
        append_redirect(parameters, _func)
        num_of_parameter_with_default = sum(
            1 for p in inspect.signature(func).parameters.values() if p.default != inspect.Parameter.empty)
        for i in range(num_of_parameter_with_default):
            append_redirect(parameters[:-(i + 1)], _func)
        return call_overload

    def append_redirect(parameters, _func):
        if parameters in command_func.redirect:
            raise DuplicateDefinitionError(
                '{}.by({}) is duplicate.'.format(func.__name__, ', '.join(t.__name__ for t in parameters)))
        command_func.redirect[parameters] = _func

    def get_parameters(_func):
        parameters = list(inspect.signature(_func).parameters.values())
        if is_method:
            if len(parameters) > 0 and parameters[0].name == 'self':
                del parameters[0]
            else:
                raise AssertionError('{} must be method.'.format(_func))
        return tuple(p.annotation for p in parameters)

    command_func.overloads = []
    command_func.overload = append_overload
    command_func.by = call_overload
    command_func.redirect = {}
    return command_func


_CommandMethod = NamedTuple('CommandMethod', [
    ('func', Callable),
    ('self', Any)
])

_ENUM_IS_NOTHING = -1


class CommandRegistry:

    def __init__(self) -> None:
        self._commands = {}  # type: Dict[str, _CommandMethod]
        self._enum_values = collections.OrderedDict()  # type: Dict[str, Union[Enum, Callable]]
        self._enums = []  # type: List[CommandEnum]
        self._command_data = []  # type: List[CommandData]

    def register_command_processor(self, processor: Any) -> None:
        processor_cls = type(processor)
        command_names = tuple(attr_name for attr_name in dir(processor_cls) if not attr_name.startswith('_'))
        commands = {}
        aliases = collections.defaultdict(list)
        for command_name in command_names:
            attr = getattr(processor_cls, command_name)
            if command_name == attr.__name__:
                if command_name in commands:
                    raise DuplicateDefinitionError('Command "{}" is duplicate.'.format(command_name))
                commands[command_name] = attr
            else:
                aliases[attr.__name__].append((command_name, attr))
                self._append_alias(processor, command_name, attr)
        for name, alias in sorted(aliases.items()):
            self._append_enum(name + '_aliases', alias)
        for name, cmd in sorted(commands.items()):
            self._append_command(processor, name, cmd)

    def _append_alias(self, processor, name: str, command_func) -> None:
        if name in self._commands:
            raise DuplicateDefinitionError('Command "{}" is duplicate.'.format(name))
        self._commands[name] = _CommandMethod(command_func, processor)

    def _append_enum(self, name: str, values: Sequence[Tuple[str, Union[Enum, Callable]]]) -> int:
        start = len(self._enum_values)
        self._enum_values.update(values)
        assert len(self._enum_values) == start + len(values), 'Enum values may have duplicate name'
        index = len(self._enums)
        self._enums.append(CommandEnum(name, tuple(range(start, len(self._enum_values)))))
        return index

    def _get_enum_index(self, name: str) -> int:
        for i, e in enumerate(self._enums):
            if e.name == name:
                return i
        return _ENUM_IS_NOTHING

    @staticmethod
    def _enum_to_name_sequence(enum_cls: Type[Enum]) -> Sequence[Tuple[str, Enum]]:
        # noinspection PyTypeChecker
        return tuple((m.name.lower(), m) for m in list(enum_cls))

    def _append_command(self, processor, name: str, command_func) -> None:
        assert hasattr(command_func, 'overloads'), 'Command method must decorate by command decorator.'

        if name in self._commands:
            raise DuplicateDefinitionError('Command "{}" is duplicate.'.format(name))
        self._commands[name] = _CommandMethod(command_func, processor)

        doc = inspect.getdoc(command_func)
        description = doc.splitlines()[0] if doc else 'no description'

        self._command_data.append(CommandData(
            name,
            description,
            flags=0,
            permission=0,
            aliases=self._get_enum_index(name + '_aliases'),
            overloads=tuple(self._create_command_parameters(func) for func in command_func.overloads)
        ))

    def _create_command_parameters(self, func) -> Tuple[CommandParameter, ...]:
        parameters = list(inspect.signature(func).parameters.values())
        if len(parameters) > 0 and parameters[0].name == 'self':
            del parameters[0]

        def get_type_value(t) -> int:
            if t in _BASIC_TYPES:
                return _FLAG_STATIC_TYPE | _BASIC_TYPES[t]
            if issubclass(t, Enum):
                enum_name = t.__name__
                index = self._get_enum_index(enum_name)
                if index == _ENUM_IS_NOTHING:
                    index = self._append_enum(enum_name, self._enum_to_name_sequence(t))
                return _FLAG_STATIC_TYPE | _FLAG_ENUM_TYPE | index
            # TODO support dynamic

        return tuple(
            CommandParameter(p.name, get_type_value(p.annotation), p.default != inspect.Parameter.empty)
            for i, p in enumerate(parameters) if p.annotation != CommandContext)

    def get_command_spec(self) -> CommandSpec:
        return CommandSpec(
            tuple(self._enum_values),
            (),
            tuple(self._enums),
            tuple(self._command_data),
            CommandPermission.NORMAL
        )

    def get_enum_value(self, name: str) -> Union[ET, Callable]:
        return self._enum_values[name]

    def execute_command(self, context: CommandContext, command_name: str, args: str) -> None:
        func, receiver = self._commands[command_name]
        return func(receiver, context, args)


if __name__ == '__main__':
    import doctest
    doctest_result = doctest.testmod()
