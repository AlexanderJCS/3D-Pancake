from ORSModel import ors

from skimage import measure

from .processing import data
import numpy as np
import open3d as o3d


def surface_area_lewiner_2012(roi_data: np.ndarray, scale: data.Scale):
    """
    Calculates the surface area of an ROI using the Lewiner 2012 Marching Cubes algorithm, a continuation of the
    Lindblad 1987 algorithm, while removing topological inconsistencies.

    :param roi_data: The ROI data
    :param scale: The voxel scale
    :return: The estimated surface area of the PSD in microns^2. Computed by finding the surface area of the mesh and
                dividing by 2.
    """

    vertices, faces, normals, values = measure.marching_cubes(roi_data, spacing=scale.zyx())

    mesh = o3d.geometry.TriangleMesh()
    mesh.vertices = o3d.utility.Vector3dVector(vertices)
    mesh.triangles = o3d.utility.Vector3iVector(faces)

    return mesh.get_surface_area() / 1e6 / 2


def surface_area_lindblad_2005(roi: ors.ROI):
    """
    Calculates the surface area of an ROI using the Lindblad 2005 algorithm.

    :param roi: The ROI
    :return: The estimated surface area of the PSD in microns^2.
    """

    # multiply by 1e12 to convert from m^2 to microns^2
    return roi.getSurfaceFromWeightedVoxelEstimation(0, None) * 1e12 / 2
