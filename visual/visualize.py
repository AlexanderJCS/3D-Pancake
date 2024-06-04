import matplotlib.pyplot as plt


class Interactive3DVisualizer:
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

    def _update(self):
        self.im.set_data(self.distance_map[self.current_slice])
        self.ax.set_title(f"Slice {self.current_slice+1}")
        self.fig.canvas.draw_idle()  # Use draw_idle instead of draw for better performance

    def visualize(self):
        self.fig.canvas.mpl_connect("scroll_event", self._on_scroll)
        plt.show(block=True)  # if plt.show is not blocking, it will cause the window to not respond
