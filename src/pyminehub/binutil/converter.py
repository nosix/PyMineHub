import base64
import struct
from binascii import hexlify, unhexlify
from enum import Enum
from typing import NamedTuple as _NamedTuple, Callable, Dict, Generic, Optional, Type

from pyminehub.typevar import T, BT, ET

__all__ = [
    'BytesOperationError',
    'decode_base64',
    'encode_base64',
    'dict_to_flags',
    'flags_to_dict',
    'unsign_to_sign',
    'sign_to_unsign',
    'to_bytes',
    'pop_first',
    'false_to_zero',
    'Endian',
    'DataCodecContext',
    'DataCodec',
    'ByteData',
    'ShortData',
    'TriadData',
    'IntData',
    'LongData',
    'FloatData',
    'BytesData',
    'StringData',
    'RawData',
    'VarIntData',
    'OptionalData',
    'EnumData',
    'ValueFilter'
]


class BytesOperationError(Exception):
    pass


def decode_base64(base64_encoded_data: bytes) -> bytes:
    padding_byte = ord('=')
    padding = bytes(padding_byte for _ in range(len(base64_encoded_data) % 4))
    return base64.decodebytes(base64_encoded_data + padding)


def encode_base64(data: bytes) -> bytes:
    return base64.encodebytes(data)


def dict_to_flags(enum_cls: Type[Enum], **kwargs: bool) -> int:
    """
    >>> class Settings(Enum):
    ...     FOO = 0
    ...     BAR = 1
    ...     MOO = 2
    >>> dict_to_flags(Settings, foo=True, moo=True)
    5
    """
    flags_bits = tuple(1 << enum_value.value for enum_value in enum_cls if kwargs.get(enum_value.name.lower(), False))
    return sum(flags_bits)


def flags_to_dict(enum_cls: Type[Enum], flags: int) -> Dict[str, bool]:
    """
    >>> class Settings(Enum):
    ...     FOO = 0
    ...     BAR = 1
    ...     MOO = 2
    >>> sorted(flags_to_dict(Settings, 5).items())
    [('foo', True), ('moo', True)]
    """
    return dict((enum_value.name.lower(), True) for enum_value in enum_cls if flags & (1 << enum_value.value))


def unsign_to_sign(value: int, bits=32) -> int:
    """
    >>> unsign_to_sign(-1)
    Traceback (most recent call last):
      ...
    AssertionError
    >>> unsign_to_sign(0)
    0
    >>> unsign_to_sign(2147483647)
    2147483647
    >>> unsign_to_sign(2147483648)
    -2147483648
    >>> unsign_to_sign(4294967295)
    -1
    >>> unsign_to_sign(4294967296)
    Traceback (most recent call last):
      ...
    AssertionError
    """
    assert 0 <= value < (1 << bits)
    sign_mask = 1 << (bits - 1)
    if value & sign_mask:
        mask = sign_mask - 1
        value &= mask
        return - ((value ^ mask) + 1)
    else:
        return value


def sign_to_unsign(value: int, bits=32) -> int:
    """
    >>> sign_to_unsign(0)
    0
    >>> sign_to_unsign(2147483647)
    2147483647
    >>> sign_to_unsign(2147483648)
    Traceback (most recent call last):
      ...
    AssertionError
    >>> sign_to_unsign(-1)
    4294967295
    >>> sign_to_unsign(-2147483648)
    2147483648
    >>> sign_to_unsign(-2147483649)
    Traceback (most recent call last):
      ...
    AssertionError
    """
    assert - (1 << (bits - 1)) <= value <= (1 << (bits - 1)) - 1
    mask = (1 << bits) - 1
    return value & mask


def to_bytes(hex_str: str) -> bytes:
    """ Convert hex string to bytes.

    >>> hexlify(to_bytes('00:ff:ff:00:fe:fe:fe:fe:fd:fd:fd:fd:12:34:56:78'))
    b'00ffff00fefefefefdfdfdfd12345678'
    """
    return bytes.fromhex(hex_str.replace(':', ''))


def pop_first(data: bytearray, size: int) -> bytearray:
    if len(data) < size:
        raise BytesOperationError('Data length is less than specified size. ({} < {})'.format(len(data), size))
    data_slice = slice(size)
    value = data[data_slice]
    del data[data_slice]
    return value


def false_to_zero(value: bool) -> int:
    assert not value
    return 0


class _Converter(_NamedTuple('Converter', [
    ('byte_order', str),
    ('slice_pack', Callable[[int, int], slice]),
    ('fill_zero', Callable[[bytes, bytes], bytes])
])):
    __slots__ = ()

    def pack(self, type_char: str, value: T, size: int=None) -> bytes:
        buffer = struct.pack(self.byte_order + type_char, value)
        return buffer if size is None else buffer[self.slice_pack(len(buffer), size)]

    def unpack(self, type_char: str, buffer: bytes, fill_size: int=None) -> T:
        if fill_size is not None:
            buffer = self.fill_zero(buffer, b'\x00' * fill_size)
        return struct.unpack(self.byte_order + type_char, buffer)[0]


class Endian:
    """Support bytes and value conversion.

    >>> hexlify(Endian.LITTLE.pack('h', 1))
    b'0100'
    >>> hexlify(Endian.BIG.pack('h', 1))
    b'0001'
    >>> Endian.LITTLE.unpack('h', bytes.fromhex('0100'))
    1
    >>> Endian.BIG.unpack('h', bytes.fromhex('0001'))
    1
    """

    LITTLE = _Converter('<', lambda l, n: slice(None, n), lambda buffer, zero_bytes: buffer + zero_bytes)
    BIG = _Converter('>', lambda l, n: slice(l-n, None), lambda buffer, zero_bytes: zero_bytes + buffer)


class DataCodecContext:

    def __init__(self) -> None:
        self.length = 0

    def clear(self) -> None:
        self.__init__()

    def __repr__(self) -> str:
        return str(self.__dict__)


class DataCodec(Generic[T]):

    def read(self, data: bytearray, context: DataCodecContext) -> T:
        raise NotImplementedError()

    def write(self, data: bytearray, value: T, context: DataCodecContext) -> None:
        raise NotImplementedError()


class ByteData(DataCodec[int]):
    """Convert unsigned 1 byte data.

    >>> c = ByteData()
    >>> data = bytearray()
    >>> context = DataCodecContext()
    >>> c.write(data, 255, context)
    >>> c.write(data, 127, context)
    >>> context.length
    2
    >>> hexlify(data)
    b'ff7f'
    >>> context.clear()
    >>> c.read(data, context)
    255
    >>> c.read(data, context)
    127
    >>> context.length
    2
    >>> hexlify(data)
    b''
    """

    def read(self, data: bytearray, context: DataCodecContext) -> int:
        if not len(data) > 0:
            raise BytesOperationError('Data is empty.')
        value = data.pop(0)
        context.length += 1
        return value

    def write(self, data: bytearray, value: int, context: DataCodecContext) -> None:
        data.append(value)
        context.length += 1


class ShortData(DataCodec[int]):
    """Convert unsigned 2 bytes data.

    >>> c = ShortData()
    >>> data = bytearray()
    >>> context = DataCodecContext()
    >>> c.write(data, 255, context)
    >>> c.write(data, 127, context)
    >>> context.length
    4
    >>> hexlify(data)
    b'00ff007f'
    >>> context.clear()
    >>> c.read(data, context)
    255
    >>> c.read(data, context)
    127
    >>> context.length
    4
    >>> hexlify(data)
    b''

    >>> c = ShortData(Endian.LITTLE)
    >>> data = bytearray()
    >>> context = DataCodecContext()
    >>> c.write(data, 255, context)
    >>> c.write(data, 127, context)
    >>> context.length
    4
    >>> hexlify(data)
    b'ff007f00'
    >>> context.clear()
    >>> c.read(data, context)
    255
    >>> c.read(data, context)
    127
    >>> context.length
    4
    >>> hexlify(data)
    b''
    """

    _LENGTH = 2

    def __init__(self, endian: _Converter=Endian.BIG) -> None:
        self.endian = endian

    def read(self, data: bytearray, context: DataCodecContext) -> int:
        d = pop_first(data, self._LENGTH)
        context.length += self._LENGTH
        return self.endian.unpack('H', d)

    def write(self, data: bytearray, value: int, context: DataCodecContext) -> None:
        data += self.endian.pack('H', value)
        context.length += self._LENGTH


class TriadData(DataCodec[int]):
    """Convert unsigned 3 bytes data.

    >>> c = TriadData()
    >>> data = bytearray()
    >>> context = DataCodecContext()
    >>> c.write(data, 255, context)
    >>> c.write(data, 127, context)
    >>> context.length
    6
    >>> hexlify(data)
    b'ff00007f0000'
    >>> context.clear()
    >>> c.read(data, context)
    255
    >>> c.read(data, context)
    127
    >>> context.length
    6
    >>> hexlify(data)
    b''

    >>> c = TriadData(Endian.BIG)
    >>> data = bytearray()
    >>> context = DataCodecContext()
    >>> c.write(data, 255, context)
    >>> c.write(data, 127, context)
    >>> context.length
    6
    >>> hexlify(data)
    b'0000ff00007f'
    >>> context.clear()
    >>> c.read(data, context)
    255
    >>> c.read(data, context)
    127
    >>> context.length
    6
    >>> hexlify(data)
    b''
    """

    _LENGTH = 3

    def __init__(self, endian: _Converter=Endian.LITTLE) -> None:
        self.endian = endian

    def read(self, data: bytearray, context: DataCodecContext) -> int:
        d = pop_first(data, self._LENGTH)
        context.length += self._LENGTH
        return self.endian.unpack('I', d, 1)

    def write(self, data: bytearray, value: int, context: DataCodecContext) -> None:
        data += self.endian.pack('I', value, 3)
        context.length += self._LENGTH


class IntData(DataCodec[int]):
    """Convert unsigned and signed 4 bytes data.

    >>> c = IntData()
    >>> data = bytearray()
    >>> context = DataCodecContext()
    >>> c.write(data, 255, context)
    >>> c.write(data, 127, context)
    >>> context.length
    8
    >>> hexlify(data)
    b'000000ff0000007f'
    >>> context.clear()
    >>> c.read(data, context)
    255
    >>> c.read(data, context)
    127
    >>> context.length
    8
    >>> hexlify(data)
    b''

    >>> c = IntData(Endian.LITTLE)
    >>> data = bytearray()
    >>> context = DataCodecContext()
    >>> c.write(data, 255, context)
    >>> c.write(data, 127, context)
    >>> context.length
    8
    >>> hexlify(data)
    b'ff0000007f000000'
    >>> context.clear()
    >>> c.read(data, context)
    255
    >>> c.read(data, context)
    127
    >>> context.length
    8
    >>> hexlify(data)
    b''

    >>> c = IntData(unsigned=False)
    >>> data = bytearray()
    >>> context = DataCodecContext()
    >>> c.write(data, 255, context)
    >>> c.write(data, -1, context)
    >>> context.length
    8
    >>> hexlify(data)
    b'000000ffffffffff'
    >>> context.clear()
    >>> c.read(data, context)
    255
    >>> c.read(data, context)
    -1
    >>> context.length
    8
    >>> hexlify(data)
    b''
    """

    _LENGTH = 4

    def __init__(self, endian: _Converter=Endian.BIG, unsigned=True) -> None:
        self.endian = endian
        self.unsigned = unsigned

    def read(self, data: bytearray, context: DataCodecContext) -> int:
        d = pop_first(data, self._LENGTH)
        context.length += self._LENGTH
        return self.endian.unpack('I' if self.unsigned else 'i', d)

    def write(self, data: bytearray, value: int, context: DataCodecContext) -> None:
        data += self.endian.pack('I' if self.unsigned else 'i', value)
        context.length += self._LENGTH


class LongData(DataCodec[int]):
    """Convert unsigned 8 bytes data.

    >>> c = LongData()
    >>> data = bytearray()
    >>> context = DataCodecContext()
    >>> c.write(data, 255, context)
    >>> c.write(data, 127, context)
    >>> context.length
    16
    >>> hexlify(data)
    b'00000000000000ff000000000000007f'
    >>> context.clear()
    >>> c.read(data, context)
    255
    >>> c.read(data, context)
    127
    >>> context.length
    16
    >>> hexlify(data)
    b''

    >>> c = LongData(Endian.LITTLE)
    >>> context = DataCodecContext()
    >>> data = bytearray()
    >>> c.write(data, 255, context)
    >>> c.write(data, 127, context)
    >>> context.length
    16
    >>> hexlify(data)
    b'ff000000000000007f00000000000000'
    >>> context.clear()
    >>> c.read(data, context)
    255
    >>> c.read(data, context)
    127
    >>> context.length
    16
    >>> hexlify(data)
    b''
    """

    _LENGTH = 8

    def __init__(self, endian: _Converter=Endian.BIG) -> None:
        self.endian = endian

    def read(self, data: bytearray, context: DataCodecContext) -> int:
        d = pop_first(data, self._LENGTH)
        context.length += self._LENGTH
        return self.endian.unpack('Q', d)

    def write(self, data: bytearray, value: int, context: DataCodecContext) -> None:
        data += self.endian.pack('Q', value)
        context.length += self._LENGTH


class FloatData(DataCodec[float]):
    """Convert signed 4 bytes data.

    >>> c = FloatData()
    >>> data = bytearray()
    >>> context = DataCodecContext()
    >>> c.write(data, 1.75, context)
    >>> c.write(data, -1.75, context)
    >>> context.length
    8
    >>> hexlify(data)
    b'3fe00000bfe00000'
    >>> context.clear()
    >>> c.read(data, context)
    1.75
    >>> c.read(data, context)
    -1.75
    >>> context.length
    8
    >>> hexlify(data)
    b''

    >>> c = FloatData(Endian.LITTLE)
    >>> context = DataCodecContext()
    >>> data = bytearray()
    >>> c.write(data, 1.75, context)
    >>> c.write(data, -1.75, context)
    >>> context.length
    8
    >>> hexlify(data)
    b'0000e03f0000e0bf'
    >>> context.clear()
    >>> c.read(data, context)
    1.75
    >>> c.read(data, context)
    -1.75
    >>> context.length
    8
    >>> hexlify(data)
    b''
    """

    _LENGTH = 4

    def __init__(self, endian: _Converter=Endian.BIG) -> None:
        self.endian = endian

    def read(self, data: bytearray, context: DataCodecContext) -> float:
        d = pop_first(data, self._LENGTH)
        context.length += self._LENGTH
        return self.endian.unpack('f', d)

    def write(self, data: bytearray, value: float, context: DataCodecContext):
        data += self.endian.pack('f', value)
        context.length += self._LENGTH


class BytesData(DataCodec[bytes]):
    """Convert N bytes data that has 2 bytes length data.

    >>> c = BytesData()
    >>> data = bytearray()
    >>> context = DataCodecContext()
    >>> c.write(data, unhexlify('ff00'), context)
    >>> c.write(data, unhexlify('123456'), context)
    >>> context.length
    9
    >>> hexlify(data)
    b'0002ff000003123456'
    >>> context.clear()
    >>> hexlify(c.read(data, context))
    b'ff00'
    >>> hexlify(c.read(data, context))
    b'123456'
    >>> context.length
    9
    >>> hexlify(data)
    b''

    >>> c = BytesData(ShortData(Endian.LITTLE))
    >>> data = bytearray()
    >>> context = DataCodecContext()
    >>> c.write(data, unhexlify('ff00'), context)
    >>> c.write(data, unhexlify('123456'), context)
    >>> context.length
    9
    >>> hexlify(data)
    b'0200ff000300123456'
    >>> context.clear()
    >>> hexlify(c.read(data, context))
    b'ff00'
    >>> hexlify(c.read(data, context))
    b'123456'
    >>> context.length
    9
    >>> hexlify(data)
    b''
    """

    def __init__(self, len_codec: DataCodec[int]=None) -> None:
        self._len_codec = ShortData(Endian.BIG) if len_codec is None else len_codec

    def read(self, data: bytearray, context: DataCodecContext) -> bytes:
        bytes_len = self._len_codec.read(data, context)
        d = pop_first(data, bytes_len)
        context.length += len(d)
        return bytes(d)

    def write(self, data: bytearray, value: bytes, context: DataCodecContext) -> None:
        length = len(value)
        self._len_codec.write(data, length, context)
        data += value
        context.length += length


class StringData(DataCodec[str]):
    """Convert N bytes string that has 2 bytes length data.

    >>> c = StringData()
    >>> data = bytearray()
    >>> context = DataCodecContext()
    >>> c.write(data, 'Hello', context)
    >>> c.write(data, 'マイクラ', context)
    >>> c.write(data, '', context)
    >>> context.length
    23
    >>> hexlify(data)
    b'000548656c6c6f000ce3839ee382a4e382afe383a90000'
    >>> context.clear()
    >>> c.read(data, context)
    'Hello'
    >>> c.read(data, context)
    'マイクラ'
    >>> c.read(data, context)
    ''
    >>> context.length
    23
    >>> hexlify(data)
    b''
    """

    def __init__(self, len_codec: DataCodec[int]=None, encoding: str='utf8') -> None:
        self._len_codec = ShortData(Endian.BIG) if len_codec is None else len_codec
        self.encoding = encoding

    def read(self, data: bytearray, context: DataCodecContext) -> str:
        length = self._len_codec.read(data, context)
        d = pop_first(data, length)
        context.length += length
        return str(d, self.encoding)

    def write(self, data: bytearray, value: str, context: DataCodecContext) -> None:
        bytes_data = bytes(value, self.encoding)
        length = len(bytes_data)
        self._len_codec.write(data, length, context)
        data += bytes_data
        context.length += length


class RawData(DataCodec[bytes]):
    """Convert N bytes data that does not have length data.

    >>> c = RawData()
    >>> data = bytearray()
    >>> context = DataCodecContext()
    >>> c.write(data, unhexlify('ff00'), context)
    >>> c.write(data, unhexlify('123456'), context)
    >>> context.length
    5
    >>> hexlify(data)
    b'ff00123456'
    >>> context.clear()
    >>> hexlify(c.read(data, context))
    b'ff00123456'
    >>> context.length
    5
    >>> hexlify(data)
    b''

    >>> c = RawData(data_len=2)
    >>> data = bytearray()
    >>> context = DataCodecContext()
    >>> c.write(data, unhexlify('ff00'), context)
    >>> c.write(data, unhexlify('1234'), context)
    >>> context.length
    4
    >>> hexlify(data)
    b'ff001234'
    >>> context.clear()
    >>> hexlify(c.read(data, context))
    b'ff00'
    >>> hexlify(c.read(data, context))
    b'1234'
    >>> context.length
    4
    >>> hexlify(data)
    b''
    """

    def __init__(self, data_len: int=None) -> None:
        self.data_len = data_len

    def read(self, data: bytearray, context: DataCodecContext) -> bytes:
        if self.data_len is None:
            value = bytes(data)
            del data[:]
            context.length += len(value)
            return value
        else:
            d = pop_first(data, self.data_len)
            context.length += len(d)
            return bytes(d)

    def write(self, data: bytearray, value: bytes, context: DataCodecContext) -> None:
        length = len(value)
        if self.data_len is not None and length != self.data_len:
            raise BytesOperationError(
                'Invalid value data length. (actual:{}, expected:{})'.format(length, self.data_len))
        data += value
        context.length += length


class VarIntData(DataCodec[int]):
    """Convert variable length N bytes data.

    >>> c = VarIntData()
    >>> data = bytearray()
    >>> context = DataCodecContext()
    >>> c.write(data, 0, context)  # 0000_0000 -> 0 (0000_0000)
    >>> c.write(data, 127, context)  # 0111_1111 -> 7f (0111_1111)
    >>> c.write(data, 128, context)  # 1000_0000 -> 8001 (1000_000 0000_0001)
    >>> c.write(data, 16383, context)  # 0011_1111 1111_1111 -> 01ff7f (0000_0001 1111_1111 0111_ffff)
    >>> c.write(data, 16384, context)  # 0100_0000 0000_0000 -> 808001 (1000_0000 8000_0000 0000_0001)
    >>> context.length
    9
    >>> hexlify(data)
    b'007f8001ff7f808001'
    >>> context.clear()
    >>> c.read(data, context)
    0
    >>> c.read(data, context)
    127
    >>> c.read(data, context)
    128
    >>> c.read(data, context)
    16383
    >>> c.read(data, context)
    16384
    >>> context.length
    9
    >>> hexlify(data)
    b''

    >>> c = VarIntData(unsigned=False)
    >>> data = bytearray()
    >>> context = DataCodecContext()
    >>> c.write(data, 0, context)  # 0000_0001 -> 00 (0000_0000)
    >>> c.write(data, 1, context)  # 0000_0001 -> 02 (0000_0010)
    >>> c.write(data, -1, context)  # 1111_1111 1111_1111 -> 01 (0000_0001)
    >>> c.write(data, 32767, context)  # 0111_1111 1111_1111 -> feff03 (1111_1110 1111_1111 0000_0011)
    >>> c.write(data, -32768, context)  # 1000_0000 0000_0001 -> ffff03 (1111_1111 1111_1111 0000_0011)
    >>> context.length
    9
    >>> hexlify(data)
    b'000201feff03ffff03'
    >>> context.clear()
    >>> c.read(data, context)
    0
    >>> c.read(data, context)
    1
    >>> c.read(data, context)
    -1
    >>> c.read(data, context)
    32767
    >>> c.read(data, context)
    -32768
    >>> context.length
    9
    >>> hexlify(data)
    b''
    """

    def __init__(self, unsigned: bool=True) -> None:
        self._unsigned = unsigned

    @staticmethod
    def _exchange_for_reading(value: int) -> int:
        """
        Mark [] shows sign bit. Negative value inverts bits.
        0000 001[0] -> [0]000 0001 (1)
        0000 000[1] -> [1]111 1111 (-1)
        """
        return ~(value >> 1) if value & 1 else (value >> 1)

    @staticmethod
    def _exchange_for_writing(value: int) -> int:
        """
        Mark [] shows sign bit. Negative value inverts bits.
        [0]000 0001 -> 0000 001[0] (1)
        [1]111 1111 -> 0000 000[1] (-1)
        """
        return ~(value << 1) if value < 0 else (value << 1)

    def read(self, data: bytearray, context: DataCodecContext) -> int:
        value = 0
        shift = 0
        while True:
            if len(data) == 0:
                raise BytesOperationError('Invalid data format. (context = {})'.format(context))
            d = data.pop(0)
            context.length += 1
            value += (d & 0x7f) << shift
            if d & 0x80 == 0:
                break
            shift += 7
        return value if self._unsigned else self._exchange_for_reading(value)

    def write(self, data: bytearray, value: int, context: DataCodecContext) -> None:
        if not self._unsigned:
            value = self._exchange_for_writing(value)
        while True:
            d = value & 0x7f
            value >>= 7
            if value != 0:
                data.append(d | 0x80)
                context.length += 1
            else:
                data.append(d)
                context.length += 1
                break


class OptionalData(DataCodec[T]):
    """Pass if predicate is true.

    >>> c = OptionalData(ByteData(), lambda _context: _context.values[0])
    >>> data = bytearray()
    >>> context = DataCodecContext()
    >>> context.values = [False]
    >>> c.write(data, 255, context)
    >>> context.length
    1
    >>> hexlify(data)
    b'ff'
    >>> context.clear()
    >>> c.read(data, context)
    255
    >>> context.length
    1
    >>> hexlify(data)
    b''
    >>> context.clear()
    >>> context.values = [True]
    >>> c.write(data, 255, context)
    >>> context.length
    0
    >>> hexlify(data)
    b''
    >>> context.clear()
    >>> c.read(data, context)
    >>> context.length
    0
    >>> hexlify(data)
    b''
    """

    def __init__(self, data_codec: DataCodec[T], predicate: Callable[[DataCodecContext], bool]):
        self._data_codec = data_codec
        self._predicate = predicate

    def read(self, data: bytearray, context: DataCodecContext) -> Optional[T]:
        return self._data_codec.read(data, context) if not self._predicate(context) else None

    def write(self, data: bytearray, value: Optional[T], context: DataCodecContext) -> None:
        if not self._predicate(context):
            if value is None:
                raise BytesOperationError('Decoding needs the Value.')
            # noinspection PyTypeChecker
            self._data_codec.write(data, value, context)


class ValueFilter(DataCodec[T]):
    """Convert value by filter functions.

    >>> read = lambda _data: len(_data)  # type: Callable[[bytes], int]
    >>> write = lambda _value: unhexlify(b'00') * _value  # type: Callable[[int], bytes]
    >>> c = ValueFilter(RawData(), read=read, write=write)
    >>> data = bytearray()
    >>> context = DataCodecContext()
    >>> c.write(data, 5, context)
    >>> hexlify(data)
    b'0000000000'
    >>> context.clear()
    >>> c.read(data, context)
    5
    >>> hexlify(data)
    b''
    """

    def __init__(self, data_codec: DataCodec[BT], read: Callable[[BT], T]=None, write: Callable[[T], BT]=None) -> None:
        self._data_codec = data_codec
        self._read_filter = (lambda data: data) if read is None else read
        self._write_filter = (lambda value: value) if write is None else write

    def read(self, data: bytearray, context: DataCodecContext) -> T:
        return self._read_filter(self._data_codec.read(data, context))

    def write(self, data: bytearray, value: T, context: DataCodecContext) -> None:
        self._data_codec.write(data, self._write_filter(value), context)


class EnumData(DataCodec[ET]):
    """Convert enum value.

    >>> import enum
    >>> class ID(enum.Enum):
    ...     NG = 0
    ...     OK = 1
    >>> c = EnumData(ByteData(), ID)
    >>> data = bytearray()
    >>> context = DataCodecContext()
    >>> c.write(data, ID.OK, context)
    >>> hexlify(data)
    b'01'
    >>> context.clear()
    >>> c.read(data, context)
    <ID.OK: 1>
    >>> hexlify(data)
    b''
    """

    def __init__(self, data_codec: DataCodec[int], enum_cls: Callable[[int], ET]) -> None:
        self._filter = ValueFilter(data_codec, read=lambda _data: enum_cls(_data), write=lambda _value: _value.value)

    def read(self, data: bytearray, context: DataCodecContext) -> ET:
        return self._filter.read(data, context)

    def write(self, data: bytearray, value: ET, context: DataCodecContext) -> None:
        self._filter.write(data, value, context)


if __name__ == '__main__':
    import doctest
    doctest_result = doctest.testmod()
