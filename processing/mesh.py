from . import obb
from . import data

import open3d as o3d
import numpy as np

import matplotlib.pyplot as plt
from scipy import interpolate


class Mesh:
    def __init__(self, bounding_box: obb.Obb, geom_center: np.ndarray, scale: data.Scale):
        self.bounding_box = bounding_box
        self.mesh = self._gen(bounding_box, geom_center, scale)

    @staticmethod
    def _gen(bounding_box: obb.Obb, geom_center: np.ndarray, scale: data.Scale):
        # get some preliminary data
        rotation_matrix = bounding_box.rotation.as_matrix()
        center = bounding_box.o3d_obb.center
        vertices = bounding_box.vertices

        # rotate mesh vertices to be aligned with the axes
        vertices -= center
        vertices = bounding_box.vertices @ rotation_matrix
        vertices += center

        # rotate geom center to be aligned with the axes
        geom_center_rotated = geom_center - center
        geom_center_rotated = geom_center_rotated @ rotation_matrix
        geom_center_rotated += center

        # find the minimum vertex in all xyz directions
        min_vertex_index = np.argmin(np.sum(vertices, axis=1))
        min_vertex = vertices[min_vertex_index]

        # starting_vertex = min_vertex but the shortest extent axis is set to the value of the geom center at that axis
        starting_vertex = min_vertex
        min_extent_index = np.argmin(bounding_box.o3d_obb.extent)
        starting_vertex[min_extent_index] = geom_center_rotated[min_extent_index]

        # opposite_vertex = starting_vertex + extent of all but the shortest axis
        opposite_extent = np.copy(bounding_box.o3d_obb.extent)
        opposite_extent[min_extent_index] = 0
        opposite_vertex = starting_vertex + opposite_extent

        # remove the shortest extent axis from min_vertex and opposite_vertex
        starting_vertex_2d = np.delete(starting_vertex, min_extent_index)
        opposite_vertex_2d = np.delete(opposite_vertex, min_extent_index)

        # create the vertices in the plane
        plane_vertices_2d = np.array([
            starting_vertex_2d,
            opposite_vertex_2d,
            [opposite_vertex_2d[0], starting_vertex_2d[1]],
            [starting_vertex_2d[0], opposite_vertex_2d[1]]
        ])

        # add back the shortest extent axis
        plane_vertices = np.insert(plane_vertices_2d, min_extent_index, min_vertex[min_extent_index], axis=1)

        # Rotate the plane vertices back
        plane_vertices -= center
        plane_vertices = plane_vertices @ rotation_matrix.T
        plane_vertices += center

        # Linear interpolator for the plane, given the two longer extent axes find the shorter extent axis value
        # use scipy for interpolation
        interp = interpolate.LinearNDInterpolator(
            np.delete(vertices, min_extent_index, axis=1),
            vertices[:, min_extent_index]
        )


        # plot in 3d
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(vertices[:, 0], vertices[:, 1], vertices[:, 2])
        ax.scatter(plane_vertices[:, 0], plane_vertices[:, 1], plane_vertices[:, 2])
        ax.scatter(geom_center_rotated[0], geom_center_rotated[1], geom_center_rotated[2])
        plt.show()

        return None

    def deform(self, projected_gradient: np.ndarray, scale: data.Scale):
        for i, vertex in enumerate(self.mesh.vertices):
            vertex = np.array(vertex)

            # find the gradient at the vertex
            gradient = projected_gradient[int(vertex[2] / scale.z), int(vertex[1] / scale.xy), int(vertex[0] / scale.xy)]
            vertex += gradient

            self.mesh.vertices[i] = vertex
