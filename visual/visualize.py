import matplotlib.pyplot as plt
import numpy as np
import open3d as o3d

from processing import data
from processing import obb
from processing import mesh

from typing import Optional


class SliceViewer:
    def __init__(self, distance_map, cmap="gray", clamp_negative=True):
        self.distance_map = distance_map
        if clamp_negative:
            self.distance_map[self.distance_map < 0] = 0  # clamp negative values to 0

        self.current_slice = 0

        self.fig, self.ax = plt.subplots()

        self.im = self.ax.imshow(
            self.distance_map[self.current_slice],
            cmap=cmap,
            vmin=distance_map.min(),
            vmax=distance_map.max()
        )

        self.fig.colorbar(self.im)

        self._update()

    def _handle_event(self, up: bool):
        if up:
            self.current_slice = (self.current_slice + 1) % self.distance_map.shape[0]
        else:
            self.current_slice = (self.current_slice - 1) % self.distance_map.shape[0]
        self._update()

    def _on_scroll(self, event):
        self._handle_event(event.step < 0)

    def _on_key(self, event):
        self._handle_event(event.key == "right" or event.key == "up")

    def _on_click(self, event):
        # Get the clicked location and print the value at that location
        x, y = int(event.xdata), int(event.ydata)
        print(self.distance_map[self.current_slice, y, x])

    def _update(self):
        self.im.set_data(self.distance_map[self.current_slice])
        self.ax.set_title(f"Slice {self.current_slice+1}")
        self.fig.canvas.draw_idle()  # Use draw_idle instead of draw for better performance

    def visualize(self):
        self.fig.canvas.mpl_connect("scroll_event", self._on_scroll)
        self.fig.canvas.mpl_connect("key_press_event", self._on_key)
        self.fig.canvas.mpl_connect("button_press_event", self._on_click)

        plt.show(block=True)  # if plt.show is not blocking, it will cause the window to not respond


def calculate_zy_rotation_for_arrow(vec):
    # Answer by Yi Liu: https://stackoverflow.com/questions/59026581/create-arrows-in-open3d
    gamma = np.arctan2(vec[1], vec[0])
    r_z = np.array([
                    [np.cos(gamma), -np.sin(gamma), 0],
                    [np.sin(gamma), np.cos(gamma), 0],
                    [0, 0, 1]
                ])

    vec = r_z.T @ vec

    beta = np.arctan2(vec[0], vec[2])
    r_y = np.array([
                    [np.cos(beta), 0, np.sin(beta)],
                    [0, 1, 0],
                    [-np.sin(beta), 0, np.cos(beta)]
                ])
    return r_z, r_y


def get_arrow(vec: np.ndarray, origin=np.array([0, 0, 0]), scale=1):
    # Answer by Yi Liu: https://stackoverflow.com/questions/59026581/create-arrows-in-open3d
    size = np.sqrt(np.sum(vec ** 2))

    r_z, r_y = calculate_zy_rotation_for_arrow(vec)
    arrow_mesh = o3d.geometry.TriangleMesh().create_arrow(
        cone_radius=max(size / 17.5 * scale, 0.05),
        cone_height=max(size * 0.2 * scale, 0.05),
        cylinder_radius=max(size / 30 * scale, 0.05),
        cylinder_height=max(size * (1 - 0.2 * scale), 0.05)
    )
    arrow_mesh.rotate(r_y, center=np.array([0, 0, 0]))
    arrow_mesh.rotate(r_z, center=np.array([0, 0, 0]))
    arrow_mesh.translate(origin)
    return arrow_mesh


def lineset_from_vectors(vectors: np.ndarray, scale: data.Scale):
    lineset = o3d.geometry.LineSet()
    vectors_flat = vectors.reshape(-1, vectors.shape[-1])  # ::-1 to convert from zyx to xyz

    # reshape to xyz
    vectors_flat = vectors_flat.reshape(-1, 3)

    # create original xyz coordinates
    original_xyz = np.array([
        [x, y, z]
        for z in range(vectors.shape[0])
        for y in range(vectors.shape[1])
        for x in range(vectors.shape[2])]
    ).astype(float)

    # scale by xyz
    vectors_flat *= scale.xyz()
    original_xyz *= scale.xyz()

    # put in the pattern of [[original_xyz], [original_xyz + vector], ...]
    stacked = np.column_stack((original_xyz, original_xyz + vectors_flat))
    interleaved = stacked.reshape(-1, original_xyz.shape[-1])

    print(interleaved.shape)
    print(interleaved)

    lineset.points = o3d.utility.Vector3dVector(interleaved)

    # create lines with the pattern [[0, 1], [2, 3], [4, 5], ...]
    lines = np.array([
        [i, i + 1]
        for i in range(0, vectors_flat.shape[0], 2)
    ])

    lineset.lines = o3d.utility.Vector2iVector(lines)

    return lineset


def o3d_point_cloud(
        dist_map: np.ndarray,
        scale: data.Scale,
        obbs: Optional[list[obb.Obb]] = None,
        psd_mesh: Optional[mesh.Mesh] = None,
        center: Optional[np.ndarray] = None,
        vectors: Optional[np.ndarray] = None
):
    vis = o3d.visualization.Visualizer()
    vis.create_window(window_name="3D Visualization")
    vis.get_render_option().mesh_show_back_face = True
    vis.get_render_option().mesh_show_wireframe = True

    vis.add_geometry(
        o3d.geometry.PointCloud(
            o3d.utility.Vector3dVector(
                np.argwhere(dist_map > 0).astype(float)[:, ::-1] * scale.xyz()  # remove negative values and scale
            )
        )
    )

    if obbs is not None:
        for box in obbs:
            vis.add_geometry(box.o3d_obb)

    if psd_mesh is not None:
        vis.add_geometry(psd_mesh.mesh)

    if center is not None:
        # create a sphere to visualize the center
        sphere = o3d.geometry.TriangleMesh().create_sphere(radius=max(dist_map.shape * scale.zyx()) / 75, resolution=20)
        sphere.translate(center)
        vis.add_geometry(sphere)

    if vectors is not None:
        print("vectors")
        lineset = lineset_from_vectors(vectors, scale)
        vis.add_geometry(lineset)
        print("added lineset")

    vis.run()
    vis.destroy_window()
