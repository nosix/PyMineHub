import unittest
from binascii import unhexlify as unhex

from pyminehub.mcpe.network.packet import GamePacketID as MCPEGamePacketID
from pyminehub.mcpe.network.packet import PacketID as MCPEPacketID
from pyminehub.network.codec import PacketCodecContext, BYTE_DATA
from pyminehub.raknet.encapsulation import CapsuleID as RakNetCapsuleID
from pyminehub.raknet.packet import PacketID as RakNetPacketID


class GamePacket:

    # noinspection PyUnresolvedReferences
    from pyminehub.mcpe.network.codec import game_packet_codec

    def __init__(self, packet_id: MCPEGamePacketID):
        self._packet_id = packet_id
        self._data = None
        self._mcpe_game_packet = None

    def on(self, test_case: unittest.TestCase, data: bytes):
        context = PacketCodecContext()
        self._data = data
        self._mcpe_game_packet = self.game_packet_codec.decode(data, context=context)
        test_case.assertEqual(MCPEGamePacketID(self._mcpe_game_packet.id), self._packet_id)
        test_case.assertEqual(context.length, len(data))

    def verify(self, test_case: unittest.TestCase):
        assert self._data is not None and self._mcpe_game_packet is not None
        data = self.game_packet_codec.encode(self._mcpe_game_packet, BYTE_DATA)
        test_case.assertEqual(data, self._data)


class Batch:

    # noinspection PyUnresolvedReferences
    from pyminehub.mcpe.network.codec import packet_codec

    def __init__(self):
        self._packet_validators = []
        self._data = None
        self._mcpe_packet = None

    def that_has(self, game_packet: GamePacket):
        self._packet_validators.append(game_packet)
        return self

    def and_(self, game_packet: GamePacket):
        return self.that_has(game_packet)

    def on(self, test_case: unittest.TestCase, data: bytes):
        context = PacketCodecContext()
        self._data = data
        self._mcpe_packet = self.packet_codec.decode(data, context=context)
        test_case.assertEqual(MCPEPacketID(self._mcpe_packet.id), MCPEPacketID.batch)
        test_case.assertEqual(context.length, len(data))
        test_case.assertEqual(len(self._mcpe_packet.payloads), len(self._packet_validators))
        for payload, validator in zip(self._mcpe_packet.payloads, self._packet_validators):
            try:
                validator.on(test_case, payload)
            except Exception as e:
                e.args += (self._mcpe_packet, )
                raise e

    def verify(self, test_case: unittest.TestCase):
        assert self._data is not None and self._mcpe_packet is not None
        data = self.packet_codec.encode(self._mcpe_packet, BYTE_DATA)
        test_case.assertEqual(data, self._data)
        for validator in self._packet_validators:
            validator.verify(test_case)


class Capsule:

    # noinspection PyUnresolvedReferences
    from pyminehub.raknet.codec import capsule_codec

    def __init__(self, capsule_id: RakNetCapsuleID):
        self._capsule_id = capsule_id
        self._batch = None
        self._data = None
        self._capsule = None

    def that_has(self, batch: Batch):
        self._batch = batch
        return self

    def on(self, test_case: unittest.TestCase, data: bytes):
        context = PacketCodecContext()
        self._data = data
        self._capsule = self.capsule_codec.decode(data, context=context)
        test_case.assertEqual(RakNetCapsuleID(self._capsule.id), self._capsule_id)
        if self._batch is not None:
            try:
                self._batch.on(test_case, self._capsule.payload)
            except Exception as e:
                e.args += (self._capsule, )
                raise e
        return context.length

    def verify(self, test_case: unittest.TestCase):
        assert self._data is not None and self._capsule is not None
        data = self.capsule_codec.encode(self._capsule, BYTE_DATA)
        test_case.assertEqual(data, self._data)
        if self._batch is not None:
            self._batch.verify(test_case)


class TestPacket:

    # noinspection PyUnresolvedReferences
    from pyminehub.raknet.codec import packet_codec

    def __init__(self, data: str):
        self._data = unhex(data)
        self._packet_id = None
        self._capsule_validators = []
        self._raknet_packet = None

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
        self._raknet_packet = self.packet_codec.decode(self._data, context=context)
        test_case.assertEqual(RakNetPacketID(self._raknet_packet.id), self._packet_id, self._raknet_packet)
        test_case.assertEqual(context.length, len(self._data))

    def on(self, test_case: unittest.TestCase):
        self._test_raknet_packet(test_case)
        assert self._raknet_packet is not None
        data = self._raknet_packet.payload
        payload_length = 0
        try:
            for validator in self._capsule_validators:
                payload_length += validator.on(test_case, data)
        except Exception as e:
            e.args += (self._raknet_packet, )
            raise e
        test_case.assertEqual(payload_length, len(data))
        return self

    def and_verify_encoded_data_on(self, test_case: unittest.TestCase):
        assert self._raknet_packet is not None
        data = self.packet_codec.encode(self._raknet_packet, BYTE_DATA)
        test_case.assertEqual(data, self._data)
        for validator in self._capsule_validators:
            validator.verify(test_case)


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
        ).on(self).and_verify_encoded_data_on(self)


if __name__ == '__main__':
    unittest.main()
