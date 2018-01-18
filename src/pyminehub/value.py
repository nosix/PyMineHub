from enum import Enum
from typing import NamedTuple as _NamedTuple, Callable, Dict, Iterable, Sequence, Tuple, Union

from pyminehub.config import ConfigKey, get_value

ValueType = Enum

ValueObject = Union[tuple, _NamedTuple('ValueObject', [])]  # To suppress warnings, NamedTuple is specified.


def _snake2camel(name: str) -> str:
    return ''.join(s.title() for s in name.split('_'))


class ValueObjectFactory:

    def __init__(
            self,
            module_globals: Dict,
            value_specs: Dict[ValueType, Sequence[Tuple[str, type]]],
            cls_prefix: str=''
    ) -> None:
        """Build a factory with the specified specification.

        :param module_globals: it register NamedTuple classes in this dictionary.
        :param value_specs: tuple has attribute name and attribute type pair.
        :param cls_prefix: it append prefix to class name of the NamedTuple class.
        """
        self._factory = dict(
            (
                value_type,
                self._create_namedtuple_factory(module_globals, value_type, field_names, cls_prefix)
            )
            for value_type, field_names in value_specs.items())

    @staticmethod
    def _create_namedtuple_factory(
            module_globals: Dict,
            value_type: ValueType,
            field_names: Iterable[Tuple[str, type]],
            cls_prefix: str
    ) -> Callable[..., ValueObject]:
        cls_name = cls_prefix + _snake2camel(value_type.name)
        assert cls_name not in module_globals, cls_name
        cls = _NamedTuple(cls_name, field_names)
        cls.__module__ = module_globals['__name__']  # for pickle
        module_globals[cls_name] = cls  # for pickle

        def namedtuple_factory(*args, **kwargs) -> ValueObject:
            try:
                # noinspection PyCallingNonCallable
                return cls(*args, **kwargs)
            except TypeError as exc:
                exc.args = ('{}.{}'.format(cls_name, exc.args[0]), )
                raise exc

        return namedtuple_factory

    def create(self, value_type: ValueType, *args, **kwargs) -> ValueObject:
        """Create value object.

        >>> factory.create(PacketType.pong, 8721, 5065, True, 'MCPE;')
        Pong(type=<PacketType.pong: 28>, time=8721, guid=5065, is_valid=True, server_id='MCPE;')
        """
        return self._factory[value_type](value_type, *args, **kwargs)


class LogString:
    """For lazy evaluation when logging."""

    def __init__(self, value: ValueObject) -> None:
        self._value = value

    def __str__(self) -> str:
        max_length = get_value(ConfigKey.MAX_LOG_LENGTH)
        return str(self._value) if max_length is None else str(self._value)[:max_length]


if __name__ == '__main__':
    class PacketType(ValueType):
        pong = 0x1c

    _packet_specs = {
        PacketType.pong: [
            ('type', PacketType),
            ('time', int),
            ('guid', bytes),
            ('is_valid', bool),
            ('server_id', str)
        ]
    }

    factory = ValueObjectFactory(globals(), _packet_specs)

    import doctest
    doctest_result = doctest.testmod()
