from . import obb
from . import data

import open3d as o3d
import numpy as np

import matplotlib.pyplot as plt

class Mesh:
    def __init__(self, bounding_box: obb.Obb, geom_center: np.ndarray, scale: data.Scale):
        self.bounding_box = bounding_box
        self.mesh = self._gen(bounding_box, geom_center)

    @staticmethod
    def _gen(bounding_box: obb.Obb, geom_center: np.ndarray):
        rotation_matrix = bounding_box.rotation.as_matrix()
        center = bounding_box.o3d_obb.center
        vertices = bounding_box.vertices

        vertices -= center
        vertices = bounding_box.vertices @ rotation_matrix
        vertices += center

        geom_center_rotated = geom_center - center
        geom_center_rotated = geom_center_rotated @ rotation_matrix
        geom_center_rotated += center

        print(center)

        print(bounding_box.o3d_obb.extent)

        # find the minimum vertex in all xyz directions
        min_vertex_index = np.argmin(np.sum(vertices, axis=1))
        min_vertex = vertices[min_vertex_index]

        # starting_vertex = min_vertex but the shortest extent axis is set to the value of the geom center at that axis
        starting_vertex = np.copy(min_vertex)
        min_extent_index = np.argmin(bounding_box.o3d_obb.extent)
        starting_vertex[min_extent_index] = geom_center_rotated[min_extent_index]

        # create other vertices in the plane

