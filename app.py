from flask import Flask, send_from_directory
import os
from web_vis import load_point_cloud, load_bounding_boxes, export_visualization_to_gltf

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/models/<path:path>')
def send_model(path):
    return send_from_directory('static/models', path)

@app.route('/generate-model')
def generate_model():
    num = '000003'
    base_file = 'data/kitti/training'
    bin_path = f'{base_file}/velodyne/{num}.bin'
    txt_path = f'{base_file}/label_2/{num}.txt'
    output_path = 'static/models/output_model.gltf'

    points = load_point_cloud(bin_path)
    boxes = load_bounding_boxes(txt_path)
    export_visualization_to_gltf(points, boxes, output_path)
    return "Model generated successfully!"

if __name__ == '__main__':
    app.run(debug=True)
