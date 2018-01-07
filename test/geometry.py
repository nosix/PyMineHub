from unittest import TestCase

from pyminehub.mcpe.geometry import Vector3, OrientedBoundingBox


class GeometryTestCase(TestCase):

    def test_collision_yaw_equals_0(self):
        box_o = OrientedBoundingBox.create(Vector3(10.0, 10.0, 10.0), Vector3(1, 2, 3), 0)

        box_x1 = OrientedBoundingBox.create(Vector3(11.0, 10.0, 10.0), Vector3(1, 2, 3), 0)
        self.assertTrue(box_o.has_collision(box_x1))

        box_x2 = OrientedBoundingBox.create(Vector3(11.1, 10.0, 10.0), Vector3(1, 2, 3), 0)
        self.assertFalse(box_o.has_collision(box_x2))

        box_y1 = OrientedBoundingBox.create(Vector3(10.0, 12.0, 10.0), Vector3(1, 2, 3), 0)
        self.assertTrue(box_o.has_collision(box_y1))

        box_y2 = OrientedBoundingBox.create(Vector3(10.0, 12.1, 10.0), Vector3(1, 2, 3), 0)
        self.assertFalse(box_o.has_collision(box_y2))

        box_z1 = OrientedBoundingBox.create(Vector3(10.0, 10.0, 13.0), Vector3(1, 2, 3), 0)
        self.assertTrue(box_o.has_collision(box_z1))

        box_z2 = OrientedBoundingBox.create(Vector3(10.0, 10.0, 13.1), Vector3(1, 2, 3), 0)
        self.assertFalse(box_o.has_collision(box_z2))

    def test_collision_yaw_equals_90(self):
        box_o = OrientedBoundingBox.create(Vector3(10.0, 10.0, 10.0), Vector3(1, 2, 3), 90)

        box_x1 = OrientedBoundingBox.create(Vector3(12.0, 10.0, 10.0), Vector3(1, 2, 3), 0)
        self.assertTrue(box_o.has_collision(box_x1))

        box_x2 = OrientedBoundingBox.create(Vector3(12.1, 10.0, 10.0), Vector3(1, 2, 3), 0)
        self.assertFalse(box_o.has_collision(box_x2))

        box_y1 = OrientedBoundingBox.create(Vector3(10.0, 12.0, 10.0), Vector3(1, 2, 3), 0)
        self.assertTrue(box_o.has_collision(box_y1))

        box_y2 = OrientedBoundingBox.create(Vector3(10.0, 12.1, 10.0), Vector3(1, 2, 3), 0)
        self.assertFalse(box_o.has_collision(box_y2))

        box_z1 = OrientedBoundingBox.create(Vector3(10.0, 10.0, 12.0), Vector3(1, 2, 3), 0)
        self.assertTrue(box_o.has_collision(box_z1))

        box_z2 = OrientedBoundingBox.create(Vector3(10.0, 10.0, 12.1), Vector3(1, 2, 3), 0)
        self.assertFalse(box_o.has_collision(box_z2))


if __name__ == '__main__':
    import unittest
    unittest.main()
