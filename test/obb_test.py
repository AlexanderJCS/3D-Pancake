import unittest

import numpy as np
from processing import obb


class TestObb(unittest.TestCase):
    def test_blobs(self):
        z_layer = np.array(
            [
                [1, 1, 0, 0, 0],
                [1, 1, 1, 0, 0],
                [0, 0, 0, 1, 1],
                [0, 0, 0, 1, 1],
            ]
        )

        blob_1 = np.array(
            [
                [1, 1, 0, 0, 0],
                [1, 1, 1, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0]
            ]
        )

        blob_2 = np.array(
            [
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 1, 1],
                [0, 0, 0, 1, 1]
            ]
        )

        blobs = obb.get_blobs(z_layer)

        self.assertEqual(len(blobs), 2)
        self.assertTrue(np.array_equal(blobs[0], blob_1) or np.array_equal(blobs[1], blob_1))
        self.assertTrue(np.array_equal(blobs[0], blob_2) or np.array_equal(blobs[1], blob_2))


if __name__ == "__main__":
    unittest.main()
