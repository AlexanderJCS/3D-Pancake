import shapely
import open3d as o3d  # for visualization
import numpy as np

from processing.data import meta


scale = meta.Scale(5.03, 42.017)


def generate_edges(vertices):
    edges = []

    for i in range(0, len(vertices), 3):
        edges.append((i, i + 1, i + 2))

    return edges


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


roi_exterior = get_data()

multi_point = shapely.geometry.MultiPoint(np.argwhere(roi_exterior)[:, ::-1] * scale.xyz())
concave_hull = shapely.concave_hull(multi_point, ratio=0.002)

vertices = np.array(concave_hull.exterior.coords)
triangles = [[i, i + 1, i + 2] for i in range(0, len(vertices) - 2, 3)]

pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(vertices)

mesh = o3d.geometry.TriangleMesh()
mesh.vertices = o3d.utility.Vector3dVector(vertices)
mesh.triangles = o3d.utility.Vector3iVector(triangles)

o3d.visualization.draw_geometries([mesh, pcd], mesh_show_back_face=True)
