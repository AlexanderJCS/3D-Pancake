import numpy as np

import unittest

from processing.mesh import interp


class TestInterp(unittest.TestCase):
    def test_interp(self):
        vertices = np.array([[1, 1], [2, 1], [1, 2], [2, 2]])
        values = np.array([0, 1, 1, 2])

        # Test the corners
        self.assertEqual(interp(vertices, values, np.array([[1, 1]])), 0)
        self.assertEqual(interp(vertices, values, np.array([[2, 1]])), 1)
        self.assertEqual(interp(vertices, values, np.array([[1, 2]])), 1)
        self.assertEqual(interp(vertices, values, np.array([[2, 2]])), 2)

        # Test the middle
        self.assertEqual(interp(vertices, values, np.array([[1.5, 1.5]])), 1)

        # Test extrapolation
        # self.assertEqual(interp(vertices, values, np.array([[0, 1]])), -1)
        # self.assertEqual(interp(vertices, values, np.array([[1, 0]])), -1)

    def test_real_world(self):
        """
        Tests the interp function with real world data
        """

        xy = np.array([
            [260.62501686, 1135.26210923],
            [522.6748873, 1934.23742692],
            [805.47019885, 1623.5213609],
            [-22.17029468, 1445.97817525]
        ])

        z = np.array([464.59722127, 229.20921326, 239.74814519, 454.05828935])

        # Test the corners
        self.assertAlmostEqual(float(interp(xy, z, np.array([xy[0]]))[0]), float(z[0]))
        self.assertAlmostEqual(float(interp(xy, z, np.array([xy[1]]))[0]), float(z[1]))
        self.assertAlmostEqual(float(interp(xy, z, np.array([xy[2]]))), float(z[2]))
        self.assertAlmostEqual(float(interp(xy, z, np.array([xy[3]]))), float(z[3]))
