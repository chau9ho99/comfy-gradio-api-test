from flask import Flask, request, send_file, jsonify
import requests
import json
from light_fast import generate_image
from PIL import Image
import io
import base64

app = Flask(__name__)


@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()

    input_text = data['input_text']
    style_choice = data['style_choice']
    use_base_style = data['use_base_style']
    aspect_ratio = data.get('aspectRatio')  # 添加这一行来获取新的 aspectRatio 参数，如果没有就返回None

    image_path = generate_image(input_text, style_choice, use_base_style,aspect_ratio)

    if not image_path:   # If the image does not exist, return an error
        return jsonify({'error': 'No image generated.'}), 500

    with open(image_path, 'rb') as img_file:
        img_bytes = img_file.read()
    img_b64 = base64.b64encode(img_bytes).decode('utf-8')

    return jsonify({'image': img_b64})

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
