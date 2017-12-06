import runpy


if __name__ == '__main__':
    files = [
        'pyminehub/config',
        'pyminehub/binutil',
        'pyminehub/network/codec',
        'pyminehub/network/packet'
    ]
    for f in files:
        runpy.run_path('../src/{}.py'.format(f), run_name='__main__')
