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
        self.rgi: Optional[interpolate.RegularGridInterpolator] = None

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

        # -- Create mesh vertices --
        # loop over the two axes that are variable
        loop_and_loop_next = [
            x_range.shape[0],
            y_range.shape[0],
            z_range.shape[0]
        ]

        loop_and_loop_next.pop(min_extent_index_rotated)
        loop, loop_next = loop_and_loop_next

        indices = []
        for i in range(loop - 1):
            for j in range(loop_next - 1):
                # make a quad
                indices.append([i * loop_next + j, i * loop_next + j + 1, (i + 1) * loop_next + j])
                indices.append([i * loop_next + j + 1, (i + 1) * loop_next + j + 1, (i + 1) * loop_next + j])

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

    def _append_prev_vertices(self, vertices: np.ndarray):
        self.prev_vertices.append(vertices.copy())

        # Remove elements of prev_vertices if it exceeds the maximum length
        while len(self.prev_vertices) > self.MAX_PREV_VERTICES:
            self.prev_vertices.pop(0)

    def gen_rgi(self, scale: data.Scale, projected_gradient: np.ndarray) -> None:
        """
        Generates a regular grid interpolator and saves it as a class variable. Instead of just generating it each
        iteration, this function is used to generate it once and save it for later use. This results in a 1% performance
        increase on average for the entire runtime of the program.

        :param scale: The scale of the data
        :param projected_gradient: The gradient data
        """

        # Create x y z points for the regular grid interpolator
        x = np.linspace(0, projected_gradient.shape[2] * scale.xy, projected_gradient.shape[2]) - scale.xy / 2
        y = np.linspace(0, projected_gradient.shape[1] * scale.xy, projected_gradient.shape[1]) - scale.xy / 2
        z = np.linspace(0, projected_gradient.shape[0] * scale.z, projected_gradient.shape[0]) - scale.z / 2

        # Interpolate the gradient values
        self.rgi = interpolate.RegularGridInterpolator(
            (z, y, x),
            projected_gradient,
            bounds_error=False,
            fill_value=np.nan,
            method="linear"
        )

    def deform(self, projected_gradient: np.ndarray, scale: data.Scale):
        if self.min_extent_idx_rotated in (0, 2):
            # no idea why I need to do this, but it works
            projected_gradient = projected_gradient[:, :, :, ::-1]  # flip the gradient vector

        vertices = np.asarray(self.mesh.vertices)

        self._append_prev_vertices(vertices)

        if self.rgi is None:
            self.gen_rgi(scale, projected_gradient)

        vertices = vertices[:, ::-1]  # rearrange vertices to zyx format since that's what the interpolator wants
        gradients = self.rgi(vertices)

        # Create a mask to not do math on NaN values to avoid errors
        # Ideally there should be no NaN values but just in case
        nan_mask = np.isnan(gradients).any(axis=1)
        vertices[~nan_mask] += gradients[~nan_mask] * 5
        self.mesh.vertices = o3d.utility.Vector3dVector(vertices[:, ::-1])

    def error(self) -> float:
        """
        Returns the euclidian error based off of the mesh's position and the previous positions. Lower means the mesh is
        closer to its final form. Used when deforming the mesh.

        :return: The euclidian error
        """

        if len(self.prev_vertices) < self.MAX_PREV_VERTICES:
            return np.inf

        # e = sigma(i = 1, k) ((p_i a - p_i b)) / k
        # aka, mean euclidian distance shifted per vertex
        sum_error = 0

        vertices = np.asarray(self.mesh.vertices)
        for prev_vertices_item in self.prev_vertices:
            sum_error += np.mean(np.linalg.norm(vertices - prev_vertices_item, axis=1))

        mean_error = sum_error / self.MAX_PREV_VERTICES

        return mean_error

    def clip_vertices(self, bool_data: np.ndarray, scale: data.Scale, dist_threshold: Optional[float] = None) -> None:
        """
        Clips all vertices that are outside the boolean data by a certain distance threshold.

        :param bool_data: The boolean data to clip the vertices to
        :param scale: The voxel spacing
        :param dist_threshold: The distance threshold to clip each vertex in the final step. If None, the threshold is
                                 equal to max(scale.xy, scale.z) / 1.5
        :return: None
        """

        points = np.argwhere(bool_data)[:, ::-1] * scale.xyz()
        vertices = np.asarray(self.mesh.vertices)

        # Create a KDTree from points
        tree = spatial.cKDTree(points)

        # Query the KDTree to find the distance to the nearest point in points for each vertex
        distances, _ = tree.query(vertices, k=1)

        # Find vertices that need to be removed
        if dist_threshold is None:
            dist_threshold = max(scale.xy, scale.z) / 1.5

        indices_to_remove = np.where(distances > dist_threshold)[0]

        self.mesh.remove_vertices_by_index(indices_to_remove)

    def bend(self, projected_gradient: np.array, scale: data.Scale) -> None:
        """
        Bends the mesh so the vertices are set where the gradient converges.
        :param projected_gradient: The projected gradient
        :param scale: The voxel spacing
        """

        gradient_dir = self.bounding_box.get_normal()
        new_vertices = np.asarray(self.mesh.vertices)

        # get the dot products of all vectors in projected gradient with the gradient direction vector, returning a 1D
        # value for each vertex determining the direction of the gradient
        magnitudes = np.dot(projected_gradient, gradient_dir)

        x = np.linspace(0, projected_gradient.shape[2] * scale.xy, projected_gradient.shape[2]) - scale.xy / 2
        y = np.linspace(0, projected_gradient.shape[1] * scale.xy, projected_gradient.shape[1]) - scale.xy / 2
        z = np.linspace(0, projected_gradient.shape[0] * scale.z, projected_gradient.shape[0]) - scale.z / 2

        rgi = interpolate.RegularGridInterpolator(
            (z, y, x),
            magnitudes,
            bounds_error=False,
            fill_value=np.nan,
            method="linear"
        )

        scene = o3d.t.geometry.RaycastingScene()
        scene.add_triangles(o3d.t.geometry.TriangleMesh.from_legacy(self.bounding_box.get_mesh()))

        for i, vertex in enumerate(new_vertices):
            """
            Below is a dumb approach but it works for the proof of concept
            
            1. Identify the point projected on the gradient direction vector, putting it in that coordinate system
            2. Traverse all x values in the new coordinate system, until it flips direction or reaches the edge
            3. Set the vertex to the x value where the gradient direction flips/whose absolute value is minimum
            """

            if i % 100 == 0:
                print(f"{i}/{len(new_vertices)}")

            # cast rays in the direction of the gradient, and negative gradient
            rays = o3d.core.Tensor([[*vertex, *gradient_dir], [*vertex, *(-gradient_dir)]], dtype=o3d.core.Dtype.Float32)
            hit_distances = scene.cast_rays(rays)["t_hit"]

            if np.inf in hit_distances:
                print("uh oh")
                continue  # uh oh, ray didn't hit anything which should be impossible

            hit_point_1 = vertex + gradient_dir * hit_distances[0].numpy()
            hit_point_2 = vertex - gradient_dir * hit_distances[1].numpy()

            # conduct binary search on the gradient, searching for 0
            while np.linalg.norm(hit_point_1 - hit_point_2) > 0.05:
                mid = (hit_point_1 + hit_point_2) / 2
                mid_val = rgi(mid[::-1])

                if mid_val < 0:
                    hit_point_1 = mid
                else:
                    hit_point_2 = mid

            new_vertices[i] = mid

    def area(self) -> float:
        """
        Gets the surface area of the mesh

        :return: The surface area of the mesh
        """

        return self.mesh.get_surface_area()
