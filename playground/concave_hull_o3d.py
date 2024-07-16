import open3d as o3d
import numpy as np
from processing.data import meta


with open("../data/test/10as065n5.npy", "rb") as f:
    roi = np.load(f)

scale = meta.Scale(5.03, 42.017)

roi_exterior = np.zeros_like(roi)

for i in range(1, roi.shape[0] - 1):
    for j in range(1, roi.shape[1] - 1):
        for k in range(1, roi.shape[2] - 1):
            if roi[i, j, k] and not np.all(roi[i, j - 1:j + 2, k - 1:k + 2]):
                roi_exterior[i, j, k] = True

pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(np.argwhere(roi_exterior)[:, ::-1] * scale.xyz())


o3d.visualization.draw_geometries([pcd])

mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(pcd, alpha=1)
mesh.compute_vertex_normals()
o3d.visualization.draw_geometries([mesh], mesh_show_back_face=True, mesh_show_wireframe=True)
