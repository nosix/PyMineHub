import unittest
from binascii import unhexlify as unhex

from pyminehub.mcpe.network.packet import GamePacketID as MCPEGamePacketID
from pyminehub.mcpe.network.packet import PacketID as MCPEPacketID
from pyminehub.network.codec import PacketCodecContext
from pyminehub.raknet.encapsulation import CapsuleID as RakNetCapsuleID
from pyminehub.raknet.packet import PacketID as RakNetPacketID


class GamePacket:

    # noinspection PyUnresolvedReferences
    from pyminehub.mcpe.network.codec import game_packet_codec

    def __init__(self, packet_id: MCPEGamePacketID):
        self._packet_id = packet_id

    def on(self, test_case: unittest.TestCase, data: bytes):
        context = PacketCodecContext()
        mcpe_game_packet = self.game_packet_codec.decode(data, context=context)
        test_case.assertEqual(MCPEGamePacketID(mcpe_game_packet.id), self._packet_id)
        test_case.assertEqual(context.length, len(data))


class Batch:

    # noinspection PyUnresolvedReferences
    from pyminehub.mcpe.network.codec import packet_codec

    def __init__(self):
        self._packet_validators = []

    def that_has(self, game_packet: GamePacket):
        self._packet_validators.append(game_packet)
        return self

    def and_(self, game_packet: GamePacket):
        return self.that_has(game_packet)

    def on(self, test_case: unittest.TestCase, data: bytes):
        context = PacketCodecContext()
        mcpe_packet = self.packet_codec.decode(data, context=context)
        test_case.assertEqual(MCPEPacketID(mcpe_packet.id), MCPEPacketID.batch)
        test_case.assertEqual(context.length, len(data))
        test_case.assertEqual(len(mcpe_packet.payloads), len(self._packet_validators))
        for payload, validator in zip(mcpe_packet.payloads, self._packet_validators):
            validator.on(test_case, payload)


class Capsule:

    # noinspection PyUnresolvedReferences
    from pyminehub.raknet.codec import capsule_codec

    def __init__(self, capsule_id: RakNetCapsuleID):
        self._capsule_id = capsule_id
        self._batch = None

    def that_has(self, batch: Batch):
        self._batch = batch
        return self

    def on(self, test_case: unittest.TestCase, data: bytes):
        context = PacketCodecContext()
        capsule = self.capsule_codec.decode(data, context=context)
        test_case.assertEqual(RakNetCapsuleID(capsule.id), self._capsule_id)
        if self._batch is not None:
            self._batch.on(test_case, capsule.payload)
        return context.length


class TestPacket:

    # noinspection PyUnresolvedReferences
    from pyminehub.raknet.codec import packet_codec

    def __init__(self, data: str):
        self._data = unhex(data)
        self._packet_id = None
        self._capsule_validators = []

    def is_(self, packet_id: RakNetPacketID):
        self._packet_id = packet_id
        return self

    def that_has(self, capsule: Capsule):
        self._capsule_validators.append(capsule)
        return self

    def and_(self, capsule: Capsule):
        return self.that_has(capsule)

    def _test_raknet_packet(self, test_case: unittest.TestCase):
        assert self._packet_id is not None
        context = PacketCodecContext()
        packet = self.packet_codec.decode(self._data, context=context)
        test_case.assertEqual(RakNetPacketID(packet.id), self._packet_id)
        test_case.assertEqual(context.length, len(self._data))
        return packet.payload

    def on(self, test_case: unittest.TestCase):
        data = self._test_raknet_packet(test_case)
        payload_length = 0
        for validator in self._capsule_validators:
            payload_length += validator.on(test_case, data)
        test_case.assertEqual(payload_length, len(data))


class TestDecode(unittest.TestCase):

    def test_(self):
        TestPacket(
            '840400006000a000000000000000fe7801010800f7ff0702000000000000004e'
            '000a6000a801000001000000fe7801010900f6ff080600000000000000008100'
            '0f'
        ).is_(
            RakNetPacketID.custom_packet_4
        ).that_has(
            Capsule(RakNetCapsuleID.reliable_ordered).that_has(
                Batch().that_has(
                    GamePacket(MCPEGamePacketID.login)  # TODO change packet ID
                )
            )
        ).and_(
            Capsule(RakNetCapsuleID.reliable_ordered).that_has(
                Batch().that_has(
                    GamePacket(MCPEGamePacketID.login)  # TODO change packet ID
                )
            )
        ).on(self)


if __name__ == '__main__':
    unittest.main()
