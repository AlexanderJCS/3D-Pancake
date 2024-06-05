import matplotlib.pyplot as plt
import numpy as np
import open3d as o3d


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


def o3d_point_cloud(dist_map: np.ndarray, center: np.ndarray):
    point_cloud = o3d.geometry.PointCloud(
        o3d.utility.Vector3dVector(np.argwhere(dist_map > 0))
    )

    # create a sphere to visualize the center
    sphere = o3d.geometry.TriangleMesh().create_sphere(radius=max(dist_map.shape) / 100, resolution=20)
    sphere.translate(center)

    o3d.visualization.draw_geometries([sphere, point_cloud])
