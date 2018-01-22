from pyminehub.binutil.converter import *


__all__ = [
    'BYTE_DATA',
    'B_SHORT_DATA',
    'L_SHORT_DATA',
    'L_TRIAD_DATA',
    'B_INT_DATA',
    'L_INT_DATA',
    'L_SIGNED_INT_DATA',
    'B_LONG_DATA',
    'L_LONG_DATA',
    'L_FLOAT_DATA',
    'BYTES_DATA',
    'STRING_DATA',
    'RAW_DATA',
    'VAR_INT_DATA',
    'VAR_SIGNED_INT_DATA',
    'VAR_BYTES_DATA',
    'VAR_STRING_DATA',
    'BOOL_DATA',
    'FALSE_DATA'
]


# convert 1 byte length unsigned integer data
BYTE_DATA = ByteData()

# convert 2 bytes length unsigned integer data
B_SHORT_DATA = ShortData()
L_SHORT_DATA = ShortData(endian=Endian.LITTLE)

# convert 3 bytes length unsigned integer data
L_TRIAD_DATA = TriadData()

# convert 4 bytes length unsigned integer data
B_INT_DATA = IntData()
L_INT_DATA = IntData(endian=Endian.LITTLE)

# convert 4 bytes length signed integer data
L_SIGNED_INT_DATA = IntData(endian=Endian.LITTLE, unsigned=False)

# convert 8 bytes length unsigned integer data
B_LONG_DATA = LongData()
L_LONG_DATA = LongData(endian=Endian.LITTLE)

# convert 4 bytes length signed float data
L_FLOAT_DATA = FloatData(endian=Endian.LITTLE)

# convert N bytes length bytes data (length is B_SHORT_DATA)
BYTES_DATA = BytesData()

# convert N bytes length string data (length is B_SHORT_DATA)
STRING_DATA = StringData()

# convert N bytes length bytes data (without length in data)
RAW_DATA = RawData()

# convert N bytes length unsigned integer data (without length in data)
VAR_INT_DATA = VarIntData()

# convert N bytes length signed integer data (without length in data)
VAR_SIGNED_INT_DATA = VarIntData(unsigned=False)

# convert N bytes length bytes data (length is VAR_INT_DATA)
VAR_BYTES_DATA = BytesData(len_codec=VAR_INT_DATA)

# convert N bytes length string data (length is VAR_INT_DATA)
VAR_STRING_DATA = StringData(len_codec=VAR_INT_DATA)

# convert 1 byte length boolean data
BOOL_DATA = ValueFilter(BYTE_DATA, read=lambda _data: _data != 0, write=lambda _value: 1 if _value else 0)

# convert 1 byte length false data
FALSE_DATA = ValueFilter(BYTE_DATA, read=lambda _data: _data != 0, write=false_to_zero)
