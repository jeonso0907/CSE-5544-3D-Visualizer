import numpy as np
import open3d as o3d
import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering
import os
import platform
import sys

from scipy.spatial import distance


class AppWindow:
    def __init__(self, width, height):
        self.window = gui.Application.instance.create_window("Open3D", width, height)
        self._scene = gui.SceneWidget()
        self.window.add_child(self._scene)

        self.settings = {
            "bg_color": gui.Color(1, 1, 1),
            "show_skybox": False,
            "use_ibl": True,
            "ibl_intensity": 45000,
            "sun_intensity": 45000,
            "sun_dir": [0.577, -0.577, -0.577],
        }

        self.custom_colormap = [[1, 0, 0], [1, 0.3, 0.3], [1, 0.7, 0.7], [1, 1, 1]]
        self._apply_settings()

        # File menu
        file_menu = gui.Menu()
        file_menu.add_item("Open...", 1)
        file_menu.add_item("Export Current Image...", 2)
        file_menu.add_item("Quit", 3)
        gui.Application.instance.menubar = gui.Menu()
        gui.Application.instance.menubar.add_menu("File", file_menu)
        self.window.set_on_menu_item_activated(1, self._on_menu_open)
        self.window.set_on_menu_item_activated(2, self._on_menu_export)
        self.window.set_on_menu_item_activated(3, self._on_menu_quit)

        self._setup_colormaps_and_point_filter_controls()
        self.bounding_boxes = []
        self.current_point_cloud = None

    def _apply_settings(self):
        self._scene.scene.set_background([self.settings["bg_color"].red, self.settings["bg_color"].green,
                                          self.settings["bg_color"].blue, 1.0])
        self._scene.scene.show_skybox(self.settings["show_skybox"])
        self._scene.scene.scene.set_indirect_light_intensity(self.settings["ibl_intensity"])
        self._scene.scene.scene.set_sun_light(
            self.settings["sun_dir"], [1, 1, 1], self.settings["sun_intensity"]
        )

    def _setup_colormaps_and_point_filter_controls(self):
        # Add controls for colormap, point size, point filter, and 3D label tree
        # (Keeping the controls minimal)
        self._bg_color = gui.ColorEdit()
        self._bg_color.set_on_value_changed(self._on_bg_color)

        self._point_size = gui.Slider(gui.Slider.INT)
        self._point_size.set_limits(1, 10)
        self._point_size.set_on_value_changed(self._on_point_size)

        self._point_filter = gui.Slider(gui.Slider.INT)
        self._point_filter.set_limits(1, 100)
        self._point_filter.set_on_value_changed(self._on_point_filter)

        # Adding controls to the window
        v = gui.Vert(1)
        v.add_child(gui.Label("Background Color"))
        v.add_child(self._bg_color)
        v.add_child(gui.Label("Point Size"))
        v.add_child(self._point_size)
        v.add_child(gui.Label("Point Filter"))
        v.add_child(self._point_filter)

        self.window.add_child(v)

    def _on_menu_open(self):
        dlg = gui.FileDialog(gui.FileDialog.OPEN, "Choose a .bin point cloud", self.window.theme)
        dlg.add_filter(".bin", "Binary Point Cloud Data (.bin)")
        dlg.set_on_done(self._on_load_dialog_done)
        dlg.set_on_cancel(self._on_file_dialog_cancel)
        self.window.show_dialog(dlg)

    def _on_load_dialog_done(self, filename):
        self.window.close_dialog()
        self._load_point_cloud(filename)

    def _load_point_cloud(self, filename):
        self._scene.scene.clear_geometry()
        points = np.fromfile(filename, dtype=np.float32).reshape(-1, 4)
        cloud = o3d.geometry.PointCloud()
        cloud.points = o3d.utility.Vector3dVector(points[:, :3])
        self.current_point_cloud = cloud

        colormap = np.tile([0.5, 0.5, 0.5], (len(points), 1))
        cloud.colors = o3d.utility.Vector3dVector(colormap)

        self._scene.scene.add_geometry("__model__", cloud, self.settings)
        self._scene.setup_camera(60, self._scene.scene.bounding_box, [0, 0, 0])

    def _on_file_dialog_cancel(self):
        self.window.close_dialog()

    def _on_menu_export(self):
        dlg = gui.FileDialog(gui.FileDialog.SAVE, "Save Image", self.window.theme)
        dlg.add_filter(".png", "PNG files (.png)")
        dlg.set_on_done(self._on_export_dialog_done)
        dlg.set_on_cancel(self._on_file_dialog_cancel)
        self.window.show_dialog(dlg)

    def _on_export_dialog_done(self, filename):
        self.window.close_dialog()
        frame = self._scene.frame
        self._scene.scene.render_to_image(
            lambda img: o3d.io.write_image(filename, img, 9 if filename.endswith(".png") else 100)
        )

    def _on_menu_quit(self):
        gui.Application.instance.quit()

    def _on_bg_color(self, new_color):
        self.settings["bg_color"] = new_color
        self._apply_settings()

    def _on_point_size(self, size):
        pass  # Implement point size change logic

    def _on_point_filter(self, filter_range):
        pass  # Implement point filter logic


def main():
    gui.Application.instance.initialize()
    app_window = AppWindow(1024, 768)
    gui.Application.instance.run()


if __name__ == "__main__":
    main()
