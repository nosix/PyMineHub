from testcase.codec import *


class ExtraTestCase(CodecTestCase):

    def test_command_request(self):
        assertion = EncodedData(
            '841d000060013011000006000000fe78da93f6656060d12f4b2d6238e5c2633433473e7b89f88bd98f3239f73230000071d20913'
        ).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketType.COMMAND_REQUEST)
                    )
                )
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)


if __name__ == '__main__':
    import unittest
    unittest.main()
