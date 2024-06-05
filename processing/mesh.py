from . import obb

import open3d as o3d
import numpy as np


class Mesh:
    def __init__(self, bounding_box: obb.Obb, geom_center: np.ndarray):
        self.bounding_box = bounding_box
        self.mesh = self._gen(bounding_box)

    @staticmethod
    def _gen(bounding_box: obb.Obb):
        pass
