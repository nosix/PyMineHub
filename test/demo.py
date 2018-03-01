import math
import time

from plugin.action import ActionCommandMixin
from pyminehub.mcpe.const import EntityType
from pyminehub.mcpe.geometry import Face
from pyminehub.mcpe.main.client import connect
from pyminehub.mcpe.network import MCPEClient, EntityInfo, EntityEvent


class _Client(MCPEClient, ActionCommandMixin):

    @property
    def client(self) -> MCPEClient:
        return self


def run():
    with connect('127.0.0.1', player_name='', client_factory=_Client, timeout=30) as client:
        player = client.get_entity()
        mobs = []

        def mob_added(event: EntityEvent, info: EntityInfo):
            if event is EntityEvent.ADDED and info.owner_runtime_id == player.entity_runtime_id:
                mobs.append(info.entity_runtime_id)

        client.set_entity_event_listener(mob_added)

        base_position = player.position + (0, 0, 2)

        client.spawn_mob(EntityType.CHICKEN, base_position.x, base_position.y, base_position.z)
        client.spawn_mob(EntityType.CHICKEN, base_position.x, base_position.y, base_position.z)
        client.spawn_mob(EntityType.CHICKEN, base_position.x, base_position.y, base_position.z)

        while len(mobs) != 3:
            if not client.wait_response(10):
                raise AssertionError('timeout')

        def move(
                index: int,
                x: float=0.0, y: float=0.0, z: float=0.0,
                pitch: float=0.0, yaw: float=0.0, head_yaw: float=0.0,
                on_ground: bool=True
        ):
            entity = client.get_entity(mobs[index])
            client.move_mob(
                mobs[index],
                *entity.position + (x, y, z),
                pitch=entity.pitch + pitch, yaw=entity.yaw + yaw, head_yaw=entity.head_yaw + head_yaw,
                on_ground=on_ground)

        def jump_up(y: float):
            move(0, y=y, on_ground=False)
            time.sleep(0.1)
            move(1, y=y, on_ground=False)
            time.sleep(0.1)
            move(2, y=y, on_ground=False)

        def jump_down(y: float):
            move(0, y=-y)
            time.sleep(0.1)
            move(1, y=-y)
            time.sleep(0.1)
            move(2, y=-y)

        def rotate(yaw: float):
            move(0, yaw=yaw)
            time.sleep(0.1)
            move(1, yaw=yaw)
            time.sleep(0.1)
            move(2, yaw=yaw)

        def circle(index: int, radius: float, step: int, start: Face):
            start_position = client.get_entity(mobs[index]).position
            o = start_position + start.inverse.direction * radius
            for i in range(step):
                degree = (i + 1) * (360 / step) + start.yaw
                x = radius * math.sin(math.radians(degree))
                z = radius * math.cos(math.radians(degree))
                client.move_mob(mobs[index], o.x - x, o.y, round(o.z + z, 1))
                time.sleep(0.1)
            while client.get_entity(mobs[index]).position != start_position:
                client.wait_response(10)

        time.sleep(1)

        move(0, x=-2)
        move(2, x=+2)

        time.sleep(1)

        for _ in range(3):
            jump_up(2)
            time.sleep(0.1)
            jump_down(2)

        for _ in range(4):
            rotate(90)

        for _ in range(4):
            rotate(-90)

        circle(0, 1, 12, Face.WEST)
        circle(2, 1, 12, Face.EAST)
        circle(1, 1, 12, Face.SOUTH)

        rotate(180)

        time.sleep(1)

        jump_up(10)

        time.sleep(3)

        for mob_id in mobs:
            client.remove_mob(mob_id)


if __name__ == '__main__':
    run()
