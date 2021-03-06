from typing import Callable, Dict, Iterator, Tuple, Union

from pyminehub.mcpe.network.player import Player
from pyminehub.mcpe.value import PlayerID
from pyminehub.network.address import Address
from pyminehub.network.handler import SessionNotFound

__all__ = [
    'SessionManager'
]


class SessionManager:

    def __init__(self) -> None:
        self._players = {}  # type: Dict[Address, Player]
        self._address = {}  # type: Dict[PlayerID, Address]

    def __str__(self) -> str:
        return '\n'.join(
            '{} {} {}'.format(addr, player.entity_runtime_id, player.name)
            if player.has_identity else '{}'.format(addr)
            for addr, player in self._players.items())

    def append(self, player: Player, addr: Address) -> None:
        self._players[addr] = player
        self._address[player.id] = addr

    @property
    def addresses(self) -> Iterator[Address]:
        return iter(self._players.keys())

    def __iter__(self) -> Iterator[Tuple[Address, Player]]:
        return iter((addr, player) for addr, player in self._players.items() if player.has_identity)

    def excluding(self, player: Player) -> Iterator[Tuple[Address, Player]]:
        return iter((addr, p) for addr, p in self._players.items() if p.has_identity and p != player)

    def find(self, func: Callable[[Player], bool]) -> Iterator[Tuple[Address, Player]]:
        return iter((addr, p) for addr, p in self._players.items() if p.has_identity and func(p))

    def __contains__(self, key: Union[PlayerID, Address]) -> bool:
        if isinstance(key, PlayerID):
            return key in self._address
        else:
            return key in self._players

    def __getitem__(self, key: Union[PlayerID, Address]) -> Player:
        addr = self.get_address(key) if isinstance(key, PlayerID) else key
        if addr not in self._players:
            raise SessionNotFound(addr)
        return self._players[addr]

    def get_address(self, key: PlayerID) -> Address:
        if key not in self._address:
            raise SessionNotFound()
        return self._address[key]

    def __delitem__(self, key: Address) -> None:
        if key in self._players:
            player = self._players[key]
            del self._players[key]
            del self._address[player.id]
