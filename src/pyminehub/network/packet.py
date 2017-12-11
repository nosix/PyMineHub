from typing import NamedTuple


class PacketFactory:

    def __init__(self, packet_specs):
        self._factory = dict(
            (packet_id, NamedTuple(packet_id.name, field_names)) for packet_id, field_names in packet_specs.items())

    def create(self, packet_id, *args, **kwargs) -> NamedTuple:
        """Create packet.

        >>> factory.create(ID.unconnected_pong, 8721, 5065, True, 'MCPE;')
        unconnected_pong(id=28, time_since_start=8721, server_guid=5065, valid_message_data_id=True, server_id='MCPE;')
        """
        # noinspection PyCallingNonCallable
        return self._factory[packet_id](packet_id.value, *args, **kwargs)


if __name__ == '__main__':
    from enum import Enum

    class ID(Enum):
        unconnected_pong = 0x1c

    _packet_specs = {
        ID.unconnected_pong: [
            ('id', int),
            ('time_since_start', int),
            ('server_guid', bytes),
            ('valid_message_data_id', bool),
            ('server_id', str)
        ]
    }

    factory = PacketFactory(_packet_specs)

    import doctest
    doctest.testmod()
