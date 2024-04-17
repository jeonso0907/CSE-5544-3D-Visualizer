import numpy as np
import open3d as o3d
import json

def load_point_cloud(bin_path, max_value=20):
    points = np.fromfile(bin_path, dtype=np.float32).reshape(-1, 4)
    # Filter points where any of x, y, or z exceeds max_value
    points = points[(np.abs(points[:, :3]) <= max_value).all(axis=1)]
    return points

def load_bounding_boxes(txt_path):
    boxes = []
    with open(txt_path, 'r') as file:
        for line in file:
            data = line.split()
            category = data[0]  # Get the category of the object
            h, w, l = map(float, data[8:11])
            y, z, x = map(float, data[11:14])
            rotation_y = float(data[14])
            boxes.append((x, -y, -z, h, w, l, rotation_y, category))
    return boxes

def create_bounding_box(box):
    x, y, z, h, w, l, ry, _ = box  # Ignore category here
    z = z + h / 2  # Adjust the center for z-coordinate
    bbox = o3d.geometry.OrientedBoundingBox(center=[x, y, z], R=o3d.geometry.get_rotation_matrix_from_axis_angle([0, ry, 0]), extent=[w, h, l])
    return bbox

def create_colormap(points, max_distance):
    colors = np.zeros((points.shape[0], 3))
    for i, point in enumerate(points):
        # Normalize the X-coordinate to the range [-1, 1] and then scale to [0, 1]
        x_normalized = (point[0] / max_distance + 1) / 2
        # Apply the colormap: Blue for negative X, Red for positive X, White for near 0
        colors[i] = [x_normalized, 0.5 * (1 - abs(x_normalized - 0.5)), 1 - x_normalized]
    return colors

def visualize_point_cloud(points, boxes, distance_threshold=5):
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points[:, :3])

    # Find max distance for coloring
    max_distance = np.abs(points[:, 0]).max()  # Assuming forward direction is X

    # Create a colormap for all points initially
    colormap = create_colormap(points[:, :3], max_distance)

    # Apply the category-based colors to points inside bounding boxes
    category_colors = {
        'Car': [1, 0, 0],  # Red
        'Pedestrian': [0, 0, 1],  # Blue
        'Misc': [0, 1, 0]
    }
    for box in boxes:
        obb = create_bounding_box(box)
        category = box[-1]
        color = category_colors.get(category, [0.5, 0.5, 0.5])  # Default to gray if category not found
        indices = obb.get_point_indices_within_bounding_box(o3d.utility.Vector3dVector(points[:, :3]))
        for idx in indices:
            colormap[idx] = color  # Color the points based on the category

    pcd.colors = o3d.utility.Vector3dVector(colormap)

    # Initialize the visualizer
    visualizer = o3d.visualization.Visualizer()
    visualizer.create_window()
    visualizer.add_geometry(pcd)

    # Add bounding boxes to the visualizer
    for box in boxes:
        obb = create_bounding_box(box)
        visualizer.add_geometry(obb)

    render_option = visualizer.get_render_option()
    render_option.point_size = 3

    # visualizer.get_render_option().load_from_json('data/vis_setting.json')
    ctrl = visualizer.get_view_control()

    # Assuming you have calculated the center of your point cloud or bounding boxes
    center_point = np.mean(points[:, :3], axis=0)

    # Calculate a reasonable scale to set the zoom level
    scale = np.max(np.linalg.norm(points[:, :3] - center_point, axis=1))

    # Set the camera to focus on the center point and adjust the zoom based on scale
    lookat = center_point
    front = np.array([0, 0, 1])  # Adjust based on your data orientation
    up = np.array([0, -1, 0])  # Adjust up direction if needed
    zoom = 0.5 * scale  # Adjust this factor based on your preferences

    ctrl.set_lookat(lookat)
    ctrl.set_front(front)
    ctrl.set_up(up)
    ctrl.set_zoom(zoom)

    # Run the visualizer
    visualizer.run()
    visualizer.destroy_window()

# Paths to your KITTI dataset files
num = '000011'
base_file = 'data/kitti/training'
bin_path = f'{base_file}/velodyne/{num}.bin'
txt_path = f'{base_file}/label_2/{num}.txt'

# Load point cloud
points = load_point_cloud(bin_path)

# Load bounding boxes
boxes = load_bounding_boxes(txt_path)

# Visualize
visualize_point_cloud(points, boxes, 5)
