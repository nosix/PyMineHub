from codec import *


class LoginLogoutTestCase(CodecTestCase):

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
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

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
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

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
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

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
                        GamePacket(MCPEGamePacketID.start_game)
                    )
                ),
                Capsule(RakNetCapsuleID.reliable_ordered).that_has(
                    Batch().that_has(
                        GamePacket(MCPEGamePacketID.set_time)
                    )
                ),
                Capsule(RakNetCapsuleID.reliable_ordered).that_has(
                    Batch().that_has(
                        GamePacket(MCPEGamePacketID.update_attributes)
                    )
                ),
                Capsule(RakNetCapsuleID.reliable_ordered).that_has(
                    Batch().that_has(
                        GamePacket(MCPEGamePacketID.available_commands)
                    )
                ),
                Capsule(RakNetCapsuleID.reliable_ordered).that_has(
                    Batch().that_has(
                        GamePacket(MCPEGamePacketID.adventure_settings)
                    )
                ),
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_logout_05(self):
        assertion = EncodedData(
            '840a000060021808000008000000fe7801013700c8ff36270000010700078080'
            'c680808030070100002b01900104040f4d617474654d757373656c3336323026'
            '070127030000803f1d060000004f150b386001b009000009000000fe7801012a'
            '00d5ff2931000000240000000000000000000000000000000000000000000000'
            '0000000000000000000000000013f1007f6000b00a00000a000000fe7801010a'
            '00f5ff09310000780400000000050100b7'
        ).is_(
            RakNetPacket(RakNetPacketID.custom_packet_4).that_has(
                Capsule(RakNetCapsuleID.reliable_ordered).that_has(
                    Batch().that_has(
                        GamePacket(MCPEGamePacketID.set_entity_data)
                    )
                ),
                Capsule(RakNetCapsuleID.reliable_ordered).that_has(
                    Batch().that_has(
                        GamePacket(MCPEGamePacketID.inventory_content)
                    )
                ),
                Capsule(RakNetCapsuleID.reliable_ordered).that_has(
                    Batch().that_has(
                        GamePacket(MCPEGamePacketID.inventory_content)
                    )
                )
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_logout_06(self):
        assertion = EncodedData(
            'fe78da3dd851641d5918c0f1e636e9465d2b0f798815ab2a2a561eb22b561ea2'
            'fa5057ad6bd5ea43ac58b1f2102b0fb1f2d05d7da8888a888a8a8aa88a888a8a'
            'aaaa88ba46c435222a2a628c11511151a3aaaa6a55c5de9dffff6c1fceef9cb9'
            '67e69cf9be734e46e72f7d7fe6cc5f732de74b671affce4f36432b94a10ddaff'
            'e37ea904747ddc5482d0e4d686656dd3e2ee23ba27f08e67bd870ff0093ec21d'
            '7afe5194b35cbb0b7310c336a4f4cfe0186ef3db1bd8f00dce164cb730a373dc'
            '0e191cc021ccd3739367eef2941d5add45797456262f68a70e68aff66bb3b669'
            'bbf6699796b547bbb5553bfef32573d92c09b368d8a903daabfddaac6ddaae7d'
            'daa565edd16e6dd5621693cc6290927b6a4ca9e650356fa995c2cf0c5d73e841'
            '9a83a1d509c5bd6f4b3eb88316577f2d2ed69b848b751763ddc5f880f4bc72f4'
            'd7f47ec2d5d6a21c2eca3512de4bc9c37ab9e984e14f1cf7c467655c7e0abf14'
            'e58da29ce1d29f45d95394eb25e1de759ff5aa14a65734f77d24d35b830a2599'
            'ad10980a79ad90d60a59adf0900a91ac10c90a19ad90d00a51a990ce0ad9ac30'
            'a70ae14d9843e2524a5c4a894b297129252ea5c4a927e633319f894b29712925'
            'e63d7129252ea5c488242ea58c97cedc4f99fb29733f65eea7ccfd94b99f32f7'
            '53e67ecadc4f99fb29733f65eea7ccfd94b99f32f753caf0a9c3a70e9f3a7cea'
            'f0a9c3a70e9f3a7ceaf0a9c3a70e9f3a7ceaf0a9c3a70e9f3afc0aeb33250751'
            '80c944a622321591a9884c45642a225311998ac85444a622321591a9884c4564'
            '2a2253b1412cb62186c40d05fbf00236610bf6600722d88575a8411dee059806'
            '1bf21cefd4cc16a4c70151223adf166567518e17e5773c864e178a7292becfe0'
            '1b6ee7c906c35819022368203a8afe1df45fe6b91729b97691bb2ef2a83aa3d4'
            '1da0ab6875d9a067173db7e8b965cf72d12adba067999e6526546696bb84638f'
            'bf4efb30ff1599e1b77bb4e688e25d588069ba4c71df0a3d7779af575cfc026b'
            '5c5c87cb4ce9d0905d66a287c6eca7a24f95929faafc52a57f9577a8f20e5562'
            '5b654d5759e28704e4b0f4ffa3db9495dce20e68714730cb46b359fbb547bbb5'
            '553bb457db343cbe4fbb74408b17d8270c8770a52897683c8403e6ffc02f12a6'
            '774ab8135a2fe0006e430a1be4a7466b8ffb9ec37dd2748f2e3b7459a255a7f5'
            '73515e67bb36118b6d6db407903f31e61eb66094e91ab553a3786ab44e8dcea9'
            '516e38ae837a45ab7a53afe9840ee9b08ee8a88ee9549395855079102ad3a1b2'
            '192a1ba1321f2ab3a1723b54e642a5162a5775295c781e2af550d90e95835059'
            '0d959550590b9534548e4365e96ce81c2a03fab4e8f27b11f5af498bdf277e61'
            '73dcbd213b1fb87844ca2f51ba4ffc4c85014e0596cd011cc34778eb8a84430f'
            '57f804ef2085d7f006fe81f790c111e4f0193ec0022cb992611d56e1213cf268'
            '821a3c8107b00293f002d6601196e1366cc063a8430cdbf01276600666039c1a'
            '0d3bf5827669b7f668aff669bf0ee815bdaad7b4aad7f5860eea900eeb888eea'
            '988eeb84ded45bca7e6854a642653a546643652e54d84ecf595b0bb00b775c4e'
            'b4f2008b32f7d4cd3d3d734fdbdcd336f734ce3dd4730ff5dcd337f71cca3d87'
            '72cfa1dc7328f71ccadd50b9e74feea6ce3d7772cfa386d7f5860eea900eeb88'
            '8eea988eeb84ded45b4a5cf37070e5e198cac359948723e8a9abb04578f5d850'
            'c4be52ec2bc7be6a6c686343191bcad890c4862e36e4b1a18b0d656c4a62433f'
            '424e39583ec19e9f4ab4364c344cc20c47d02c3ce355268af26f1e45bfe592f8'
            'e5e48742ceb136c66ea6cf14fcc631c3d83fb0a5cff12e0d5bb54ddb31742b06'
            '79e2ff2ff088c80dedbc0ddf8ce19e312c9bf4fa025b9e367e5bf827d92f27fe'
            '089f7822c3117c8477f01e3e73df31adc7f0908b4bc4e11117a7b8b84a6b31c0'
            '8c174ddca2895d74012cba00a678dd1f8bb29fb7e1d29cafee678a1f528bfedf'
            'cc1dff5b855f67e1111757fd3f131e70b75998d09c5f99300fd3be972f4b6b99'
            'd6335a2f6188bf00fee427e73921390d3b75407bb55f9bb54ddbb54fbbb4ac3d'
            'daadad5aec857f0132c2c56d'
        ).is_(
            Batch().that_has(
                GamePacket(MCPEGamePacketID.inventory_content)
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)

    def test_login_logout_07(self):
        assertion = EncodedData(
            '840d00006000a80d00000c000000fe7801010900f6ff081f0000010000000001'
            '4e00296000980e00000d000000fe7801010700f8ff06320000000000015d0039'
        ).is_(
            RakNetPacket(RakNetPacketID.custom_packet_4).that_has(
                Capsule(RakNetCapsuleID.reliable_ordered).that_has(
                    Batch().that_has(
                        GamePacket(MCPEGamePacketID.mob_equipment)
                    )
                ),
                Capsule(RakNetCapsuleID.reliable_ordered).that_has(
                    Batch().that_has(
                        GamePacket(MCPEGamePacketID.inventory_slot)
                    )
                )
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)


if __name__ == '__main__':
    import unittest
    unittest.main()
