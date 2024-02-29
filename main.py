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

    main_image, gallery_images = generate_image(input_text, style_choice, use_base_style)

    # 如果主图像不存在，则返回错误
    if not main_image:
        return jsonify({'error': 'No main image generated.'}), 500

    # 將主要图像轉換為 base64
    with open(main_image, "rb") as img_file:
        img_bytes = img_file.read()
    main_img_b64 = base64.b64encode(img_bytes).decode('utf-8')

    # 將画廊图像轉換為 base64
    gallery_data = []
    for image_path in gallery_images:
        if image_path:  # 确保 image_path 不为空
            with open(image_path, "rb") as img_file:
                img_bytes = img_file.read()
            img_b64 = base64.b64encode(img_bytes).decode('utf-8')
            gallery_data.append(img_b64)
        else:
            print("Warning: An image path in gallery_images was empty.")

    # 回傳 base64 編碼的圖片
    return jsonify({'main_image': main_img_b64, 'gallery_images': gallery_data})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
