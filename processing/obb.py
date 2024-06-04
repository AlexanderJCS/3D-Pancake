import open3d as o3d
import numpy as np


class Obb:
    def __init__(self, o3d_obb: o3d.geometry.OrientedBoundingBox):
        self.o3d_obb: o3d.geometry.OrientedBoundingBox = o3d_obb


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


def gen_point_cloud(data: np.ndarray, xy_scale: float, z_layer: float, z_scale: float) -> o3d.geometry.PointCloud:
    """
    Converts a 3D numpy boolean array into a point cloud. Used for finding the OBB.

    :param data: The 2D numpy boolean array for the given layer
    :param xy_scale: The distance of a voxel in the x or y direction
    :param z_layer: The z layer to convert
    :param z_scale: The distance of a voxel in the z direction
    :return: A point cloud of the True values in the array
    """

    points = np.argwhere(data)
    points *= xy_scale

    # convert each point into 4 points representing the corners of the voxel
    points = np.array([
        [point[0], point[1], z_layer] for point in points
    ])

    # add a z layer for each point: the z layer of the voxel and the z layer of the voxel + z_scale
    points = np.array([
        [point[0], point[1], z_layer] for point in points
    ])

    points_2 = np.array([
        [point[0], point[1], z_layer + z_scale] for point in points
    ])

    points = np.concatenate((points, points_2), axis=0)

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)

    return pcd


def get_obbs(data: np.ndarray, xy_scale: float, z_scale: float, visualize: bool = False) -> list[Obb]:
    """
    Finds the oriented bounding boxes of the data

    :param data: The 3D numpy boolean array
    :param xy_scale: The distance of a voxel in the x or y direction
    :param z_scale: The distance of a voxel in the z direction
    :param visualize: Whether to visualize the OBBs. Will open a new window
    :return: An Obb object
    """

    pcds = []
    o3d_obbs = []

    for layer_num, z_layer in enumerate(data):
        z_layer: np.ndarray  # add this type hinting so pycharm doesn't complain about nothing

        blobs = get_blobs(z_layer)

        for blob in blobs:
            pcd = gen_point_cloud(blob, xy_scale, layer_num, z_scale)
            obb = o3d.geometry.OrientedBoundingBox().create_from_points(pcd.points)

            obb.color = np.array([1, 0, 0])  # make obb red instead of white for better visualization

            pcds.append(pcd)
            o3d_obbs.append(obb)

    if visualize:
        o3d.visualization.draw_geometries([*pcds, *o3d_obbs])

    obbs: list[Obb] = []
    for obb in o3d_obbs:
        obbs.append(Obb(obb))

    return obbs