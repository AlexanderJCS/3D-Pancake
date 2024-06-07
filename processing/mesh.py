from . import obb
from . import data

import open3d as o3d
import numpy as np

import matplotlib.pyplot as plt
from scipy import interpolate


class Mesh:
    def __init__(self, bounding_box: obb.Obb, geom_center: np.ndarray, scale: data.Scale, raw_data):
        self.bounding_box = bounding_box
        self.mesh = self._gen(bounding_box, geom_center, scale, raw_data)

    @staticmethod
    def _gen(bounding_box: obb.Obb, geom_center: np.ndarray, scale: data.Scale, raw_data):
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
        plane_points = np.delete(plane_vertices, min_extent_index, axis=1)
        plane_values = plane_vertices[:, min_extent_index]

        interp = interpolate.LinearNDInterpolator(
            np.delete(plane_vertices, min_extent_index, axis=1),
            plane_vertices[:, min_extent_index]
        )

        print("creating vertices")
        # go from min_x to max_x, min_y to max_y, min_z to max_z
        x_range = np.arange(np.min(plane_vertices[:, 0]), np.max(plane_vertices[:, 0]) + scale.xy, scale.xy) \
            # if min_vertex_index != 0 else 0
        y_range = np.arange(np.min(plane_vertices[:, 1]), np.max(plane_vertices[:, 1]) + scale.xy, scale.xy) \
            # if min_vertex_index != 1 else 0
        z_range = np.arange(np.min(plane_vertices[:, 2]), np.max(plane_vertices[:, 2]) + scale.z, scale.z) \
            # if min_vertex_index != 2 else 0

        extent_rotated = np.array([x_range.max() - x_range.min(), y_range.max() - y_range.min(), z_range.max() - z_range.min()])
        min_extent_index_rotated = np.argmin(extent_rotated)

        print("filling")
        # fill the zero range with the interpolated values
        if isinstance(x_range, int):
            x_range = y_range.copy()
            y_range = np.zeros(x_range.shape[0])
        if isinstance(y_range, int):
            xz = np.array([[[x, z] for z in z_range] for x in x_range])
            y_range = interp(xz)
        if isinstance(z_range, int):
            xy = np.array([[[x, y] for y in y_range] for x in x_range])
            z_range = interp(xy)

        print(x_range)
        # create the vertices
        print(x_range.max() - x_range.min(), y_range.max() - y_range.min(), z_range.max() - z_range.min())

        x_range = x_range if min_extent_index_rotated != 0 else np.array([0])
        y_range = y_range if min_extent_index_rotated != 1 else np.array([0])
        z_range = z_range if min_extent_index_rotated != 2 else np.array([0])

        x, y, z = np.meshgrid(x_range, y_range, z_range, indexing='ij')

        vertices = np.stack((x, y, z), axis=-1).reshape(-1, 3)
        print(vertices.shape)

        vertices[:, 1] = 0

        print("plotting")
        pcd = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(vertices))
        pcd.paint_uniform_color([0.5, 0.5, 0.5])
        data_pcd = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(np.argwhere(raw_data)[:, ::-1] * scale.xyz()))
        o3d.visualization.draw_geometries([pcd, bounding_box.o3d_obb])

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
            gradient = projected_gradient[
                int(vertex[2] / scale.z), int(vertex[1] / scale.xy), int(vertex[0] / scale.xy)]
            vertex += gradient

            self.mesh.vertices[i] = vertex
