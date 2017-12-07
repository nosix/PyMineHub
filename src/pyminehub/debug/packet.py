def print_packet_info(specs, data_codecs):
    for packet_id, spec in specs.items():
        data_codec = data_codecs[packet_id]
        print(packet_id, ':')
        assert len(spec[1:]) == len(data_codec), '{} != {}'.format(len(spec[1:]), len(data_codec))
        for data_spec, data_codec in zip(spec[1:], data_codec):
            orig_base = str(type(data_codec).__dict__['__orig_bases__'][0])
            print('  ', data_spec[0], ':', data_spec[1].__name__, '=',
                  type(data_codec).__name__ + orig_base.split('DataCodec')[-1])


if __name__ == '__main__':
    # noinspection PyProtectedMember
    from pyminehub.mcpe.network.packet import _game_packet_specs
    # noinspection PyProtectedMember
    from pyminehub.mcpe.network.codec import _game_data_codecs
    print_packet_info(_game_packet_specs, _game_data_codecs)
