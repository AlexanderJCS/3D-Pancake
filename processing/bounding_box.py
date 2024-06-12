import open3d as o3d
import numpy as np

from .data import meta

from scipy.spatial.transform import Rotation


class Obb:
    def __init__(self, bool_data: np.ndarray, scale: meta.Scale):
        self.o3d_obb: o3d.geometry.OrientedBoundingBox = self._gen(bool_data, scale)
        self.vertices = np.array(self.o3d_obb.get_box_points())
        self.rotation = Rotation.from_matrix(np.array(self.o3d_obb.R))

        # set o3d_obb color to blue for visualization
        self.o3d_obb.color = (0, 0, 1)

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
