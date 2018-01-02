"""
This is a simple proxy server that can be used when connecting to RaspberryPi Zero via USB.

In RaspberryPi Zero, edit /etc/dhcpcd.conf and set a static IP.

  interface usb0
  static ip_address=192.168.2.2/24
  static routers=192.168.2.1
  static domain_name_servers=192.168.2.1 8.8.8.8

Then, start PyMineHub server in RaspberryPi Zero and start this server.
"""
import asyncio


_SERVER_ADDRESS = ('192.168.2.2', 19132)


class _ProxyProtocol(asyncio.DatagramProtocol):

    def sendto(self, data: bytes, addr: tuple) -> None:
        raise NotImplementedError()


class _ClientProtocolImpl(_ProxyProtocol):

    def __init__(self, protocol: _ProxyProtocol, addr: tuple) -> None:
        self._server_protocol = protocol
        self._addr = addr
        self._transport = None

    def connection_made(self, transport: asyncio.DatagramTransport) -> None:
        self._transport = transport

    def datagram_received(self, data: bytes, addr: tuple) -> None:
        self._server_protocol.sendto(data, self._addr)

    def sendto(self, data: bytes, addr: tuple) -> None:
        if self._transport is None:
            print('Drop', addr, data.hex())
        else:
            self._transport.sendto(data, addr)


class _ServerProtocolImpl(_ProxyProtocol):

    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop
        self._clients = {}
        self._transport = None

    def connection_made(self, transport: asyncio.DatagramTransport) -> None:
        self._transport = transport

    def datagram_received(self, data: bytes, addr: tuple) -> None:
        port = addr[1]
        if port not in self._clients:
            client = _ClientProtocolImpl(self, addr)
            listen = self._loop.create_datagram_endpoint(lambda: client, local_addr=('0.0.0.0', port))
            asyncio.ensure_future(listen, loop=self._loop)
            self._clients[port] = client
        self._clients[port].sendto(data, _SERVER_ADDRESS)

    def sendto(self, data: bytes, addr: tuple) -> None:
        self._transport.sendto(data, addr)


def run():
    loop = asyncio.get_event_loop()
    listen = loop.create_datagram_endpoint(
        lambda: _ServerProtocolImpl(loop), local_addr=('0.0.0.0', 19132)
    )
    transport, protocol = loop.run_until_complete(listen)  # non-blocking
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        pending = asyncio.Task.all_tasks()
        try:
            loop.run_until_complete(asyncio.gather(*pending))
        except asyncio.CancelledError:
            pass
    transport.close()
    loop.close()


if __name__ == '__main__':
    run()
