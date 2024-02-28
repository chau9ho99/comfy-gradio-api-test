import os
import json
import time
import glob
import random
import requests
import gradio as gr
from PIL import Image

URL = "http://34.70.55.198:8188/prompt"
INPUT_DIR = "/ComfyUI/input"
OUTPUT_DIR = "/ComfyUI/output/SDXL_LIGHT"
cached_seed = 0

def start_queue(prompt_workflow):
    p = {"prompt": prompt_workflow}
    data = json.dumps(p).encode('utf-8')
    requests.post(URL, data=data)

def get_style_names(json_file):
    try:
        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)
            categories = data["categories"]
            return [(value, key) for category in categories for key, value in category.items()]
    except Exception as e:
        print(f"Error: {str(e)}")
        return []

def get_latest_image(folder):
    files = os.listdir(folder)
    image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    image_files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)))
    latest_image = os.path.join(folder, image_files[-1]) if image_files else None
    return latest_image

def generate_image(input_text, style_choice="photo-hdr", use_base_style=False):
    with open("light.json", "r") as file_json:
        prompt = json.load(file_json)
    prompt["3"]["inputs"]["seed"] = random.randint(1, 1500000)

    global cached_seed
    if cached_seed == prompt["3"]["inputs"]["seed"]:
        return [get_latest_image(OUTPUT_DIR)] + gallery_images()

    cached_seed = prompt["3"]["inputs"]["seed"]

    if isinstance(style_choice, list) and len(style_choice) == 0:
        style_choice = "photo-hdr"  # Or another appropriate default value

    if use_base_style:
        style_choice = "base"
    
    print(f"Input style value: {style_choice}")
    prompt["17"]["inputs"]["text_positive"] = input_text
    prompt["17"]["inputs"]["style"] = style_choice

    with open("light.json", "w") as temp_file:
        json.dump(prompt, temp_file)

    start_queue(prompt)

    previous_image = get_latest_image(OUTPUT_DIR)
        
    while True:
        latest_image = get_latest_image(OUTPUT_DIR)
        if latest_image != previous_image:
            break
        time.sleep(1)

    image_paths = [get_latest_image(OUTPUT_DIR)] + gallery_images()
    return image_paths[0], image_paths[1:]

def gallery_images():
    image_paths = glob.glob(f"{OUTPUT_DIR}/*.png")
    image_paths.sort(key=lambda x: os.path.getmtime(x))

    if not image_paths:
        return [None]*4

    latest_images = image_paths[-10:-1]

    return [image_path for i, image_path in enumerate(reversed(latest_images))]

def clear_previous_session():
    files = glob.glob(os.path.join(OUTPUT_DIR, "*"))
    for f in files:
        os.remove(f)

description = """
# 《創意文字藝術轉換器》

**簡介:**

《創意文字藝術轉換器》係一個超強嘅文字轉換應用軟件。你只需要輸入你想轉換嘅文字，然後選擇一種風格（或者選擇使用基本風格），就可以喺我哋嘅應用軟件上見到你嘅圖片被轉換成選擇嘅風格，就好似文字變成藝術品咁！真係又快捷又方便！

**使用指南:**

1. 開始嗰陣，你要先喺`Textbox`一欄入面輸入你想轉換嘅文字。

2. 然後，你可以喺下拉選單中揀選你想嘅風格。如果你唔揀風格，就可以選擇喺`Use base style`一欄裏打勾。打勾後，程式會將你嘅文字轉換成基本風格。

3. 揀好風格或者選擇了基本風格後，你只需撳下個`Submit`按鈕。之後，你就可以喺網頁的`Latest Image`和`Gallery Images`欄目中見到你輸入的文字變成各種全新風格嘅圖片啦！

希望呢度嘅介紹同指南對你有幫助。如果你有更多嘅問題，請隨時問我，我會好樂意答你。
"""

use_base_style = gr.Checkbox(label="Use base style")
style_names = get_style_names("sdxl_styles_zh.json")
style_choice = gr.Dropdown(choices=style_names, label="Style Choice")

clear_previous_session()

demo = gr.Interface(
    fn=generate_image, 
    inputs=[gr.Textbox(label="Text Input"), style_choice, use_base_style], 
    outputs=[
        gr.Image(label="Latest Image"),
        gr.Gallery(label="Gallery Images")
    ],
    description=description,
)

if __name__ == "__main__":
    demo.launch(share=True)
