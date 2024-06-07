from . import obb
from . import data

import open3d as o3d
import numpy as np

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

        # rotate the vertices back
        plane_vertices -= center
        plane_vertices = plane_vertices @ rotation_matrix.T
        plane_vertices += center

        # -- Linear Interpolator --
        # Linear interpolator for the plane, given the two longer extent axes find the shorter extent axis value
        # use scipy for interpolation
        plane_points = np.delete(plane_vertices, min_extent_index, axis=1)
        plane_values = plane_vertices[:, min_extent_index]

        interp = interpolate.LinearNDInterpolator(
            np.delete(plane_vertices, min_extent_index, axis=1),
            plane_vertices[:, min_extent_index]
        )

        # -- Create the vertices --
        # go from min_x to max_x, min_y to max_y, min_z to max_z
        x_range = np.arange(np.min(plane_vertices[:, 0]), np.max(plane_vertices[:, 0]) + scale.xy, scale.xy)
        y_range = np.arange(np.min(plane_vertices[:, 1]), np.max(plane_vertices[:, 1]) + scale.xy, scale.xy)
        z_range = np.arange(np.min(plane_vertices[:, 2]), np.max(plane_vertices[:, 2]) + scale.z, scale.z)

        # create the vertices
        extent_rotated = np.array([
            x_range.max() - x_range.min(),
            y_range.max() - y_range.min(),
            z_range.max() - z_range.min()
        ])

        min_extent_index_rotated = np.argmin(extent_rotated)

        x_range = x_range if min_extent_index_rotated != 0 else np.array([0])
        y_range = y_range if min_extent_index_rotated != 1 else np.array([0])
        z_range = z_range if min_extent_index_rotated != 2 else np.array([0])

        # Create the [[x, y, z], ...] array
        x, y, z = np.meshgrid(x_range, y_range, z_range, indexing='ij')
        vertices = np.stack((x, y, z), axis=-1).reshape(-1, 3)

        # Interpolate the min_extent_index_rotated axis
        interp_values = interp(np.delete(vertices, min_extent_index_rotated, axis=1))
        vertices[:, min_extent_index_rotated] = interp_values

        print("plotting")
        pcd = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(vertices))
        pcd.paint_uniform_color([0.5, 0.5, 0.5])
        o3d.visualization.draw_geometries([pcd, bounding_box.o3d_obb])

        return None

    def deform(self, projected_gradient: np.ndarray, scale: data.Scale):
        for i, vertex in enumerate(self.mesh.vertices):
            vertex = np.array(vertex)

            # find the gradient at the vertex
            gradient = projected_gradient[
                int(vertex[2] / scale.z), int(vertex[1] / scale.xy), int(vertex[0] / scale.xy)]
            vertex += gradient

            self.mesh.vertices[i] = vertex
