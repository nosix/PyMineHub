import collections
import functools
import json
from typing import NamedTuple as _NamedTuple, Any, Callable, Dict, List, Sequence, Tuple

from pyminehub.mcpe.const import CommandPermission, CommandArgType
from pyminehub.mcpe.geometry import Vector3
from pyminehub.mcpe.value import CommandData, CommandParameter, CommandEnum, CommandSpec

Int = int
Float = float
String = str


class Value(str):  # TODO change to accurate type
    pass


class Target(str):
    pass


class Position(Vector3[float]):

    def __new__(cls, *args) -> 'Position':
        """
        >>> Position('256.5 64 256.5')
        Position(x=256.5, y=64.0, z=256.5)
        >>> Position(256.5, 64, 256.5)
        Position(x=256.5, y=64.0, z=256.5)
        """
        argv = args[0].split() if len(args) == 1 and isinstance(args[0], str) else args
        return super().__new__(cls, *tuple(float(v) for v in argv))


class Message(str):
    pass


class Text(str):
    pass


class JSON(str):

    def decode(self) -> Dict:
        """
        >>> json = JSON('{"price": 1980, "pi": 3.14, "messages": ["foo", "bar"]}')
        >>> json.decode()
        {'price': 1980, 'pi': 3.14, 'messages': ['foo', 'bar']}
        """
        return json.loads(self)


class Command(str):
    pass


_FLAG_BASIC_TYPE = 0x100000
_FLAG_ENUM_TYPE = 0x200000
_FLAG_DYNAMIC_TYPE = 0x1000000

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


class CommandContext:

    def send_text(self, text: str, broadcast: bool=False) -> None:
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

    is_method = '.' in func.__qualname__
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
        if _func.__defaults__ is not None:
            for i in range(len(_func.__defaults__)):
                append_redirect(parameters[:-(i + 1)], _func)
        return call_overload

    def append_redirect(parameters, _func):
        if parameters in command_func.redirect:
            raise DuplicateDefinitionError(
                '{}.by({}) is duplicate.'.format(func.__name__, ', '.join(t.__name__ for t in parameters)))
        command_func.redirect[parameters] = _func

    def get_parameters(_func):
        return tuple(t for name, t in _func.__annotations__.items() if name != 'return')

    command_func.overloads = []
    command_func.overload = append_overload
    command_func.by = call_overload
    command_func.redirect = {}
    return command_func


_CommandMethod = _NamedTuple('CommandMethod', [
    ('func', Callable),
    ('self', Any)
])


class CommandRegistry:

    def __init__(self) -> None:
        self._commands = {}  # type: Dict[str, _CommandMethod]
        self._enum_values = []  # type: List[str]
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
                aliases[attr.__name__].append(command_name)
                self._append_alias(processor, command_name, attr)
        for name, alias in sorted(aliases.items()):
            self._append_enum(name + '_aliases', alias)
        for name, cmd in sorted(commands.items()):
            self._append_command(processor, name, cmd)

    def _append_alias(self, processor, name: str, command_func) -> None:
        if name in self._commands:
            raise DuplicateDefinitionError('Command "{}" is duplicate.'.format(name))
        self._commands[name] = _CommandMethod(command_func, processor)

    def _append_enum(self, name: str, values: Sequence[str]) -> None:
        start = len(self._enum_values)
        self._enum_values.extend(values)
        self._enums.append(CommandEnum(name, tuple(range(start, len(self._enum_values)))))

    def _get_enum_index(self, name: str) -> int:
        for i, e in enumerate(self._enums):
            if e.name == name:
                return i
        return -1

    def _append_command(self, processor, name: str, command_func) -> None:
        assert hasattr(command_func, 'overloads'), 'Command method must decorate by command decorator.'

        if name in self._commands:
            raise DuplicateDefinitionError('Command "{}" is duplicate.'.format(name))
        self._commands[name] = _CommandMethod(command_func, processor)

        description = command_func.__doc__.splitlines()[0] if command_func.__doc__ else 'no description'

        self._command_data.append(CommandData(
            name,
            description,
            flags=0,
            permission=0,
            aliases=self._get_enum_index(name + '_aliases'),
            overloads=tuple(self._create_command_parameters(func) for func in command_func.overloads)
        ))

    @staticmethod
    def _create_command_parameters(func) -> Tuple[CommandParameter, ...]:
        parameters = func.__annotations__.copy()
        parameters.pop('return', None)
        num_of_parameters = len(parameters)
        num_of_defaults = len(func.__defaults__) if func.__defaults__ else 0

        def has_default(index: int) -> bool:
            return index >= num_of_parameters - num_of_defaults

        def get_type_value(t) -> int:
            return _FLAG_BASIC_TYPE | _BASIC_TYPES[t]  # TODO support enum and dynamic
        return tuple(
            CommandParameter(name, get_type_value(parameters[name]), has_default(i))
            for i, name in enumerate(parameters) if parameters[name] != CommandContext)

    def get_command_spec(self) -> CommandSpec:
        return CommandSpec(
            tuple(self._enum_values),
            (),
            tuple(self._enums),
            tuple(self._command_data),
            CommandPermission.NORMAL
        )

    def execute_command(self, context: CommandContext, command_name: str, args: str) -> None:
        func, receiver = self._commands[command_name]
        return func(receiver, context, args)


class CommandContextImpl(CommandContext):

    def __init__(self, send_text: Callable[[str, bool], None]) -> None:
        self._send_text = send_text

    def send_text(self, text: str, broadcast: bool=False) -> None:
        self._send_text(text, broadcast)


if __name__ == '__main__':
    import doctest
    doctest_result = doctest.testmod()
