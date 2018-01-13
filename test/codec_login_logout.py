from testcase.codec import *


class CodecLoginLogoutTestCase(CodecTestCase):

    def test_login_c00(self):
        assertion = EncodedData(
            '8400000040009000000009869e0aed5f1a87ae00000000003d380300'
        ).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                RakNetFrame(RakNetFrameType.RELIABLE).that_has(
                    ConnectionPacket(ConnectionPacketType.CONNECTION_REQUEST)
                )
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_s01(self):
        assertion = EncodedDataInFile(self).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                RakNetFrame(RakNetFrameType.UNRELIABLE).that_has(
                    ConnectionPacket(ConnectionPacketType.CONNECTION_REQUEST_ACCEPTED)
                )
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_c01(self):
        assertion = EncodedDataInFile(self).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                RakNetFrame(RakNetFrameType.UNRELIABLE).that_has(
                    ConnectionPacket(ConnectionPacketType.CONNECTED_PONG)
                ),
                RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                    ConnectionPacket(ConnectionPacketType.NEW_INCOMING_CONNECTION)
                ),
                RakNetFrame(RakNetFrameType.UNRELIABLE).that_has(
                    ConnectionPacket(ConnectionPacketType.CONNECTED_PING)
                ),
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_c0c(self):
        assertion = EncodedDataInFile(self).is_(
            Batch().that_has(
                GamePacket(GamePacketType.LOGIN)
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=False)

    def test_login_s04(self):
        assertion = EncodedData(
            '840400006000a000000000000000fe7801010800f7ff0702000000000000004e'
            '000a6000a801000001000000fe7801010900f6ff080600000000000000008100'
            '0f'
        ).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketType.PLAY_STATUS)
                    )
                ),
                RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketType.RESOURCE_PACKS_INFO)
                    )
                )
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_c0d(self):
        assertion = EncodedData(
            '840d00006000800b000002000000fe78da63e360606066600000006a0012'
        ).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketType.RESOURCE_PACK_CLIENT_RESPONSE)
                    )
                )
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_s05(self):
        assertion = EncodedData(
            '8405000060009802000002000000fe7801010700f8ff06070000000000005b00'
            '0e'
        ).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketType.RESOURCE_PACK_STACK)
                    )
                )
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_s09(self):
        assertion = EncodedDataInFile(self).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketType.START_GAME)
                    )
                ),
                RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketType.SET_TIME)
                    )
                ),
                RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketType.UPDATE_ATTRIBUTES)
                    )
                ),
                RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketType.AVAILABLE_COMMANDS)
                    )
                ),
                RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketType.ADVENTURE_SETTINGS)
                    )
                ),
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_s0a(self):
        assertion = EncodedDataInFile(self).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketType.SET_ENTITY_DATA)
                    )
                ),
                RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketType.INVENTORY_CONTENT)
                    )
                ),
                RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketType.INVENTORY_CONTENT)
                    )
                )
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_s0c(self):
        assertion = EncodedDataInFile(self).is_(
            Batch().that_has(
                GamePacket(GamePacketType.INVENTORY_CONTENT)
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_s0d(self):
        assertion = EncodedData(
            '840d00006000a80d00000c000000fe7801010900f6ff081f0000010000000001'
            '4e00296000980e00000d000000fe7801010700f8ff06320000000000015d0039'
        ).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketType.MOB_EQUIPMENT)
                    )
                ),
                RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketType.INVENTORY_SLOT)
                    )
                )
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_s0f(self):
        assertion = EncodedDataInFile(self).is_(
            Batch().that_has(
                GamePacket(GamePacketType.PLAYER_LIST)
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_s20(self):
        assertion = EncodedDataInFile(self).is_(
            Batch().that_has(
                GamePacket(GamePacketType.CRAFTING_DATA)
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_c12(self):
        assertion = EncodedData(
            '841200006000700e000004000000fe78da63716560100000013d005a'
        ).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketType.REQUEST_CHUNK_RADIUS)
                    )
                )
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_s21(self):
        assertion = EncodedData(
            '8421000060008822000010000000fe7801010500faff04460000100141005b'
        ).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketType.CHUNK_RADIUS_UPDATED)
                    )
                )
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_s22(self):
        assertion = EncodedData(
            '842200006000b823000011000000fe7801010b00f4ff0a150000f60337e20303'
            '300cf10268'
        ).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketType.UPDATE_BLOCK)
                    )
                )
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_s23(self):
        assertion = EncodedDataInFile(self).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketType.FULL_CHUNK_DATA)
                    )
                )
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_s85(self):
        assertion = EncodedData(
            '84850100600008a002008402000015'
        ).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                    ConnectionPacket(ConnectionPacketType.DISCONNECTION_NOTIFICATION)
                )
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_logout(self):
        assertion = EncodedDataInFile(self).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketType.TEXT)
                    )
                ),
                RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketType.REMOVE_ENTITY)
                    )
                ),
                RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketType.PLAYER_LIST)
                    )
                )
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)


if __name__ == '__main__':
    import unittest
    unittest.main()
