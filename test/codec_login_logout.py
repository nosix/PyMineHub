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

    def test_login_logout_08(self):
        assertion = EncodedData(
            'fe78daed9a5b6c1c571980273cf186c4032a50f1b05c14c4aeb5376fb676916b'
            '89a6896b53e3124572e254637b9cdd78ed35bbb37162cb8a894a439a94a2802a'
            '456afb02528325704b30829480040251b50f04aab6e94591aa1435d036d0d73c'
            '0ce73f9e7ffc9f7fcfccae7766e34b98d5af73e69cb99cefbfed9c39f3c2d33b'
            '7a0cc3d8f15cd79993734f9e7cf5fc273f7dd7f35f78ff7b9ff8d48069dbd640'
            'ad5ab54a995c3af9d5b154deca759a6662d7683a95c8e632bb12f78ce63289bc'
            '399e1307a4ad8964ea91de92756c717187d1607beffc038e94277a9cbaba28df'
            '584c074aa3eb37daae9def5f95b3f7d7d74579e5443e50c26e9415f9dffed1bd'
            'b27cff997e8f73e9f4214522e327acc8ffdab95e59befbcc90c7f9dc695391c8'
            'f85d5e60453d487e571fc8fef4fca022a88328ec0fbcc08a7a90fcae3e90fdfc'
            'dc9022a88328ecaff0931880f6b6f3bbbc1e3f890168bf1dfc20929fc402ec03'
            'ffb5bffca4edfc20929fc402ec03ff3b7ffe697bf959bea3b10fd2767e96ef68'
            'ec83b49bdf8b759aff890f20bf4ea2e0f7629de67fe203c8af9328f869de439b'
            '73ff0f92b0f7a7790f6dcefd3f481a6d948dfa358f77afd4fc1fea8ea37ad395'
            '787dca46fd9ac7bb576afe0f75c751bde94abcbe2f87cfb831fe398b9fcebc76'
            '8d0f419b2f87cfb831fe398b9fcebc768d0f415bd0b83927b0fffb1f17a52876'
            '467d31bb73bd501fc36b068d9b7302fb8dbfaf4851ec8cfa6276e77aa13e86d7'
            'e436c5b8c636ac23fbc76f5e72aebffc3329341f7ad7a036663ad2c504b729dd'
            'f83e70ffe7eaef028f516ccc74a48b09c59f998da10e9cb76edd72be38fa25c9'
            'fef13b7f947568833efa2c18940fa87e695df16797056d0c5bb5ef6e43dccbe8'
            '9ccf798c508736e843663c3728e6b95f411dc78f769736168c9255c847affdda'
            'b979f5458f5d966f5d763e7afdb7b28e7ad2726a6242d91782ff6f98cfa58ddf'
            'fe93b433b735b6739ff074c8393531a1ec83ffb378471f97acc8eb96375f7c41'
            '0aea0675e5e9c027c7d37ccaf30a8f77f471c98a7a70cb0f2f5f9482ba415d79'
            '3af0c9f1349ff2bc42c78b7e4fedef096d23baa9636ff47f88b9029f9fc878d1'
            'efa9fd3da16d443775ec8dfe0f31dfb86d7c1bef8d3b5476eedca948a3e789b9'
            '9559e7b15366dd7b00e42fdc9f0c9486d75f9e7550deb8f463a97f28bf95fab2'
            '0112768b8a9f0af0a3ef47c2bfb235f8f11918eaede04776288fdc973440360b'
            'bf974785d0bc10a5ff47c1efe9d3d5298ce1f8beaf3b8bc3f739537d19b90f7a'
            'c0f2ecef1f97b2f0cb3929deb9eef9d0c7f9f933a076aec1fe3fbfbb72c23973'
            'e9fb0eb5375e1fdae5bdd9d8a11dfb8de565434a13f6c66b0363e59b39c90f42'
            'd9b15eeeef94ba018163e9fd717c8f9f9950f8d107e87f001ecfe71bc08dec1e'
            '3fcacaacc70ef7e1f7c673a06f3dfc9413f950177efda01fc9afb18f1cdf1385'
            'b5b902f9efe73cc88b82f653f8898f511b73fb63fb7af951681c22df7af96797'
            '6b5e8c800e40905d8917f73c3a66ca0dc742b97872d839757a540ad421b69efc'
            'e1a42c83fa5ae147ff7eecd06e2950e7fd3c5f71fb507ef453c9feab39ad3feb'
            'f83dfd09b9fed20545d0a74082fa9616260c90465b7777b783827cc7be7daf14'
            'b43b3d66f7eedd8a28f61725325326caa6f02fabf14cf9b1e46cf4d99bea01fb'
            'b06c967fefdebd0e0af00d0f0f3b23232352a00e6df49881810167fffefd52a0'
            'cef9b9ed390f8f176a6face3b9c84f5991ffc6df96e5fe07affe46cc43976449'
            '9fcf5be107314dd3999c9c940275de5fc7bfa2fa3f8e1be380b228fcec787a2c'
            '3d07b89013ca1b57d67470f3ea65d9fedecb3f776ebef98735dd5c69deffa9ed'
            'fdf8a90f70febbf29f713ed7f359af7c68b15fe1a7f900fae018ddf1f2d8e76d'
            'e51ce8033e2a92df9d7fc13e70639f372f5b87fd8101646868c8f3ffb1b13129'
            'e8ffd087c7f5f5f53983838352a04e7d1f4ae042a1acb84f731f08efa7ba0141'
            '36e0943646c66b7fade7176dd0f72f517faa7cc000590fffc18307ebec0f6deb'
            'e1e7f18eff634afc6b8ee73903db911b5925a3cb897dd88fed20cdf2f7f4f438'
            '28c00a769f999991027568a3c7ecd9b3c7e9efef970275dd3328fc6fd406f38a'
            '409bccff2bfefc5ca04f72bb71eef113ffa73ed00aff466d9665b576e2d9b386'
            'b1b4244b98efe0bc37aaf9efa6df80fd9557648973be3b925fd81f99510f51cc'
            'ff37fd46fc9fb36f4bfe43870ce3c8913579f4d1551d80d0769073e756656e6e'
            '4db6faf6e083865128acca8913ab73ba0b170ce3d96757f741681f08ea0164ab'
            '6f607fca0fecc87927f283dd81f10eb17fe51b5f339e7aa457caa97ddd063ed7'
            '83c03e08f663fb0f0afb3cd9ea9b8e1f9eeb6449dab72bbfd5fd152dbf943b8c'
            '9f32727e1a1bdb919fdb98f2f3dcb09df831fe393f8d7fee1b0b23fd9e6cf52d'
            '88df2fff6f477e146002bf86f23b0fa48c8587729e60fb46f2875d3f956b449a'
            'f5eda6e737383f72e7c7b7fbfd40587eba4ed6123fb0bb7ad888f70351f0c37a'
            '215fdf6e7afcc82fca8d783f109a1fd835df3734cd7f9bdf0ff0ef03e09b015c'
            '1fa5ebe674fd9cae6fd077a168fba0b53238078ef1e63a1bfc7e80af0fe3da31'
            '5f3ff6fd7e80f0e1f701756bdf41ebfbf07e00379c03a21fe0fc90f6453c3fe4'
            'fcc00425f0e1fa7153ebe76c7d5ff77d87767d1fec4ff9e1fd006c747edc667e'
            'ba368edf8fe87c5fc71f7a7d9ff303376cf4fdc86de26fe5fb81b0ebfbf07c84'
            '1bce01d0fef87c085bbbe68761bf1f08bbbeefc74fe707ede40ffbfd80dffa3e'
            'b2d2f56fddfa3ecc0f370b7f2bdf0f503e58e7a3ebfbd80eebfb7efcefbefe0b'
            'e3c37fbe2405ead7dfba68fcf7832bb2c47d5ac7bea8f95bfd7ea0d1fabe5f9f'
            'cefe68635927ef07a86f446dffb0df0fd4ade1ba7cc0ead7c7edef67e3a0bea8'
            'e68761bf1fa06bfb1e2359dfa73af0fa84e8f21fb53f7d3f40fba27e3f10f6fb'
            '01e0c238e76bf8daef5b34fcbaf703d0d7d4fb81bb0f5be529cbae1cef28d4a6'
            'cce97271bc63ac56b5cb530f978a53973f3f1fabeb8f75cdc746cbd35635d675'
            '603e366d4e59b12ed1307e3c168fcd148f966dd19e8ca7b3f1e4483c36561b75'
            '0f2c578a878bd3a29ac8c653e978222d7aabc53971f2813c3464c57eeda8d84b'
            'e5e2a9dcc8c2c842dcbbfaac59acdae2f2d3d651ab32644d8f5b9558975da959'
            'f48ee21a497a52c132c79b1f92e84c64e990c40f4794840b2b9736ed68ae9c49'
            'cb138bd31325d316bdc98ece85110d27b9b7b872c1eead4c9101243ae3e9b4ef'
            '08f25cdd5945ddd9649dba4bd604bb43d00db2cd5d3f1e9b2a562a651fa07eeb'
            '30054a75dcb36a4f3d5246742703eea94752efd1e016c98e5433b76054e2966b'
            '013366ce58102cb675ccae55acd9e2b85d8875e5b2716c2958801eeb125e501f'
            '51f26ce664898ccf683b8553c94e77ac29185e3ca53ab018ab70b24ad12c89cb'
            '9ba59982195307cc32405773a1bf1a0c8acb4e98a5aaa5b95d5dcc689dae6255'
            '2d1be31bd5eb5e32028714dacee655ef2031a5dcbc5d0126efb7d7b6942016f6'
            'ea9426d36539b3624ddb74a44c730f972c715644119b0705295929dda9771f86'
            '54378ab08acba4d73b8eb5406fc68d4226011163dc95e0fe83e6b45d8d32d5e8'
            'cd3153aeaa176f681f3eb0f079566fa0d591259a1cda11736cd25ac71f6aa3a7'
            '87669d2628f7c1d34ff4f92f4cba4b757406c433f452a564a2487901b74cec6a'
            '744f9af6688ecb76f866395d766c25f1855155c4c92fac0aff9f000312e0a6c9'
            '779b33bb2d18ff03d0d504c3'
        ).is_(
            Batch().that_has(
                GamePacket(MCPEGamePacketID.player_list)
            )
        )
        assertion.is_correct_on(self, and_verified_with_encoded_data=True)


if __name__ == '__main__':
    import unittest
    unittest.main()
