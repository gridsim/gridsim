import unittest
from gridsim.util import Position


class TestPosition(unittest.TestCase):

    def test_default_position(self):
        default_pos = Position()

        self.assertEqual(Position(0, 0, 0), default_pos)

    def test_distance_to(self):

        # Create a point and output the coordinates.
        office = Position(46.240301, 7.358394, 566)

        # Create a second point.
        home = Position(46.309180, 7.972517, 676)

        # Calculate the difference between the two points.
        dist_to = home.distance_to(office)

        ref_dist_to = 43339.9590758375

        self.assertEqual(dist_to, ref_dist_to)

if __name__ == '__main__':
    unittest.main()
