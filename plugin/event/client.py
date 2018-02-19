from pyminehub.mcpe.const import SoundType, SpaceEventType, EntityEventType
from pyminehub.mcpe.geometry import Vector3
from pyminehub.mcpe.main.client import connect
from pyminehub.mcpe.network import MCPEClient
from pyminehub.mcpe.value import EntityRuntimeID


class GameEventCommandMixin:

    @property
    def client(self) -> MCPEClient:
        raise NotImplementedError()

    def sound_event(
            self,
            event_type: SoundType,
            position: Vector3[float],
            data: int=0,
            pitch: int=0
    ) -> None:
        x, y, z = position
        self.client.execute_command(
            '/sound_event {} {} {} {} {} {}'.format(
                event_type.name.lower(), x, y, z, data, pitch))

    def space_event(
            self,
            event_type: SpaceEventType,
            position: Vector3[float],
            data: int=0
    ) -> None:
        x, y, z = position
        self.client.execute_command(
            '/space_event {} {} {} {} {}'.format(
                event_type.name.lower(), x, y, z, data))

    def entity_event(
            self,
            event_type: EntityEventType,
            entity_runtime_id: EntityRuntimeID,
            data: int=0
    ) -> None:
        self.client.execute_command(
            '/entity_event {} {} {}'.format(
                event_type.name.lower(), entity_runtime_id, data))


class GameEventCommandClient(MCPEClient, GameEventCommandMixin):

    @property
    def client(self) -> MCPEClient:
        return self


if __name__ == '__main__':
    import time

    with connect('127.0.0.1', client_factory=GameEventCommandClient) as _client:
        _entity = _client.get_entity()

        for e in _client.entities:
            if e.entity_runtime_id != _client.entity_runtime_id:
                _entity = e
                break
        else:
            print('Login by other player.')

        _client.sound_event(SoundType.HURT, _entity.position)
        time.sleep(1)

        _client.space_event(SpaceEventType.SOUND_GHAST, _entity.position)
        time.sleep(1)

        _client.entity_event(EntityEventType.HURT_ANIMATION, _entity.entity_runtime_id)
        time.sleep(1)
