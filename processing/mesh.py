import itertools
from typing import Optional

from . import bounding_box
from . import data

import open3d as o3d
import numpy as np

from scipy import interpolate
from scipy import spatial


class Mesh:
    MAX_PREV_VERTICES = 10

    def __init__(self, obb: bounding_box.Obb, geom_center: np.ndarray, scale: data.Scale):
        self.bounding_box = obb
        self.mesh, self.min_extent_idx_rotated = self._gen(obb, geom_center, scale)
        self.prev_vertices = []

    @staticmethod
    def _gen(obb: bounding_box.Obb, geom_center: np.ndarray, scale: data.Scale):
        # Generate the quads for the mesh based off the smallest voxel size
        scale = data.Scale(min(scale.xy, scale.z), min(scale.xy, scale.z))

        # get some preliminary data
        rotation_matrix = obb.rotation.as_matrix()
        center = obb.o3d_obb.center
        vertices = obb.vertices

        # rotate mesh vertices to be aligned with the axes
        vertices -= center
        vertices = obb.vertices @ rotation_matrix
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
        min_extent_index = np.argmin(obb.o3d_obb.extent)
        starting_vertex[min_extent_index] = geom_center_rotated[min_extent_index]

        # opposite_vertex = starting_vertex + extent of all but the shortest axis
        opposite_extent = np.copy(obb.o3d_obb.extent)
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
        x, y, z = np.meshgrid(x_range, y_range, z_range, indexing="ij")
        vertices = np.stack((x, y, z), axis=-1).reshape(-1, 3)

        # -- Create mesh edges --
        # loop over the two axes that are variable
        loop_and_loop_next = [
            x_range.shape[0],
            y_range.shape[0],
            z_range.shape[0]
        ]

        loop_and_loop_next.pop(min_extent_index_rotated)
        loop, loop_next = loop_and_loop_next

        indices = []
        for i, j in itertools.product(range(loop - 1), range(loop_next - 1)):
            indices.extend((
                [
                    i * loop_next + j,
                    i * loop_next + j + 1,
                    (i + 1) * loop_next + j,
                ],
                [
                    i * loop_next + j + 1,
                    (i + 1) * loop_next + j + 1,
                    (i + 1) * loop_next + j,
                ],
            ))
        
        # -- Create the mesh --
        mesh = o3d.geometry.TriangleMesh()
        mesh.vertices = o3d.utility.Vector3dVector(vertices)
        mesh.triangles = o3d.utility.Vector3iVector(indices)

        # -- Linear Interpolation --
        plane_points = np.delete(plane_vertices, min_extent_index_rotated, axis=1)
        plane_values = plane_vertices[:, min_extent_index_rotated]

        interp = interpolate.LinearNDInterpolator(plane_points, plane_values)

        interp_values = interp(np.delete(vertices, min_extent_index_rotated, axis=1))
        vertices[:, min_extent_index_rotated] = interp_values
        mesh.vertices = o3d.utility.Vector3dVector(vertices)

        # -- Remove any vertices which has nan values at the min_extent_index_rotated index --
        remove_vertex_indices = np.isnan(vertices[:, min_extent_index_rotated]).nonzero()[0]
        mesh.remove_vertices_by_index(remove_vertex_indices)

        return mesh, min_extent_index_rotated

    def clip_vertices(self, dist_map: np.ndarray, scale: data.Scale, dist_threshold: Optional[float] = None) -> None:
        """
        Clips all vertices that are outside the boolean data by a certain distance threshold.

        :param dist_map: The distance map to clip the vertices by. Note that this should be the not-projected dist map.
        :param scale: The voxel spacing
        :param dist_threshold: The distance threshold to clip each vertex in the final step. If None, the threshold is
                                 equal to max(scale.xy, scale.z) / 2
        :return: None
        """

        dist_map_rgi = self._get_rgi(dist_map, scale)
        vertices = np.asarray(self.mesh.vertices)

        # Find the distances of each vertex
        distances = dist_map_rgi(vertices[:, ::-1])  # Reverse the order for z, y, x indexing

        if dist_threshold is None:
            dist_threshold = max(scale.xy, scale.z) / 2

        # less than negative distance threshold since outside values are negative in the dist map
        indices_to_remove = np.where(distances < -dist_threshold)[0]

        self.mesh.remove_vertices_by_index(indices_to_remove)

    @staticmethod
    def _get_rgi(gradient: np.array, scale: data.Scale) -> interpolate.RegularGridInterpolator:
        """
        Gets the regular grid interpolator for the gradient. Helper function for bend.
        
        :param gradient: The gradient to interpolate.
        :param scale: The voxel spacing.
        :return: The regular grid interpolator.
        """
        
        x = np.linspace(0, gradient.shape[2] * scale.xy, gradient.shape[2]) - scale.xy / 2
        y = np.linspace(0, gradient.shape[1] * scale.xy, gradient.shape[1]) - scale.xy / 2
        z = np.linspace(0, gradient.shape[0] * scale.z, gradient.shape[0]) - scale.z / 2

        return interpolate.RegularGridInterpolator(
            (z, y, x),
            gradient,
            bounds_error=False,
            fill_value=np.nan,
            method="linear"
        )

    def bend(self, projected_gradient: np.array, scale: data.Scale) -> None:
        """
        Bends the mesh so the vertices are set where the gradient converges.
        :param projected_gradient: The projected gradient
        :param scale: The voxel spacing
        """

        gradient_dir = self.bounding_box.get_normal()
        new_vertices = np.asarray(self.mesh.vertices)  # the vertices to update

        # get the dot products of all vectors in projected gradient with the gradient direction vector, returning a 1D
        # value for each vertex determining the direction of the gradient
        magnitudes = np.dot(projected_gradient, gradient_dir)
        rgi = self._get_rgi(magnitudes, scale)

        scene = o3d.t.geometry.RaycastingScene()
        scene.add_triangles(o3d.t.geometry.TriangleMesh().from_legacy(mesh_legacy=self.bounding_box.get_mesh()))

        # Duplicate each vertex for two rays (positive and negative gradient)
        ray_origins = np.repeat(new_vertices, 2, axis=0)
        ray_directions = np.tile([gradient_dir, -gradient_dir], (len(new_vertices), 1))

        # Combine origins and directions to form rays
        rays = np.hstack([ray_origins, ray_directions])
        rays = o3d.core.Tensor(rays, dtype=o3d.core.Dtype.Float32)

        # Perform batch raycasting
        hit_results = scene.cast_rays(rays)
        hit_distances = hit_results["t_hit"].numpy().reshape(-1, 2)

        # Filter out rays that didn't hit anything
        valid_hits = np.all(hit_distances != np.inf, axis=1)
        valid_vertices = new_vertices[valid_hits]
        valid_hit_distances = hit_distances[valid_hits]

        # Compute hit points
        hit_points_neg = valid_vertices - gradient_dir * valid_hit_distances[:, 1].reshape(-1, 1)
        hit_points_pos = valid_vertices + gradient_dir * valid_hit_distances[:, 0].reshape(-1, 1)

        # Binary search for zero gradient across all valid vertices
        # Initialize midpoints to hit_points_pos. Avoids the very unlikely case that the loop will not run, and an
        #  error will be thrown due to the uninitialized variable "midpoints"
        midpoints = hit_points_pos
        
        while np.linalg.norm(hit_points_neg - hit_points_pos, axis=1).max() > 0.05:  # 0.05 nm threshold
            midpoints = (hit_points_neg + hit_points_pos) / 2
            mid_values = rgi(midpoints[:, ::-1])  # Reverse the order for z, y, x indexing

            # Vectorized update for binary search
            mask = mid_values < 0
            hit_points_pos[mask] = midpoints[mask]
            hit_points_neg[~mask] = midpoints[~mask]

        # Update only the valid vertices
        new_vertices[valid_hits] = midpoints

    def area(self) -> float:
        """
        Gets the surface area of the mesh

        :return: The surface area of the mesh
        """

        return self.mesh.get_surface_area()
