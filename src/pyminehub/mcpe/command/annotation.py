import json
from typing import Dict

from pyminehub.mcpe.geometry import Vector3

__all__ = [
    'Int',
    'Float',
    'String',
    'Value',
    'Target',
    'Position',
    'Message',
    'Text',
    'JSON',
    'Command'
]


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
        >>> sorted(json.decode().items())
        [('messages', ['foo', 'bar']), ('pi', 3.14), ('price', 1980)]
        """
        return json.loads(self)


class Command(str):
    pass


if __name__ == '__main__':
    import doctest
    doctest_result = doctest.testmod()
