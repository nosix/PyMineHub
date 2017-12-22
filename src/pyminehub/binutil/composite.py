from typing import Sequence, Tuple, Callable

from pyminehub.binutil.converter import DataCodecContext, DataCodec
from pyminehub.typevar import T


class CompositeCodecContext(DataCodecContext):

    def __init__(self) -> None:
        super().__init__()
        self._values = []
        self._stack = []

    def append_value(self, value) -> None:
        self._values.append(value)

    def get_values(self) -> tuple:
        return tuple(self._values)

    def push_stack(self) -> None:
        self._stack.append({})

    def pop_stack(self) -> None:
        self._stack.pop()

    def __setitem__(self, key, value) -> None:
        self._stack[-1][key] = value

    def __getitem__(self, key) -> T:
        for d in reversed(self._stack):
            if key in d:
                return d[key]
        raise KeyError(key)


class CompositeCodec:

    def __init__(self, data_codecs: Sequence[DataCodec]) -> None:
        self._data_codecs = data_codecs

    def encode(self, *values, context: CompositeCodecContext=None) -> bytes:
        """ Encode values to bytes.

        >>> context = CompositeCodecContext()
        >>> hexlify(_codec.encode(0x1c, 8721, 12985, 'MCPE;', context=context))
        b'1c000000000000221100000000000032b900054d4350453b'
        >>> context.length
        24
        >>> context.get_values()
        (28, 8721, 12985, 'MCPE;')

        :param values: encoding target
        :param context: if context is None then create a CompositeCodecContext
        :return: bytes data obtained by encoding
        """
        context = context or CompositeCodecContext()
        context.push_stack()
        data = bytearray()
        for (value, encoder) in zip(values, self._data_codecs):
            encoder.write(data, value, context)
            context.append_value(value)
        context.pop_stack()
        return bytes(data)

    def decode(self, data: bytes, context: CompositeCodecContext=None) -> tuple:
        """ Decode bytes to values.

        >>> data = unhexlify(b'1c000000000000221100000000000032b900054d4350453b')
        >>> context = CompositeCodecContext()
        >>> _codec.decode(data, context=context)
        (28, 8721, 12985, 'MCPE;')
        >>> context.length
        24
        >>> context.get_values()
        (28, 8721, 12985, 'MCPE;')

        :param data: decoding target
        :param context: if context is None then create a CompositeCodecContext
        :return: values obtained by decoding
        """
        context = context or CompositeCodecContext()
        context.push_stack()
        buffer = bytearray(data)
        for decoder in self._data_codecs:
            context.append_value(decoder.read(buffer, context))
        context.pop_stack()
        return context.get_values()


class NamedData(DataCodec[T]):

    def __init__(self, name: str, data_codec: DataCodec[T]):
        self._name = name
        self._data_codec = data_codec

    def read(self, data: bytearray, context: CompositeCodecContext) -> T:
        value = self._data_codec.read(data, context)
        context[self._name] = value
        return value

    def write(self, data: bytearray, value: T, context: CompositeCodecContext) -> None:
        self._data_codec.write(data, value, context)
        context[self._name] = value


class VarListData(DataCodec[Tuple[T, ...]]):

    def __init__(self, count_codec: DataCodec[int], item_codec: DataCodec[T]) -> None:
        self._count_codec = count_codec
        self._item_codec = item_codec

    def read(self, data: bytearray, context: DataCodecContext) -> Tuple[T, ...]:
        count = self._count_codec.read(data, context)
        return tuple(self._item_codec.read(data, context) for _ in range(count))

    def write(self, data: bytearray, value: Tuple[T, ...], context: DataCodecContext) -> None:
        self._count_codec.write(data, len(value), context)
        for entry in value:
            self._item_codec.write(data, entry, context)


class CompositeData(DataCodec[T]):

    def __init__(self, factory: Callable[..., T], data_codecs: Tuple[DataCodec, ...]) -> None:
        self._factory = factory
        self._data_codecs = data_codecs

    def read(self, data: bytearray, context: CompositeCodecContext) -> T:
        context.push_stack()

        def generate():
            for data_codec in self._data_codecs:
                value = data_codec.read(data, context)
                yield value

        args = tuple(generate())
        context.pop_stack()
        return self._factory(*args)

    def write(self, data: bytearray, value: T, context: CompositeCodecContext) -> None:
        context.push_stack()
        for v, data_codec in zip(value, self._data_codecs):
            data_codec.write(data, v, context)
        context.pop_stack()


if __name__ == '__main__':
    from binascii import hexlify, unhexlify
    from pyminehub.binutil.converter import ByteData, LongData, StringData

    _data_codecs = (
        ByteData(),
        LongData(),
        LongData(),
        StringData()
    )

    _codec = CompositeCodec(_data_codecs)

    import doctest
    doctest_result = doctest.testmod()
