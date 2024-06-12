import open3d as o3d
import numpy as np

from . import data

from scipy.spatial.transform import Rotation


class Obb:
    def __init__(self, o3d_obb: o3d.geometry.OrientedBoundingBox):
        self.o3d_obb: o3d.geometry.OrientedBoundingBox = o3d_obb
        self.vertices = np.array(o3d_obb.get_box_points())
        self.rotation = Rotation.from_matrix(np.array(o3d_obb.R))

    def get_rotation_vec(self) -> np.ndarray:
        """
        :return: A normalized 3D vector representing the rotation of the OBB in 3D space
        """

        # The rotation matrix R is a 3x3 matrix, and each column represents the direction of one of the OBB's local axes
        # in the world frame. We can take the first column to get the direction of one of the faces of the OBB.
        rotation_vec = self.rotation.as_matrix()[:, 0]

        return rotation_vec / np.linalg.norm(rotation_vec)

    def contains(self, point: np.ndarray) -> bool:
        """
        Returns whether a point is inside the OBB

        :param point: The point to check
        :return: If it is inside the OBB
        """

        return len(self.o3d_obb.get_point_indices_within_bounding_box(o3d.utility.Vector3dVector([point]))) > 0

    @staticmethod
    def _min_axis_dist(obb_points: np.ndarray, point: np.ndarray, axis: int) -> float:
        """
        Finds the minimum distance on the axis for a point
        :param obb_points: The OBB points. Assumes the OBB is axis-aligned
        :param point: The point to check
        :param axis: The axis to check (int). e.g., x = 0, y = 1, z = 2
        :return: The minimum distance on the axis. 0 if the point is within the OBB for the axis
        """

        # If the point is greater than the minimum value and less than the maximum value, the distance is 0
        if obb_points[:, axis].min() <= point[axis] <= obb_points[:, axis].max():
            return 0

        # Otherwise, the distance is the minimum distance to the minimum or maximum value
        return min(
            abs(obb_points[:, axis].min() - point[axis]),
            abs(obb_points[:, axis].max() - point[axis])
        )

    def dist(self, point: np.ndarray) -> float:
        """
        Returns the distance from the point to the OBB

        :param point: The point to check
        :return: The distance from the point to the OBB
        """

        # Rotate both the point and the OBB so that the OBB is axis-aligned
        point_rotated = point @ self.rotation.as_matrix()
        obb_points_rotated = self.vertices @ self.rotation.as_matrix()

        x_min = self._min_axis_dist(obb_points_rotated, point_rotated, 0)
        y_min = self._min_axis_dist(obb_points_rotated, point_rotated, 1)
        z_min = self._min_axis_dist(obb_points_rotated, point_rotated, 2)

        return np.sqrt(x_min ** 2 + y_min ** 2 + z_min ** 2)

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


def flood_fill(z_layer: np.ndarray, x: int, y: int) -> np.ndarray:
    """
    Flood fills a blob onto a new image. Used for finding blobs.

    :param z_layer: The 2D numpy boolean array. This will be modified
    :param x: The x coordinate of the starting pixel
    :param y: The y coordinate of the starting pixel
    :return: The blob image with the blob filled in
    """

    blob = np.zeros(z_layer.shape, dtype=bool)

    stack = [(x, y)]

    while stack:
        x, y = stack.pop()

        if x < 0 or y < 0 or x >= z_layer.shape[1] or y >= z_layer.shape[0]:
            continue

        if z_layer[y, x]:
            z_layer[y, x] = False
            blob[y, x] = True

            stack.append((x + 1, y))
            stack.append((x - 1, y))
            stack.append((x, y + 1))
            stack.append((x, y - 1))

    return blob


def get_blobs(z_layer: np.ndarray) -> np.ndarray:
    """
    Finds all blobs (groups of adjacent white pixels) in the image and returns an array of images, each containing one
    blob.

    :param z_layer: The 2D numpy boolean array
    :return: The blobs
    """

    z_layer = z_layer.copy()

    blobs = []

    # Iterate through each pixel. If the pixel is white, flood fill it onto a new image as a separate blob. When flood
    # filling, make sure to update the original z_layer variable to black so that the blob is not counted again.
    for y, row in enumerate(z_layer):
        for x, col in enumerate(row):
            if not col:
                continue

            # Flood fill the blob
            blobs.append(flood_fill(z_layer, x, y))

    return np.array(blobs)


def gen_point_cloud(raw_data: np.ndarray, z_layer: float, scale: data.Scale) -> o3d.geometry.PointCloud:
    """
    Converts a 3D numpy boolean array into a point cloud. Used for finding the OBB.

    :param raw_data: The 2D numpy boolean array for the given layer
    :param scale: The scale of a voxel
    :param z_layer: The z layer to convert
    :return: A point cloud of the True values in the array
    """

    points = np.argwhere(raw_data).astype(float)[:, ::-1]
    points *= scale.xy

    # add a z layer for each point: the z layer of the voxel and the z layer of the voxel + z_scale
    points = np.array([
        [point[0], point[1], z_layer * scale.z] for point in points
    ])

    points_2 = np.array([
        [point[0], point[1], (z_layer + 1) * scale.z] for point in points
    ])

    points = np.concatenate((points, points_2), axis=0)

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)

    return pcd


def get_obbs(raw_data: np.ndarray, scale: data.Scale) -> tuple[Obb, list[Obb]]:
    """
    Finds the oriented bounding boxes of the data

    :param raw_data: The 3D numpy boolean array
    :param scale: The scale of a voxel
    :return: (the 'main' obb, an array of obbs for each blob in the data
    """

    pcds = []
    o3d_obbs = []

    points = []

    for layer_num, z_layer in enumerate(raw_data):
        z_layer: np.ndarray  # add this type hinting so pycharm doesn't complain about nothing

        blobs = get_blobs(z_layer)

        for blob in blobs:
            pcd = gen_point_cloud(blob, layer_num, scale)
            points.append(np.array(pcd.points))
            obb = o3d.geometry.OrientedBoundingBox().create_from_points(pcd.points)

            obb.color = np.array([1, 0, 0])  # red

            pcds.append(pcd)
            o3d_obbs.append(obb)

    points = np.concatenate(points, axis=0)

    main_o3d_obb = o3d.geometry.OrientedBoundingBox().create_from_points(
        o3d.utility.Vector3dVector(points)
    )

    main_o3d_obb.color = np.array([0, 0, 1])  # blue
    main_obb = Obb(main_o3d_obb)

    obbs: list[Obb] = []
    for obb in o3d_obbs:
        obbs.append(Obb(obb))

    return main_obb, obbs
