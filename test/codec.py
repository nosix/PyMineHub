"""
Test cases for codec.

When debugging, execute `from codec import *` in REPL.
"""
import logging
import sys
import traceback
from binascii import unhexlify as unhex
from unittest import TestCase

from pyminehub import config
from pyminehub.mcpe.network.codec import game_packet_codec as mcpe_game_packet_codec
from pyminehub.mcpe.network.codec import packet_codec as mcpe_packet_codec
from pyminehub.mcpe.network.packet import GamePacketID as MCPEGamePacketID
from pyminehub.mcpe.network.packet import PacketID as MCPEPacketID
from pyminehub.network.codec import PacketCodecContext
from pyminehub.raknet.codec import capsule_codec as raknet_capsule_codec
from pyminehub.raknet.codec import packet_codec as raknet_packet_codec
from pyminehub.raknet.encapsulation import CapsuleID as RakNetCapsuleID
from pyminehub.raknet.packet import PacketID as RakNetPacketID

_logger = logging.getLogger(__name__)


def interrupt_for_pycharm(exc: Exception, called, packet_info=None):
    if type(exc).__name__ == 'EqualsAssertionError':
        attrs = exc.__dict__
        if 'called' not in attrs:
            attrs['called'] = called
        if 'stack' not in attrs:
            attrs['stack'] = []
        if packet_info is not None:
            attrs['stack'].append(packet_info)
        else:
            messages = ['AssertionError occurred while testing', attrs['called'][:-1]]  # remove \n
            messages.extend(attrs['stack'])
            messages.append(attrs['msg'])
            attrs['msg'] = '\n'.join(messages)
        raise exc


class _WrappedException(Exception):

    def __init__(self, exc: Exception, tb: traceback, message: str):
        super().__init__(message)
        self.exc = exc
        self.tb = tb


class GamePacket:

    def __init__(self, packet_id: MCPEGamePacketID, show_packet=False):
        """ Game packet validator.
        :param packet_id: expected packet ID
        :param show_packet: show packet information when validator verify it
        """
        self.called = traceback.format_stack()[-2]
        self._packet_id = packet_id
        self._data = None
        self._mcpe_game_packet = None
        self._show_packet = show_packet

    def is_correct_on(self, test_case: TestCase, data: bytes):
        context = PacketCodecContext()
        self._mcpe_game_packet = mcpe_game_packet_codec.decode(data, context)
        test_case.assertEqual(self._packet_id, MCPEGamePacketID(self._mcpe_game_packet.id))
        test_case.assertEqual(len(data), context.length)
        self._data = data[:context.length]

    def verify_on(self, test_case: TestCase):
        assert self._data is not None and self._mcpe_game_packet is not None
        data = mcpe_game_packet_codec.encode(self._mcpe_game_packet)
        test_case.assertEqual(self._data, data, '{}\n{}'.format(self.called, self._mcpe_game_packet))
        if self._show_packet:
            _logger.info('%s\n  -> %s\n%s', self._mcpe_game_packet, self._data.hex(), self.called)


class Batch:

    def __init__(self, show_packet=False):
        """ Batch packet validator.
        :param show_packet: show packet information when validator verify it
        """
        self.called = traceback.format_stack()[-2]
        self._assertions = []
        self._data = None
        self._mcpe_packet = None
        self._show_packet = show_packet

    def that_has(self, *game_packet: GamePacket):
        self._assertions.extend(game_packet)
        return self

    def is_correct_on(self, test_case: TestCase, data: bytes):
        context = PacketCodecContext()
        self._mcpe_packet = mcpe_packet_codec.decode(data, context)
        test_case.assertEqual(MCPEPacketID.batch, MCPEPacketID(self._mcpe_packet.id))
        test_case.assertEqual(len(data), context.length)
        test_case.assertEqual(len(self._assertions), len(self._mcpe_packet.payloads))
        for payload, assertion in zip(self._mcpe_packet.payloads, self._assertions):
            try:
                assertion.is_correct_on(test_case, payload)
            except Exception as e:
                packet_info = '  MCPE packet {}'.format(self._mcpe_packet)
                interrupt_for_pycharm(e, assertion.called, packet_info)
                message = '{} occurred while testing\n{}{}'.format(repr(e), assertion.called, packet_info)
                raise _WrappedException(e, sys.exc_info()[2], message) from None
        self._data = data[:context.length]

    def verify_on(self, test_case: TestCase):
        assert self._data is not None and self._mcpe_packet is not None
        data = mcpe_packet_codec.encode(self._mcpe_packet)
        test_case.assertEqual(self._data, data, '{}\n{}'.format(self.called, self._mcpe_packet))
        for assertion in self._assertions:
            assertion.verify_on(test_case)
        if self._show_packet:
            _logger.info('%s\n  -> %s\n%s', self._mcpe_packet, self._data.hex(), self.called)


class Capsule:

    def __init__(self, capsule_id: RakNetCapsuleID, show_capsule=False):
        """ Encapsulation of RakNet packet validator.
        :param capsule_id: expected encapsulation ID
        :param show_capsule: show encapsulation information when validator verify it
        """
        self.called = traceback.format_stack()[-2]
        self._capsule_id = capsule_id
        self._assertion = None
        self._data = None
        self._capsule = None
        self._show_capsule = show_capsule

    def that_has(self, batch: Batch):
        self._assertion = batch
        return self

    def is_correct_on(self, test_case: TestCase, data: bytes):
        context = PacketCodecContext()
        self._capsule = raknet_capsule_codec.decode(data, context)
        test_case.assertEqual(self._capsule_id, RakNetCapsuleID(self._capsule.id))
        if self._assertion is not None:
            try:
                self._assertion.is_correct_on(test_case, self._capsule.payload)
            except _WrappedException as e:
                message = '{}\n  RakNet encapsulation {}'.format(e.args[0], self._capsule)
                raise _WrappedException(e.exc, e.tb, message) from None
            except Exception as e:
                packet_info = '  RakNet encapsulation {}'.format(self._capsule)
                interrupt_for_pycharm(e, self._assertion.called, packet_info)
                message = '{} occurred while testing\n{}'.format(repr(e), self._assertion.called, packet_info)
                raise _WrappedException(e, sys.exc_info()[2], message) from None
        self._data = data[:context.length]
        return context.length

    def verify_on(self, test_case: TestCase):
        assert self._data is not None and self._capsule is not None
        data = raknet_capsule_codec.encode(self._capsule)
        test_case.assertEqual(self._data, data, '{}\n{}'.format(self.called, self._capsule))
        if self._assertion is not None:
            self._assertion.verify_on(test_case)
        if self._show_capsule:
            _logger.info('%s\n  -> %s\n%s', self._capsule, self._data.hex(), self.called)


class RakNetPacket:

    def __init__(self, packet_id: RakNetPacketID, show_packet=False):
        """ RakNet packet validator.
        :param packet_id: expected packet ID
        :param show_packet: show packet information when validator verify it
        """
        self.called = traceback.format_stack()[-2]
        self._packet_id = packet_id
        self._assertions = []
        self._data = None
        self._raknet_packet = None
        self._show_packet = show_packet

    def that_has(self, *capsule: Capsule):
        self._assertions.extend(capsule)
        return self

    def _test_raknet_packet(self, test_case: TestCase, data: bytes):
        assert self._packet_id is not None
        context = PacketCodecContext()
        self._raknet_packet = raknet_packet_codec.decode(data, context)
        test_case.assertEqual(self._packet_id, RakNetPacketID(self._raknet_packet.id), self._raknet_packet)
        test_case.assertEqual(len(data), context.length)

    def _test_raknet_encapsulation(self, test_case: TestCase):
        assert self._raknet_packet is not None
        data = self._raknet_packet.payload
        payload_length = 0
        for assertion in self._assertions:
            try:
                payload_length += assertion.is_correct_on(test_case, data[payload_length:])
            except _WrappedException as e:
                message = '{}\n  RakNet packet {}'.format(e.args[0], self._raknet_packet)
                raise _WrappedException(e.exc, e.tb, message) from None
            except Exception as e:
                packet_info = '  RakNet packet {}'.format(self._raknet_packet)
                interrupt_for_pycharm(e, assertion.called, packet_info)
                message = '{} occurred while testing\n{}{}'.format(repr(e), assertion.called, packet_info)
                raise _WrappedException(e, sys.exc_info()[2], message) from None
        test_case.assertEqual(len(data), payload_length, 'Capsule may be missing with "{}"'.format(data.hex()))

    def is_correct_on(self, test_case: TestCase, data: bytes):
        self._data = data
        try:
            self._test_raknet_packet(test_case, data)
            self._test_raknet_encapsulation(test_case)
        except _WrappedException as e:
            message = '{}'.format(e.args[0])
            raise test_case.failureException(message).with_traceback(e.tb) from None
        except Exception as e:
            interrupt_for_pycharm(e, self.called)
            message = '{} occurred while testing\n{}'.format(repr(e), self.called)
            raise test_case.failureException(message).with_traceback(sys.exc_info()[2]) from None

    def verify_on(self, test_case: TestCase):
        assert self._raknet_packet is not None
        data = raknet_packet_codec.encode(self._raknet_packet)
        test_case.assertEqual(self._data, data, '{}\n{}'.format(self.called, self._raknet_packet))
        for assertion in self._assertions:
            assertion.verify_on(test_case)
        if self._show_packet:
            _logger.info('%s\n  -> %s\n%s', self._raknet_packet, self._data.hex(), self.called)


class EncodedData:

    def __init__(self, data: str):
        """ Encoded data validator.

        :param data: data that decode to packet
        """
        self._data = unhex(data)
        self._assertion = None

    def is_(self, packet: RakNetPacket):
        self._assertion = packet
        return self

    def is_correct_on(self, test_case: TestCase, and_verify_encoded_data=False):
        self._assertion.is_correct_on(test_case, self._data)
        if and_verify_encoded_data:
            self._assertion.verify_on(test_case)


class TestDecode(TestCase):

    def setUp(self):
        _logger.setLevel(logging.INFO)
        self._handler = logging.StreamHandler(sys.stdout)
        _logger.addHandler(self._handler)
        config.reset()

    def tearDown(self):
        _logger.removeHandler(self._handler)

    def test_login_logout_01(self):
        assertion = EncodedData(
            '840400006000a000000000000000fe7801010800f7ff0702000000000000004e'
            '000a6000a801000001000000fe7801010900f6ff080600000000000000008100'
            '0f'
        ).is_(
            RakNetPacket(RakNetPacketID.custom_packet_4).that_has(
                Capsule(RakNetCapsuleID.reliable_ordered).that_has(
                    Batch().that_has(
                        GamePacket(MCPEGamePacketID.play_status)
                    )
                ),
                Capsule(RakNetCapsuleID.reliable_ordered).that_has(
                    Batch().that_has(
                        GamePacket(MCPEGamePacketID.resource_packs_info)
                    )
                )
            )
        )
        assertion.is_correct_on(self, and_verify_encoded_data=True)

    def test_login_logout_02(self):
        config.set_config(batch_compress_threshold=0)  # TODO
        assertion = EncodedData(
            '840d00006000800b000002000000fe78da63e360606066600000006a0012'
        ).is_(
            RakNetPacket(RakNetPacketID.custom_packet_4).that_has(
                Capsule(RakNetCapsuleID.reliable_ordered).that_has(
                    Batch().that_has(
                        GamePacket(MCPEGamePacketID.resource_pack_client_response)
                    )
                )
            )
        )
        assertion.is_correct_on(self, and_verify_encoded_data=True)

    def test_login_logout_03(self):
        assertion = EncodedData(
            '8405000060009802000002000000fe7801010700f8ff06070000000000005b00'
            '0e'
        ).is_(
            RakNetPacket(RakNetPacketID.custom_packet_4).that_has(
                Capsule(RakNetCapsuleID.reliable_ordered).that_has(
                    Batch().that_has(
                        GamePacket(MCPEGamePacketID.resource_pack_stack)
                    )
                )
            )
        )
        assertion.is_correct_on(self, and_verify_encoded_data=True)

    def test_login_logout_04(self):
        assertion = EncodedData(
            '8409000060035003000003000000fe7801015e00a1ff5d0b0000020100000080'
            '430080664200008043000000000000b3430100020004800438800401cc880200'
            '000000000000000001010001010000000002000014506f636b65744d696e652d'
            '4d502053657276657200000000000000000000007af30e186000980400000400'
            '0000fe7801010700f8ff060a0000cc880203e301676006f005000005000000fe'
            '78da6dd04d0ac2301005e0884b3722a20b513c810710a4bad0957790691d6d69'
            '9a9424f567658fe209bc82b8af7824b58925d53af0761f2f99b9d6fb84d41a44'
            'cf7956a419050c3d011b35f611a8f20d207342d2599e8e051b4e29dfaf04b02d'
            '1a953a1f4e0696858c7ba10b5eb8122803a980799a3f9fa7d33dcb26795a9647'
            '7c8711325510d39a3a5d4b40a9bc6e0d116cd13a33ed92732517b10a38b36b0e'
            'f59a3d8b620a471423092a1150b2d3f0b1d4eb542d1e7c48e477af49b762fde4'
            '7d1da1d9e5b6283ed9a9388a3ba4bf57fcf7748c22c0f7095f13fd87aa601cd8'
            '06000006000000fe78da8d566d6f143710de7b4980a20610a80a546a2d958a34'
            '0d415408f1812f21ada2a8548ab888ef137b76cf8ad75e79bc77ba3fc55f84f1'
            'be5c96cb6e9afbb0278f3d8f679e997976bf3cfe9824db77a8d4522b1c1766b4'
            '9ce4944d16e8b7e0c2952199deff571b73643410d228d9393365a62db586d1fd'
            '735c6f8fc7939dcfe8493bdb5aa65bcf271760df9c795ca00d24c21c05152875'
            'aa5189c2c00abd48bdcb4549da66bcaf49107a8e2049bef26f349a82cfe851f2'
            '30196d33d44b5dbc1b403b3d13a09447a25b23de6144a329ec7dd6b814604c13'
            '1209deb08c5901dd08f140610aa50919e4983b85bb330c55608d5db41bd75da7'
            '0a5d71700e97d84fcc0b12ae400fc17941014249d7317e503a4db5e48b56f1e6'
            '1a285e29ae367a98c43445197e3d528a5e7de2f0161c426de33b6dcb420f6168'
            'e51c6c78163d45b3c8ab62b09b0e98f738dd6d29d83fe6e359936d53fce004b4'
            '99cb3af201b632bdc037277a31c016c348f401b41590bbd206e1d2a188a6975a'
            '5e1eb4890f3765b5335078c630e6f9b1cb731d443342822b15cdc2b1a7bfa231'
            'febef38d4db7fb911f54759de32eb4384cfb38c7dfcfd0a7cee79be1820c3a52'
            '6f05d722f4b8ba62ff06d2feb7c1b60bf0cad9c32363dc7200846b5812de3c27'
            'f76a1c9edfbf7aa13ad37b1bb8bb0c17b434f8b4eac47645753f2d9d37aaa77b'
            '8b5abe0e4ee2a4808855885dd298852fad8d9ac17c762b3fdaa8deb647e34071'
            'ffc43fea9c15d2d9546725531a8b0256b5d83d19102cf025577f7706ebf2d428'
            '9c83d27439e4e3d2f4d9df9ae022e6dbb840191c6f72f43d69d75ef6e93ff6d6'
            '3e1382d5fe07cff949a05656b88dacc8b94490a1803664ab7ac78310d593d9bc'
            'ad745512118dd7cffe4818aa7d2a6069d5acae4e6d6111acaca270da8643719a'
            '0aeb9867e795b610381bf09d3e3ae8680bbb76cf2de3605e60ec2d75d8a3a4d5'
            '35d52d3f3711ac613a11f4651a5cf170c60fba5130c6a138e5d72516ce7f4768'
            '33447b3c842b577a4293fe51b5b1edaa4894964e363d61047e15ff39e37254a1'
            '7bbde073eb6a31dee68d4932de94a5a073fca52bd2d110c70141ce07a78a0f71'
            '0fd1eb4f28393e12cd3adec9f516452d5c6025c661bba2a8a7085b4107833f1d'
            '3b1bbc334cbcf4c80157d69e9c7782074b296b6605f8db79b35c13d9e571f023'
            '60517fb4bc3f69df9f8da18e762d42acb1d2942a0a04d8d55a345879b9a39264'
            'b241e6bde59cdf3e5162defe07165a46af34a7fed0802886ac7fb711bd6f100a'
            '5e1a60010807000007000000fe7801011500eaff143700002000ffffffff0f01'
            '0001000000000000003ea60479'
        ).is_(
            RakNetPacket(RakNetPacketID.custom_packet_4).that_has(
                Capsule(RakNetCapsuleID.reliable_ordered).that_has(
                    Batch().that_has(
                        GamePacket(MCPEGamePacketID.start_game, True)
                    )
                ),
                Capsule(RakNetCapsuleID.reliable_ordered).that_has(
                    Batch().that_has(
                        GamePacket(MCPEGamePacketID.start_game, True)  # TODO
                    )
                )
            )
        )
        assertion.is_correct_on(self, and_verify_encoded_data=True)


if __name__ == '__main__':
    import unittest
    unittest.main()
