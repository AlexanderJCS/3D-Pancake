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
        Pads the data so the OBB does not have values outside the dataset. In addition, it offsets the vertices
        of this OBB to adjust to the new, expanded dataset.

        :param scale: The scale of the data.
        :param data: The data to expand
        :return: (The expanded data, the xyz transformations). Also mutates the vertices of this OBB
        """

        # Get the min and max of the OBB
        min_obb_xyz = (
            np.min(self.vertices[:, 0]),
            np.min(self.vertices[:, 1]),
            np.min(self.vertices[:, 2])
        )

        max_obb_xyz = (
            np.max(self.vertices[:, 0]),
            np.max(self.vertices[:, 1]),
            np.max(self.vertices[:, 2])
        )

        # Get the min and max of the data
        min_data_xyz = (0, 0, 0)
        max_data_xyz = data.shape[::-1] * scale.xyz()

        # Find the minimum amount of padding needed to have the OBB inside the data
        min_padding = np.max([
            abs(max_data_xyz[0] - max_obb_xyz[0]),
            abs(max_data_xyz[1] - max_obb_xyz[1]),
            abs(max_data_xyz[2] - max_obb_xyz[2]),
            abs(min_data_xyz[0] - min_obb_xyz[0]),
            abs(min_data_xyz[1] - min_obb_xyz[1]),
            abs(min_data_xyz[2] - min_obb_xyz[2])
        ])

        # Pad the data
        padding_voxels = int(min_padding // scale.z) + 1
        padded_data = np.pad(data, padding_voxels, mode="constant")

        translation_arr = np.array([padding_voxels * scale.xy, padding_voxels * scale.xy, padding_voxels * scale.z],
                                   dtype=np.float64)

        self.o3d_obb.translate(translation_arr, relative=True)
        self.vertices = np.array(self.o3d_obb.get_box_points())

        return padded_data, translation_arr
