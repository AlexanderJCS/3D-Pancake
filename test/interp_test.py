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
        self.assertEqual(interp(vertices, values, np.array([[0, 1]])), -1)
        self.assertEqual(interp(vertices, values, np.array([[1, 0]])), -1)
