from codec import *


class LoginLogoutTestCase(CodecTestCase):

    def test_login_logout_c00(self):
        assertion = EncodedData(
            '8400000040009000000009869e0aed5f1a87ae00000000003d380300'
        ).is_(
            RakNetPacket(PacketID.CUSTOM_PACKET_4).that_has(
                Capsule(CapsuleID.RELIABLE).that_has(
                    ConnectionPacket(ConnectionPacketID.CONNECTION_REQUEST)
                )
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_logout_s01(self):
        assertion = EncodedDataInFile(self).is_(
            RakNetPacket(PacketID.CUSTOM_PACKET_4).that_has(
                Capsule(CapsuleID.UNRELIABLE).that_has(
                    ConnectionPacket(ConnectionPacketID.CONNECTION_REQUEST_ACCEPTED)
                )
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_logout_c01(self):
        assertion = EncodedDataInFile(self).is_(
            RakNetPacket(PacketID.CUSTOM_PACKET_4).that_has(
                Capsule(CapsuleID.UNRELIABLE).that_has(
                    ConnectionPacket(ConnectionPacketID.CONNECTED_PONG)
                ),
                Capsule(CapsuleID.RELIABLE_ORDERED).that_has(
                    ConnectionPacket(ConnectionPacketID.NEW_INCOMING_CONNECTION)
                ),
                Capsule(CapsuleID.UNRELIABLE).that_has(
                    ConnectionPacket(ConnectionPacketID.CONNECTED_PING)
                ),
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_logout_c0c(self):
        assertion = EncodedDataInFile(self).is_(
            Batch().that_has(
                GamePacket(GamePacketID.LOGIN)
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=False)

    def test_login_logout_s04(self):
        assertion = EncodedData(
            '840400006000a000000000000000fe7801010800f7ff0702000000000000004e'
            '000a6000a801000001000000fe7801010900f6ff080600000000000000008100'
            '0f'
        ).is_(
            RakNetPacket(PacketID.CUSTOM_PACKET_4).that_has(
                Capsule(CapsuleID.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketID.PLAY_STATUS)
                    )
                ),
                Capsule(CapsuleID.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketID.RESOURCE_PACKS_INFO)
                    )
                )
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_logout_c0d(self):
        config.set_config(batch_compress_threshold=0)  # TODO
        assertion = EncodedData(
            '840d00006000800b000002000000fe78da63e360606066600000006a0012'
        ).is_(
            RakNetPacket(PacketID.CUSTOM_PACKET_4).that_has(
                Capsule(CapsuleID.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketID.RESOURCE_PACK_CLIENT_RESPONSE)
                    )
                )
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_logout_s05(self):
        assertion = EncodedData(
            '8405000060009802000002000000fe7801010700f8ff06070000000000005b00'
            '0e'
        ).is_(
            RakNetPacket(PacketID.CUSTOM_PACKET_4).that_has(
                Capsule(CapsuleID.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketID.RESOURCE_PACK_STACK)
                    )
                )
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_logout_s09(self):
        assertion = EncodedDataInFile(self).is_(
            RakNetPacket(PacketID.CUSTOM_PACKET_4).that_has(
                Capsule(CapsuleID.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketID.START_GAME)
                    )
                ),
                Capsule(CapsuleID.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketID.SET_TIME)
                    )
                ),
                Capsule(CapsuleID.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketID.UPDATE_ATTRIBUTES)
                    )
                ),
                Capsule(CapsuleID.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketID.AVAILABLE_COMMANDS)
                    )
                ),
                Capsule(CapsuleID.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketID.ADVENTURE_SETTINGS)
                    )
                ),
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_logout_s0a(self):
        assertion = EncodedData(
            '840a000060021808000008000000fe7801013700c8ff36270000010700078080'
            'c680808030070100002b01900104040f4d617474654d757373656c3336323026'
            '070127030000803f1d060000004f150b386001b009000009000000fe7801012a'
            '00d5ff2931000000240000000000000000000000000000000000000000000000'
            '0000000000000000000000000013f1007f6000b00a00000a000000fe7801010a'
            '00f5ff09310000780400000000050100b7'
        ).is_(
            RakNetPacket(PacketID.CUSTOM_PACKET_4).that_has(
                Capsule(CapsuleID.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketID.SET_ENTITY_DATA)
                    )
                ),
                Capsule(CapsuleID.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketID.INVENTORY_CONTENT)
                    )
                ),
                Capsule(CapsuleID.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketID.INVENTORY_CONTENT)
                    )
                )
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_logout_s0c(self):
        assertion = EncodedDataInFile(self).is_(
            Batch().that_has(
                GamePacket(GamePacketID.INVENTORY_CONTENT)
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_logout_s0d(self):
        assertion = EncodedData(
            '840d00006000a80d00000c000000fe7801010900f6ff081f0000010000000001'
            '4e00296000980e00000d000000fe7801010700f8ff06320000000000015d0039'
        ).is_(
            RakNetPacket(PacketID.CUSTOM_PACKET_4).that_has(
                Capsule(CapsuleID.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketID.MOB_EQUIPMENT)
                    )
                ),
                Capsule(CapsuleID.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketID.INVENTORY_SLOT)
                    )
                )
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_logout_s0f(self):
        assertion = EncodedDataInFile(self).is_(
            Batch().that_has(
                GamePacket(GamePacketID.PLAYER_LIST)
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_logout_s20(self):
        assertion = EncodedDataInFile(self).is_(
            Batch().that_has(
                GamePacket(GamePacketID.CRAFTING_DATA)
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_logout_c12(self):
        assertion = EncodedData(
            '841200006000700e000004000000fe78da63716560100000013d005a'
        ).is_(
            RakNetPacket(PacketID.CUSTOM_PACKET_4).that_has(
                Capsule(CapsuleID.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketID.REQUEST_CHUNK_RADIUS)
                    )
                )
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_logout_s21(self):
        assertion = EncodedData(
            '8421000060008822000010000000fe7801010500faff04460000100141005b'
        ).is_(
            RakNetPacket(PacketID.CUSTOM_PACKET_4).that_has(
                Capsule(CapsuleID.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketID.CHUNK_RADIUS_UPDATED)
                    )
                )
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_logout_s22(self):
        assertion = EncodedData(
            '842200006000b823000011000000fe7801010b00f4ff0a150000f60337e20303'
            '300cf10268'
        ).is_(
            RakNetPacket(PacketID.CUSTOM_PACKET_4).that_has(
                Capsule(CapsuleID.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketID.UPDATE_BLOCK)
                    )
                )
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_logout_s23(self):
        assertion = EncodedDataInFile(self).is_(
            RakNetPacket(PacketID.CUSTOM_PACKET_4).that_has(
                Capsule(CapsuleID.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketID.FULL_CHUNK_DATA)
                    )
                )
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_logout_s85(self):
        assertion = EncodedData(
            '84850100600008a002008402000015'
        ).is_(
            RakNetPacket(PacketID.CUSTOM_PACKET_4).that_has(
                Capsule(CapsuleID.RELIABLE_ORDERED).that_has(
                    ConnectionPacket(ConnectionPacketID.DISCONNECTION_NOTIFICATION)
                )
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)


if __name__ == '__main__':
    import unittest
    unittest.main()
