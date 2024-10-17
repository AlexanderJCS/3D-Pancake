import json
import os

from processing import processing
from processing.data import meta

import open3d as o3d
import numpy as np


class VisTester:
    def __init__(self):
        self.files = [f for f in os.listdir("../data/test") if f.endswith(".npy")]
        self.outputs = self._gen_outputs()
        
        self.index = -1
        
        with open("../data/test/areas.json", "r") as f:
            self.ground_truth_file = json.load(f)
        
        self.output_areas = [output.area_nm / 1e6 for output in self.outputs]
        self.ground_truths = [
            self.ground_truth_file.get(os.path.basename(file)[:file.rfind(".")]) for file in self.files
        ]
        
        self.vis = o3d.visualization.VisualizerWithKeyCallback()
    
    def run(self):
        self.vis.create_window(window_name="Visualizer")
        
        self.vis.get_render_option().mesh_show_back_face = True
        self.vis.get_render_option().mesh_show_wireframe = True
        
        self.vis.register_key_callback(ord("D"), self.callback_next)
        self.vis.register_key_callback(ord("A"), self.callback_prev)
        
        self.callback_next(self.vis)  # so there is something to visualize
        
        self.vis.run()
    
    def _gen_outputs(self):
        outputs = []
        for file in self.files:
            print("Processing", file)
            data = np.load(f"../data/test/{file}")
            output = processing.get_area(data, meta.Scale(5.03, 42.017), c_s=0.2, visualize=False)
            outputs.append(output)
        
        return outputs
    
    def draw(self, vis: o3d.visualization.VisualizerWithKeyCallback, index: int):
        output = self.outputs[index]
        
        vis.clear_geometries()
        vis.add_geometry(output.obb.o3d_obb)
        vis.add_geometry(output.psd_mesh.mesh)
        vis.add_geometry(o3d.geometry.PointCloud(o3d.utility.Vector3dVector(output.points)))
        
        vis.reset_view_point(True)
        
        # Print the area and the ground truth
        print("-" * 20)
        print(f"Index: {index + 1}/{len(self.files)}")
        print(f"File: {self.files[index]}")
        print(f"Area: {self.output_areas[index]:.6f} μm²")
        print(f"Ground truth: {self.ground_truths[index]:.6f} μm²")
        print(f"Difference: {self.output_areas[index] - self.ground_truths[index]:.6f} μm²")
    
    def callback_next(self, vis: o3d.visualization.VisualizerWithKeyCallback):
        self.index += 1
        if self.index >= len(self.files):
            self.index -= 1
            return
        
        self.draw(vis, self.index)
        
    def callback_prev(self, vis: o3d.visualization.VisualizerWithKeyCallback):
        self.index -= 1
        if self.index < 0:
            self.index = 0
            return
        
        self.draw(vis, self.index)


def main():
    vis = VisTester()
    vis.run()


if __name__ == "__main__":
    main()
