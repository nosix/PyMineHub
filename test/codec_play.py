from testcase.codec import *


class PlayTestCase(CodecTestCase):

    def test_move_player(self):
        assertion = EncodedData(
            '841700006000f80f000005000000fe78da93176660e0626068707e5e9de604a21920e00018333200005cb8054e'
        ).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketType.MOVE_PLAYER)
                    )
                )
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_sound_event(self):
        assertion = EncodedDataInFile(self).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketType.SOUND_EVENT),
                        GamePacket(GamePacketType.MOVE_PLAYER)
                    )
                )
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_player_action(self):
        assertion = EncodedDataInFile(self).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketType.PLAYER_ACTION),
                        GamePacket(GamePacketType.MOVE_PLAYER)
                    )
                )
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)


if __name__ == '__main__':
    import unittest
    unittest.main()
