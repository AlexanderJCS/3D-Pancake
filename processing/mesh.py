import time

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

        # -- Extent Rotated --
        extent_rotated = np.array([
            np.max(plane_vertices[:, 0]) - np.min(plane_vertices[:, 0]),
            np.max(plane_vertices[:, 1]) - np.min(plane_vertices[:, 1]),
            np.max(plane_vertices[:, 2]) - np.min(plane_vertices[:, 2])
        ])

        min_extent_index_rotated = np.argmin(extent_rotated)

        # -- Create the vertices --
        # go from min_x to max_x, min_y to max_y, min_z to max_z
        x_range = np.arange(np.min(plane_vertices[:, 0]), np.max(plane_vertices[:, 0]) + scale.xy, scale.xy)
        y_range = np.arange(np.min(plane_vertices[:, 1]), np.max(plane_vertices[:, 1]) + scale.xy, scale.xy)
        z_range = np.arange(np.min(plane_vertices[:, 2]), np.max(plane_vertices[:, 2]) + scale.z, scale.z)

        x_range = x_range if min_extent_index_rotated != 0 else np.array([0])
        y_range = y_range if min_extent_index_rotated != 1 else np.array([0])
        z_range = z_range if min_extent_index_rotated != 2 else np.array([0])

        # Create the [[x, y, z], ...] array
        x, y, z = np.meshgrid(x_range, y_range, z_range, indexing='ij')
        vertices = np.stack((x, y, z), axis=-1).reshape(-1, 3)

        # Create vertex indices for a mesh
        # since the x coordinate would be increasing each time (unless x = 0, then we do y)
        # then we can find how many times it would loop over
        loop = x_range.shape[0] if min_extent_index_rotated != 0 else y_range.shape[0]

        # this is the one after loop, so if loop is x, then this is y, if loop is y, this is z
        loop_next = y_range.shape[0] if min_extent_index_rotated != 1 else z_range.shape[0]

        # calculate the mesh indices
        indices = []
        for i in range(loop - 1):
            for j in range(loop_next - 1):
                indices.append([i * loop_next + j, i * loop_next + j + 1, (i + 1) * loop_next + j])
                indices.append([i * loop_next + j + 1, (i + 1) * loop_next + j + 1, (i + 1) * loop_next + j])

        # Create the mesh
        mesh = o3d.geometry.TriangleMesh()
        mesh.vertices = o3d.utility.Vector3dVector(vertices)
        mesh.triangles = o3d.utility.Vector3iVector(indices)

        # -- Linear Interpolation --
        plane_points = np.delete(plane_vertices, min_extent_index_rotated, axis=1)
        plane_values = plane_vertices[:, min_extent_index_rotated]

        interpolator = interpolate.LinearNDInterpolator(plane_points, plane_values)

        interp_values = interpolator(np.delete(vertices, min_extent_index_rotated, axis=1))
        vertices[:, min_extent_index_rotated] = interp_values
        mesh.vertices = o3d.utility.Vector3dVector(vertices)

        # -- Remove any vertices which has nan values at the min_extent_index_rotated index --
        remove_vertex_indices = np.isnan(vertices[:, min_extent_index_rotated]).nonzero()[0]
        mesh.remove_vertices_by_index(remove_vertex_indices)

        return mesh
    
    def deform(self, projected_gradient: np.ndarray, scale: data.Scale):
        for i, vertex in enumerate(self.mesh.vertices):
            vertex = np.array(vertex)
            
            # TODO: this assumes the x, y, and z scales are the same when interpolating. This is not always the case
            vertex_index_float = np.array([vertex[2] / scale.z, vertex[1] / scale.xy, vertex[0] / scale.xy])
            vertex_index_int = vertex_index_float.astype(int)
            
            # create all 8 surrounding vertices
            surrounding_vertices = np.array([
                [vertex_index_int[0], vertex_index_int[1], vertex_index_int[2]],
                [vertex_index_int[0] + 1, vertex_index_int[1], vertex_index_int[2]],
                [vertex_index_int[0], vertex_index_int[1] + 1, vertex_index_int[2]],
                [vertex_index_int[0], vertex_index_int[1], vertex_index_int[2] + 1],
                [vertex_index_int[0] + 1, vertex_index_int[1] + 1, vertex_index_int[2]],
                [vertex_index_int[0] + 1, vertex_index_int[1], vertex_index_int[2] + 1],
                [vertex_index_int[0], vertex_index_int[1] + 1, vertex_index_int[2] + 1],
                [vertex_index_int[0] + 1, vertex_index_int[1] + 1, vertex_index_int[2] + 1]
            ])
            
            # get the gradient values at the point
            surrounding_gradients = np.array([
                projected_gradient[v[0], v[1], v[2]]
                for v in surrounding_vertices
            ])
            
            # create linear interpolation function
            gradient = interpolate.griddata(
                surrounding_vertices, surrounding_gradients, vertex_index_float, method="linear"
            )[0]
            
            # check if there are any nan values in the gradient
            if np.isnan(gradient).any():
                print("warning: nan values in gradient, skipping vertex")
                continue
            
            vertex += gradient * 10
            
            self.mesh.vertices[i] = vertex
