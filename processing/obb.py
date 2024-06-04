import open3d as o3d
import numpy as np


class Obb:
    def __init__(self, data: np.array):
        pass


def get_xyz(data: np.ndarray, xy_scale: float, z_scale: float) -> np.ndarray:
    """
    Converts a 3D numpy boolean array into an array of 3D coordinates

    :param data: The 3D numpy boolean array
    :param xy_scale: The distance of a voxel in the x or y direction
    :param z_scale: The distance of a voxel in the z direction
    :return: An array of 3D coordinates of the True values in the array
    """

    # Get the indices of the True values in the array
    points = np.argwhere(data)

    points[:, :2] *= xy_scale  # Scale the x and y coordinates
    points[:, 2] *= z_scale  # Scale the z coordinates

    return points


def gen_point_cloud(data: np.ndarray, xy_scale: float, z_scale: float) -> o3d.geometry.PointCloud:
    """
    Converts a 3D numpy boolean array into a point cloud. Used for finding the OBB.

    TODO: when individual layers will be passed, instead of putting the center of the voxel, put the four corners

    :param data: The 3D numpy boolean array
    :param xy_scale: The distance of a voxel in the x or y direction
    :param z_scale: The distance of a voxel in the z direction
    :return: A point cloud of the True values in the array
    """

    points = get_xyz(data, xy_scale, z_scale)

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)

    return pcd


def gen_voxels(data: np.ndarray, xy_scale: float, z_scale: float) -> o3d.geometry.VoxelGrid:
    """
    Converts a 3D numpy boolean array into a voxel grid. Used for finding the OBB.

    :param data: The 3D numpy boolean array
    :param xy_scale: The distance of a voxel in the x or y direction
    :param z_scale: The distance of a voxel in the z direction
    :return: A voxel grid of the True values in the array
    """

    pcd = gen_point_cloud(data, xy_scale, z_scale)

    voxel_grid = o3d.geometry.VoxelGrid().create_from_point_cloud(pcd, voxel_size=xy_scale)

    return voxel_grid


def get_obbs(data: np.ndarray, xy_scale: float, z_scale: float) -> Obb:
    """
    Finds the oriented bounding boxes of the data

    :param data: The 3D numpy boolean array
    :param xy_scale: The distance of a voxel in the x or y direction
    :param z_scale: The distance of a voxel in the z direction
    :return: An Obb object
    """

    pcd = gen_point_cloud(data, xy_scale, z_scale)
    obb = o3d.geometry.OrientedBoundingBox().create_from_points(pcd.points)

    obb.color = np.array([1, 0, 0])  # red

    o3d.visualization.draw_geometries([pcd, obb])

    return Obb(obb)
