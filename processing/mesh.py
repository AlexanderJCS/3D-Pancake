from . import obb
from . import data

import open3d as o3d
import numpy as np

import matplotlib.pyplot as plt

class Mesh:
    def __init__(self, bounding_box: obb.Obb, geom_center: np.ndarray, scale: data.Scale):
        self.bounding_box = bounding_box
        self.mesh = self._gen(bounding_box, geom_center, scale)

    @staticmethod
    def _gen(bounding_box: obb.Obb, geom_center: np.ndarray, scale: data.Scale):
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
        x_coords = np.arange(starting_vertex[0], starting_vertex[0] + bounding_box.o3d_obb.extent[0], scale.xy) if min_extent_index != 0 else np.array([starting_vertex[0]])
        y_coords = np.arange(starting_vertex[1], starting_vertex[1] + bounding_box.o3d_obb.extent[1], scale.xy) if min_extent_index != 1 else np.array([starting_vertex[1]])
        z_coords = np.arange(starting_vertex[2], starting_vertex[2] + bounding_box.o3d_obb.extent[2], scale.z) if min_extent_index != 2 else np.array([starting_vertex[2]])

        # create an array of xyz coordinates
        coords = np.array([[x, y, z] for x in x_coords for y in y_coords for z in z_coords])
        print(coords)

        # plot
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(*coords.T)
        ax.scatter(*geom_center_rotated)
        ax.scatter(*vertices.T)

        plt.show()
