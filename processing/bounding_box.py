import open3d as o3d
import numpy as np

from .data import meta

from scipy.spatial.transform import Rotation


class Obb:
    def __init__(self, bool_data: np.ndarray, scale: meta.Scale):
        self.o3d_obb: o3d.geometry.OrientedBoundingBox = self._gen(bool_data, scale)
        self.vertices = np.array(self.o3d_obb.get_box_points())
        self.rotation = Rotation.from_matrix(np.array(self.o3d_obb.R))

    @staticmethod
    def _gen(bool_data: np.ndarray, scale: meta.Scale) -> o3d.geometry.OrientedBoundingBox:
        """
        Generates the OBB from the data.

        :param bool_data: The 3D boolean data to generate the OBB from
        :param scale: The scale of the data
        :return: The OBB
        """

        points = np.argwhere(bool_data)[:, ::-1] * scale.xyz()

        # duplicate points 1 z-layer down to make sure the last voxel is fully included in the OBB
        points = np.vstack((points, points - [0, 0, scale.z]))

        pcd = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(points))
        return pcd.get_oriented_bounding_box()

    def get_mesh(self) -> o3d.geometry.TriangleMesh:
        """
        :return: The mesh of the OBB
        """

        mesh_box = o3d.geometry.TriangleMesh.create_box(width=1.0, height=1.0, depth=1.0)
        mesh_box.translate([-0.5, -0.5, -0.5])  # Center the box at the origin

        # Create a scaling transformation matrix to scale the box to the size of the OBB
        scaling_matrix = np.diag([*self.o3d_obb.extent, 1])
        mesh_box.transform(scaling_matrix)

        # Rotate and translate the box to match the OBB
        mesh_box.rotate(self.o3d_obb.R, center=(0, 0, 0))
        mesh_box.translate(self.o3d_obb.center)

        return mesh_box

    def get_rotation_vec(self) -> np.ndarray:
        """
        :return: A normalized 3D vector representing the rotation of the OBB in 3D space
        """

        # The rotation matrix R is a 3x3 matrix, and each column represents the direction of one of the OBB's local axes
        # in the world frame. We can take the first column to get the direction of one of the faces of the OBB.
        rotation_vec = self.rotation.as_matrix()[:, 0]

        return rotation_vec / np.linalg.norm(rotation_vec)

    def get_normal(self) -> np.ndarray:
        """
        :return: The normal vector of the OBB
        """

        # Since we are working with three dimensions, it's best if we pick a vertex then give the normal direction
        # as the vector from the original vertex to the closest vertex

        v1 = self.vertices[0]
        v2 = None
        dist = np.inf

        for vertex in self.vertices[1:]:
            if np.linalg.norm(vertex - v1) < dist:
                v2 = vertex
                dist = np.linalg.norm(vertex - v1)

        normal = v2 - v1
        return normal / np.linalg.norm(normal)

    def expand_data(self, scale: meta.Scale, data: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """
        Pads the data so the OBB does not have values outside the dataset. In addition, it mutates the vertices
        of this OBB to adjust to the new padded dataset.

        The second return value, the OBB transformations, is used to translate the final mesh back to the original
        world position to visualize it in Dragonfly.

        :param scale: The scale of the data.
        :param data: The data to expand
        :return: (The expanded data, the OBB transformations). Also mutates the vertices of this OBB
        """

        # This method uses the following logic:
        #  1. Identify the minimum amount (in world coordinates) needed to pad the data in each axis direction such that
        #      the OBB is fully contained
        #  2. Convert this amount to voxel coordinates
        #  3. Pad the data
        #  4. Translate the OBB to contain the padded data

        # Get the min and max of the OBB's vertices' AABB
        min_obb_xyz = np.min(self.vertices, axis=0)
        max_obb_xyz = np.max(self.vertices, axis=0)

        # Get the min and max of the data
        min_data_xyz = (0, 0, 0)
        max_data_xyz = data.shape[::-1] * scale.xyz()

        padding_world_coords = np.array([
            [max(-(min_obb_xyz[0] - min_data_xyz[0]), 0), max(max_obb_xyz[0] - max_data_xyz[0], 0)],
            [max(-(min_obb_xyz[1] - min_data_xyz[1]), 0), max(max_obb_xyz[1] - max_data_xyz[1], 0)],
            [max(-(min_obb_xyz[2] - min_data_xyz[2]), 0), max(max_obb_xyz[2] - max_data_xyz[2], 0)]
        ])

        # Convert to voxel coords
        padding_voxels = (padding_world_coords / scale.xyz().reshape(-1, 1)).astype(int)
        padding_voxels += 1  # Add 1 to make sure everything is fully included after casting to int

        # Pad the data
        padded_data = np.pad(data, padding_voxels[::-1], mode="constant")

        # Translate the OBB to contain the padded data
        translation_arr = (padding_voxels[:, 0] * scale.xyz()).astype(np.float64)
        self.o3d_obb.translate(translation_arr, relative=True)
        self.vertices = np.array(self.o3d_obb.get_box_points())

        return padded_data, translation_arr
