from . import obb

import open3d as o3d
import numpy as np

import matplotlib.pyplot as plt


class Mesh:
    def __init__(self, bounding_box: obb.Obb, geom_center: np.ndarray):
        self.bounding_box = bounding_box
        self.mesh = self._gen(bounding_box)

    @staticmethod
    def _gen(bounding_box: obb.Obb):
        rotation_matrix = bounding_box.rotation.as_matrix()
        center = bounding_box.o3d_obb.center
        vertices = bounding_box.vertices

        print(center)

        vertices -= center
        vertices = bounding_box.vertices @ rotation_matrix
        vertices += center

        print(center)

        print(bounding_box.o3d_obb.extent)

        # plot
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        ax.scatter(vertices[:, 0], vertices[:, 1], vertices[:, 2])
        plt.show()
