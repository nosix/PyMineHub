import asyncio
import logging

from pyminehub.binutil.converter import DataCodecContext, pop_first
from pyminehub.binutil.instance import B_INT_DATA
from pyminehub.network.address import Address
from pyminehub.network.handler import Protocol, Reliability, GameDataHandler, SessionNotFound

__all__ = [
    'TcpProtocol'
]


_logger = logging.getLogger(__name__)


class TcpProtocol(asyncio.Protocol, Protocol):

    def __init__(self, handler: GameDataHandler) -> None:
        self._handler = handler
        self._transport = None
        self._dest_addr = None
        self._buffer = bytearray()
        self._length = None

    @property
    def destination_address(self) -> Address:
        return self._dest_addr

    # asyncio.Protocol methods

    def connection_made(self, transport: asyncio.Transport) -> None:
        self._dest_addr = transport.get_extra_info('peername')
        self._transport = transport
        self._handler.register_protocol(self, self._dest_addr)

    def connection_lost(self, exc: Exception) -> None:
        _logger.info('%s TCP connection lost. (exception=%s)', self._dest_addr, exc)
        if exc is not None:
            try:
                self._handler.disconnect(self._dest_addr)
            except SessionNotFound as exc:
                assert exc.addr == self._dest_addr, '{} != {}'.format(exc.addr, self._dest_addr)
        self._handler.remove_protocol(self._dest_addr)
        self._transport = None

    def data_received(self, data: bytes) -> None:
        self._buffer += data
        context = DataCodecContext()
        while True:
            if self._length is None:
                if len(self._buffer) >= 4:
                    self._length = B_INT_DATA.read(self._buffer, context)
                    context.clear()
                else:
                    break
            if len(self._buffer) >= self._length:
                try:
                    self._handler.data_received(pop_first(self._buffer, self._length), self._dest_addr)
                    self._length = None
                except SessionNotFound as exc:
                    assert exc.addr == self._dest_addr, '{} != {}'.format(exc.addr, self._dest_addr)
                    if not self._transport.is_closing():
                        self._transport.write_eof()
                    break

    # Protocol methods

    def game_data_received(self, data: bytes, addr: Address, reliability: Reliability) -> None:
        assert self._dest_addr == addr
        buffer = bytearray()
        context = DataCodecContext()
        B_INT_DATA.write(buffer, len(data), context)
        buffer += data
        if not self._transport.is_closing():
            self._transport.write(buffer)
