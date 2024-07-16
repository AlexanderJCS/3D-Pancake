import os
import sys
import pandas as pd
import numpy as np
from descartes import PolygonPatch
import matplotlib.pyplot as plt
import alphashape
import open3d as o3d
from processing.data import meta


# points_3d = [
#     (0., 0., 0.), (0., 0., 1.), (0., 1., 0.),
#     (1., 0., 0.), (1., 1., 0.), (1., 0., 1.),
#     (0., 1., 1.), (1., 1., 1.), (.25, .5, .5),
#     (.5, .25, .5), (.5, .5, .25), (.75, .5, .5),
#     (.5, .75, .5), (.5, .5, .75)
# ]

def get_data():
    with open("../data/test/10as065n5.npy", "rb") as f:
        roi = np.load(f)

    exterior = np.zeros_like(roi)

    for i in range(1, roi.shape[0] - 1):
        for j in range(1, roi.shape[1] - 1):
            for k in range(1, roi.shape[2] - 1):
                if roi[i, j, k] and not np.all(roi[i, j - 1:j + 2, k - 1:k + 2]):
                    exterior[i, j, k] = True

    return exterior


data = get_data()

points_3d = np.argwhere(data)[:, ::-1] * meta.Scale(5.03, 42.017).xyz()

alpha_shape = alphashape.alphashape(points_3d, 0.015)

pcd = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(points_3d))
trimesh = o3d.geometry.TriangleMesh()
trimesh.vertices = o3d.utility.Vector3dVector(alpha_shape.vertices)
trimesh.triangles = o3d.utility.Vector3iVector(alpha_shape.faces)
trimesh.compute_vertex_normals()
o3d.visualization.draw_geometries([pcd, trimesh], mesh_show_back_face=True)
