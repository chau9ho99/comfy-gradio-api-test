from flask import Flask, request, send_file, jsonify
import requests
import json
from light import generate_image
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

    image_paths = generate_image(input_text, style_choice, use_base_style)

    # 將圖片轉換為 base64
    image_data = []
    for image_path in image_paths:
        # If the image path is a list, take the first element
        if isinstance(image_path, list):
            image_path = image_path[0]
        
        with open(image_path, "rb") as img_file:
            img_bytes = img_file.read()
        img_b64 = base64.b64encode(img_bytes).decode('utf-8')
        image_data.append(img_b64)

    # 回傳 base64 編碼的圖片
    return jsonify({'images': image_data})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
