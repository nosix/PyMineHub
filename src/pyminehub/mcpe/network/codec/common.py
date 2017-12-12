"""
Common codecs for MCPE packets
"""
from pyminehub.network.codec import *


class _VarIntData(DataCodec[int]):
    """Convert variable length N bytes data.

    >>> c = _VarIntData()
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

    >>> c = _VarIntData(unsigned=False)
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


VAR_INT_DATA = _VarIntData()
VAR_SIGNED_INT_DATA = _VarIntData(unsigned=False)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
