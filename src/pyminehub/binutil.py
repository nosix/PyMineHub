import struct
from binascii import hexlify, unhexlify
from collections import namedtuple
from typing import Any, Optional


def to_bytes(hex_str: str) -> bytes:
    """ Convert hex string to bytes.

    >>> hexlify(to_bytes('00:ff:ff:00:fe:fe:fe:fe:fd:fd:fd:fd:12:34:56:78'))
    b'00ffff00fefefefefdfdfdfd12345678'
    """
    return bytes.fromhex(hex_str.replace(':', ''))


def pop_first(data: bytearray, size: int) -> Optional[bytes]:
    if len(data) < size:
        return None
    data_slice = slice(size)
    value = data[data_slice]
    del data[data_slice]
    return value


class _Converter(namedtuple('Converter', ['byte_order', 'slice_pack', 'fill_zero'])):
    __slots__ = ()

    def pack(self, type_char: str, value: Any, size: int=None) -> bytes:
        buffer = struct.pack(self.byte_order + type_char, value)
        return buffer if size is None else buffer[self.slice_pack(len(buffer), size)]

    def unpack(self, type_char: str, buffer: bytes, fill_size: int=None) -> Any:
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


class ReadContext:

    def __init__(self):
        self.values = []
        self.length = 0

    def clear(self):
        self.__init__()


class ByteData:
    """Convert unsigned 1 byte data.

    >>> c = ByteData()
    >>> data = bytearray()
    >>> c.write(data, 255)
    >>> c.write(data, 127)
    >>> hexlify(data)
    b'ff7f'
    >>> context = ReadContext()
    >>> c.read(data, context)
    255
    >>> c.read(data, context)
    127
    >>> context.length
    2
    >>> hexlify(data)
    b''
    """

    # noinspection PyMethodMayBeStatic
    def read(self, data: bytearray, context: ReadContext) -> Optional[int]:
        if len(data) > 0:
            context.length += 1
            return data.pop(0)
        else:
            return None

    # noinspection PyMethodMayBeStatic
    def write(self, data: bytearray, value: Optional[int]) -> None:
        if value is not None:
            data.append(value)


class ShortData:
    """Convert unsigned 2 bytes data.

    >>> c = ShortData()
    >>> data = bytearray()
    >>> c.write(data, 255)
    >>> c.write(data, 127)
    >>> hexlify(data)
    b'00ff007f'
    >>> context = ReadContext()
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
    >>> c.write(data, 255)
    >>> c.write(data, 127)
    >>> hexlify(data)
    b'ff007f00'
    >>> context = ReadContext()
    >>> c.read(data, context)
    255
    >>> c.read(data, context)
    127
    >>> context.length
    4
    >>> hexlify(data)
    b''
    """

    def __init__(self, endian=Endian.BIG):
        self.endian = endian

    # noinspection PyMethodMayBeStatic
    def read(self, data: bytearray, context: ReadContext) -> Optional[int]:
        d = pop_first(data, 2)
        if d is not None:
            context.length += len(d)
            return self.endian.unpack('H', d)
        else:
            return None

    # noinspection PyMethodMayBeStatic
    def write(self, data: bytearray, value: Optional[int]) -> None:
        if value is not None:
            data += self.endian.pack('H', value)


class TriadData:
    """Convert unsigned 3 bytes data.

    >>> c = TriadData()
    >>> data = bytearray()
    >>> c.write(data, 255)
    >>> c.write(data, 127)
    >>> hexlify(data)
    b'ff00007f0000'
    >>> context = ReadContext()
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
    >>> c.write(data, 255)
    >>> c.write(data, 127)
    >>> hexlify(data)
    b'0000ff00007f'
    >>> context = ReadContext()
    >>> c.read(data, context)
    255
    >>> c.read(data, context)
    127
    >>> context.length
    6
    >>> hexlify(data)
    b''
    """

    def __init__(self, endian=Endian.LITTLE):
        self.endian = endian

    # noinspection PyMethodMayBeStatic
    def read(self, data: bytearray, context: ReadContext) -> Optional[int]:
        d = pop_first(data, 3)
        if d is not None:
            context.length += len(d)
            return self.endian.unpack('I', d, 1)
        else:
            return None

    # noinspection PyMethodMayBeStatic
    def write(self, data: bytearray, value: Optional[int]) -> None:
        if value is not None:
            data += self.endian.pack('I', value, 3)


class IntData:
    """Convert unsigned and signed 4 bytes data.

    >>> c = IntData()
    >>> data = bytearray()
    >>> c.write(data, 255)
    >>> c.write(data, 127)
    >>> hexlify(data)
    b'000000ff0000007f'
    >>> context = ReadContext()
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
    >>> c.write(data, 255)
    >>> c.write(data, 127)
    >>> hexlify(data)
    b'ff0000007f000000'
    >>> context = ReadContext()
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
    >>> c.write(data, 255)
    >>> c.write(data, -1)
    >>> hexlify(data)
    b'000000ffffffffff'
    >>> context = ReadContext()
    >>> c.read(data, context)
    255
    >>> c.read(data, context)
    -1
    >>> context.length
    8
    >>> hexlify(data)
    b''
    """

    def __init__(self, endian=Endian.BIG, unsigned=True):
        self.endian = endian
        self.unsigned = unsigned

    # noinspection PyMethodMayBeStatic
    def read(self, data: bytearray, context: ReadContext) -> Optional[int]:
        d = pop_first(data, 4)
        if d is not None:
            context.length += len(d)
            return self.endian.unpack('I' if self.unsigned else 'i', d)
        else:
            return None

    # noinspection PyMethodMayBeStatic
    def write(self, data: bytearray, value: Optional[int]) -> None:
        if value is not None:
            data += self.endian.pack('I' if self.unsigned else 'i', value)


class LongData:
    """Convert unsigned 8 bytes data.

    >>> c = LongData()
    >>> data = bytearray()
    >>> c.write(data, 255)
    >>> c.write(data, 127)
    >>> hexlify(data)
    b'00000000000000ff000000000000007f'
    >>> context = ReadContext()
    >>> c.read(data, context)
    255
    >>> c.read(data, context)
    127
    >>> context.length
    16
    >>> hexlify(data)
    b''

    >>> c = LongData(Endian.LITTLE)
    >>> data = bytearray()
    >>> c.write(data, 255)
    >>> c.write(data, 127)
    >>> hexlify(data)
    b'ff000000000000007f00000000000000'
    >>> context = ReadContext()
    >>> c.read(data, context)
    255
    >>> c.read(data, context)
    127
    >>> context.length
    16
    >>> hexlify(data)
    b''
    """

    def __init__(self, endian=Endian.BIG):
        self.endian = endian

    # noinspection PyMethodMayBeStatic
    def read(self, data: bytearray, context: ReadContext) -> Optional[int]:
        d = pop_first(data, 8)
        if d is not None:
            context.length += len(d)
            return self.endian.unpack('Q', d)
        else:
            return None

    # noinspection PyMethodMayBeStatic
    def write(self, data: bytearray, value: Optional[int]) -> None:
        if value is not None:
            data += self.endian.pack('Q', value)


class MagicData:
    """Check MAGIC data that is '00:ff:ff:00:fe:fe:fe:fe:fd:fd:fd:fd:12:34:56:78'.

    >>> c = MagicData()
    >>> data = bytearray()
    >>> c.write(data, True)
    >>> hexlify(data)
    b'00ffff00fefefefefdfdfdfd12345678'
    >>> context = ReadContext()
    >>> c.read(data, context)
    True
    >>> context.length
    16
    >>> hexlify(data)
    b''
    >>> c.read(bytearray(b'ffffff00fefefefefdfdfdfd12345678'), context)
    False
    """

    BYTES = unhexlify(b'00ffff00fefefefefdfdfdfd12345678')

    # noinspection PyMethodMayBeStatic
    def read(self, data: bytearray, context: ReadContext) -> bool:
        d = pop_first(data, 16)
        if d is not None:
            context.length += len(d)
        return d == MagicData.BYTES

    # noinspection PyMethodMayBeStatic
    def write(self, data: bytearray, is_valid: bool) -> None:
        assert is_valid
        data += MagicData.BYTES


class BytesData:
    """Convert N bytes data that has 2 bytes length data.

    >>> c = BytesData()
    >>> data = bytearray()
    >>> c.write(data, unhexlify('ff00'))
    >>> c.write(data, unhexlify('123456'))
    >>> hexlify(data)
    b'0002ff000003123456'
    >>> context = ReadContext()
    >>> hexlify(c.read(data, context))
    b'ff00'
    >>> hexlify(c.read(data, context))
    b'123456'
    >>> context.length
    9
    >>> hexlify(data)
    b''

    >>> c = BytesData(Endian.LITTLE)
    >>> data = bytearray()
    >>> c.write(data, unhexlify('ff00'))
    >>> c.write(data, unhexlify('123456'))
    >>> hexlify(data)
    b'0200ff000300123456'
    >>> context = ReadContext()
    >>> hexlify(c.read(data, context))
    b'ff00'
    >>> hexlify(c.read(data, context))
    b'123456'
    >>> context.length
    9
    >>> hexlify(data)
    b''
    """

    def __init__(self, endian=Endian.BIG):
        self.endian = endian
        self.len_codec = ShortData(endian)

    # noinspection PyMethodMayBeStatic
    def read(self, data: bytearray, context: ReadContext) -> Optional[bytes]:
        bytes_len = self.len_codec.read(data, context)
        if bytes_len is None:
            return None
        d = pop_first(data, bytes_len)
        if d is not None:
            context.length += len(d)
        return d

    # noinspection PyMethodMayBeStatic
    def write(self, data: bytearray, value: bytes) -> None:
        self.len_codec.write(data, len(value))
        data += value


class StringData:
    """Convert N bytes string that has 2 bytes length data.

    >>> c = StringData()
    >>> data = bytearray()
    >>> c.write(data, 'Hello')
    >>> c.write(data, 'マイクラ')
    >>> hexlify(data)
    b'000548656c6c6f000ce3839ee382a4e382afe383a9'
    >>> context = ReadContext()
    >>> c.read(data, context)
    'Hello'
    >>> c.read(data, context)
    'マイクラ'
    >>> context.length
    21
    >>> hexlify(data)
    b''
    """

    def __init__(self, endian=Endian.BIG, encoding='utf8'):
        self.endian = endian
        self.encoding = encoding
        self.len_codec = ShortData(endian)

    # noinspection PyMethodMayBeStatic
    def read(self, data: bytearray, context: ReadContext) -> Optional[str]:
        bytes_len = self.len_codec.read(data, context)
        if bytes_len is None:
            return None
        d = pop_first(data, bytes_len)
        if d is None:
            return None
        context.length += len(d)
        return str(d, self.encoding)

    # noinspection PyMethodMayBeStatic
    def write(self, data: bytearray, value: str) -> None:
        bytes_data = bytes(value, self.encoding)
        self.len_codec.write(data, len(bytes_data))
        data += bytes_data


class RawData:
    """Convert N bytes data that does not have length data.

    >>> c = RawData()
    >>> data = bytearray()
    >>> c.write(data, unhexlify('ff00'))
    >>> c.write(data, unhexlify('123456'))
    >>> hexlify(data)
    b'ff00123456'
    >>> context = ReadContext()
    >>> hexlify(c.read(data, context))
    b'ff00123456'
    >>> context.length
    5
    >>> hexlify(data)
    b''

    >>> c = RawData(bytes_len=2)
    >>> data = bytearray()
    >>> c.write(data, unhexlify('ff00'))
    >>> c.write(data, unhexlify('1234'))
    >>> hexlify(data)
    b'ff001234'
    >>> context = ReadContext()
    >>> hexlify(c.read(data, context))
    b'ff00'
    >>> hexlify(c.read(data, context))
    b'1234'
    >>> context.length
    4
    >>> hexlify(data)
    b''
    """

    def __init__(self, bytes_len=None):
        self.bytes_len = bytes_len

    # noinspection PyMethodMayBeStatic
    def read(self, data: bytearray, context: ReadContext) -> Optional[bytes]:
        if self.bytes_len is None:
            value = bytes(data)
            del data[:]
            context.length += len(value)
            return value
        else:
            d = pop_first(data, self.bytes_len)
            if d is None:
                return None
            context.length += len(d)
            return bytes(d)

    # noinspection PyMethodMayBeStatic
    def write(self, data: bytearray, value: bytes) -> None:
        data += value


class ValueFilter:
    """Convert value by filter functions.

    >>> read = lambda value: len(value)  # type: (bytes) -> int
    >>> write = lambda value: unhexlify(b'00') * value  # type: (int) -> bytes
    >>> c = ValueFilter(RawData(), read=read, write=write)
    >>> data = bytearray()
    >>> c.write(data, 5)
    >>> hexlify(data)
    b'0000000000'
    >>> context = ReadContext()
    >>> c.read(data, context)
    5
    >>> hexlify(data)
    b''
    """

    def __init__(self, data_codec, read=None, write=None):
        self.data_codec = data_codec
        self.read_filter = (lambda data: data) if read is None else read
        self.write_filter = (lambda value: value) if write is None else write

    # noinspection PyMethodMayBeStatic
    def read(self, data: bytearray, context: ReadContext) -> Any:
        return self.read_filter(self.data_codec.read(data, context))

    # noinspection PyMethodMayBeStatic
    def write(self, data: bytearray, value: Any) -> None:
        self.data_codec.write(data, self.write_filter(value))


if __name__ == '__main__':
    import doctest
    doctest.testmod()
