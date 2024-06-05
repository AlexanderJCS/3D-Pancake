from . import obb

import open3d as o3d
import numpy as np


class Mesh:
    def __init__(self, bounding_box: obb.Obb, geom_center: np.ndarray):
        self.bounding_box = bounding_box
        self.point_cloud = self._gen_pcd(bounding_box)

    @staticmethod
    def _gen_pcd(bounding_box: obb.Obb) -> o3d.geometry.PointCloud:
        # Create points with the same dimensions as the bounding box (planar to the largest face)
        # Then create a mesh
        # Then rotate the mesh to match the orientation of the bounding box
        # Then translate the mesh to intersect the geom_center while being completely inside the bounding box
        # Finally, return the mesh

        sides = np.array(bounding_box.o3d_obb.extent)
        largest_face_index = np.argmax(sides)

        points_x = np.zeros((int(sides[0]))) if largest_face_index == 0 else np.arange(0, int(sides[0]), 1, dtype=float)
        points_y = np.zeros((int(sides[1]))) if largest_face_index == 1 else np.arange(0, int(sides[1]), 1, dtype=float)
        points_z = np.zeros((int(sides[2]))) if largest_face_index == 2 else np.arange(0, int(sides[2]), 1, dtype=float)

        points_x, points_z = points_z, points_x

        mesh = o3d.geometry.TriangleMesh()
        points = np.array(np.meshgrid(points_x, points_y, points_z)).T.reshape(-1, 3)
        mesh.vertices = o3d.utility.Vector3dVector(points)

        # Get the number of points in the x, y, and z directions
        num_x = len(points_x)
        num_y = len(points_y)
        num_z = len(points_z)

        # Create an empty list to store the indices
        indices = []

        for i in range(num_x - 1):
            for j in range(num_y - 1):
                p1 = i * num_y + j
                p2 = p1 + 1
                p3 = (i + 1) * num_y + j
                p4 = p3 + 1

                indices.append([p1, p2, p3])
                indices.append([p2, p3, p4])

        # Assign the indices to the mesh
        mesh.triangles = o3d.utility.Vector3iVector(indices)

        # pcd = o3d.geometry.PointCloud(mesh.vertices)


        o3d.visualization.draw_geometries([mesh], mesh_show_back_face=True, mesh_show_wireframe=True)
