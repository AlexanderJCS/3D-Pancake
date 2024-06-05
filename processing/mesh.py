from . import obb

import open3d as o3d
import numpy as np


class Mesh:
    def __init__(self, bounding_box: obb.Obb, geom_center: np.ndarray):
        self.bounding_box = bounding_box
        self.point_cloud = self._gen_pcd(bounding_box)

    @staticmethod
    def _gen_pcd(bounding_box: obb.Obb) -> o3d.geometry.TriangleMesh:
        sides = np.array(bounding_box.o3d_obb.extent)
        largest_face_index = np.argmax(sides)

        # Generate points in a grid format for the plane of the largest face
        if largest_face_index == 0:
            points_u = np.arange(0, sides[1], 1)
            points_v = np.arange(0, sides[2], 1)
            points_x, points_y, points_z = np.meshgrid([0], points_u, points_v)
        elif largest_face_index == 1:
            points_u = np.arange(0, sides[0], 1)
            points_v = np.arange(0, sides[2], 1)
            points_x, points_y, points_z = np.meshgrid(points_u, [0], points_v)
        else:  # largest_face_index == 2
            points_u = np.arange(0, sides[0], 1)
            points_v = np.arange(0, sides[1], 1)
            points_x, points_y, points_z = np.meshgrid(points_u, points_v, [0])

        points = np.vstack((points_x.flatten(), points_y.flatten(), points_z.flatten())).T

        # Create the mesh
        mesh = o3d.geometry.TriangleMesh()
        mesh.vertices = o3d.utility.Vector3dVector(points)

        # Generate the triangles for the mesh
        indices = []
        num_u, num_v = len(points_u), len(points_v)

        for i in range(num_u - 1):
            for j in range(num_v - 1):
                p1 = i * num_v + j
                p2 = p1 + 1
                p3 = (i + 1) * num_v + j
                p4 = p3 + 1

                indices.append([p1, p3, p2])
                indices.append([p2, p3, p4])

        mesh.triangles = o3d.utility.Vector3iVector(indices)

        # Apply the rotation and translation to match the OBB
        mesh.rotate(bounding_box.o3d_obb.R)
        mesh.translate(bounding_box.o3d_obb.center - np.array(mesh.get_center()))

        return mesh
