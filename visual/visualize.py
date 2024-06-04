import matplotlib.pyplot as plt
import numpy as np


class Interactive3DVisualizer:
    def __init__(self, distance_map):
        self.distance_map = distance_map
        self.current_slice = 0

        self.fig, self.ax = plt.subplots()
        self.im = self.ax.imshow(self.distance_map[self.current_slice], cmap="jet")
        self._update()

    def _on_scroll(self, event):
        if event.button == "down":
            self.current_slice = (self.current_slice + 1) % self.distance_map.shape[0]
        elif event.button == "up":
            self.current_slice = (self.current_slice - 1) % self.distance_map.shape[0]
        self._update()

    def _update(self):
        self.im.set_data(self.distance_map[self.current_slice])
        self.ax.set_title(f"Slice {self.current_slice+1}")
        self.fig.canvas.draw_idle()  # Use draw_idle instead of draw for better performance

    def visualize(self):
        self.fig.canvas.mpl_connect("scroll_event", self._on_scroll)
        plt.show(block=True)  # if plt.show is not blocking, it will cause the window to not respond
