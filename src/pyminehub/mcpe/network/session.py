from typing import Dict, Iterator, Tuple, Union

from pyminehub.mcpe.player import Player
from pyminehub.mcpe.value import PlayerID
from pyminehub.network.address import Address
from pyminehub.raknet import SessionNotFound


class SessionManager:

    def __init__(self) -> None:
        self._players = {}  # type: Dict[Address, Player]
        self._address = {}  # type: Dict[PlayerID, Address]

    def append(self, addr: Address) -> None:
        self._players[addr] = Player()

    def bind(self, player_id: PlayerID, addr: Address) -> None:
        self._address[player_id] = addr

    @property
    def addresses(self) -> Iterator[Address]:
        return iter(self._players.keys())

    def __iter__(self) -> Iterator[Tuple[Address, Player]]:
        return iter((addr, player) for addr, player in self._players.items() if player.has_identity())

    def excluding(self, player: Player) -> Iterator[Tuple[Address, Player]]:
        return iter((addr, p) for addr, p in self._players.items() if p.has_identity() and p != player)

    def __contains__(self, key: Union[PlayerID, Address]) -> bool:
        if isinstance(key, PlayerID):
            return key in self._address
        else:
            return key in self._players

    def __getitem__(self, key: Union[PlayerID, Address]) -> Player:
        if isinstance(key, PlayerID):
            if key not in self._address:
                raise SessionNotFound()
            addr = self._address[key]
        else:
            addr = key
        if addr not in self._players:
            if isinstance(key, PlayerID):
                del self._address[key]
            raise SessionNotFound(addr)
        return self._players[addr]

    def __delitem__(self, key: Address) -> None:
        if key in self._players:
            del self._players[key]
