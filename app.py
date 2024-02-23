import json
import os
import time
import random

import gradio as gr
import numpy as np
import requests
from style_template import styles
from PIL import Image
from typing import Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)


URL = "http://35.211.102.39:8188/prompt"
INPUT_DIR = "/home/dryma/ComfyUI/input"
OUTPUT_DIR = "/home/dryma/ComfyUI/output"
STYLE_NAMES = list(styles.keys())
DEFAULT_STYLE_NAME = "Vibrant Color"
cached_seed = 0
intro_text = """
想快手變身動漫人物，保持自己樣但又想換新造型？即時ID幫到你，幾秒就搞掂！搵張有臉嘅相，記得要清楚啲，唔好太細張，避免大遮擋或者模糊。想更貼心？仲可以加張參考相，幫到我哋更好捕捉到你想要嘅面部姿勢。唔上載都得，咁我哋就會用返第一張相嚟做參考。控制下生成過程？揀揀ControlNet模型，預設係得IdentityNet，但你想加入姿勢、輪廓或深度效果都得。最後，輸入下你嘅文本提示，按下提交，等下新相就到手！快啲同朋友分享下你嘅獨特造型啦！
"""


def start_queue(prompt_workflow):
    logging.info('Starting queue with prompt_workflow: %s', prompt_workflow)
    
    p = {"prompt": prompt_workflow}
    data = json.dumps(p).encode('utf-8')
    response = requests.post(URL, data=data)

    if response.status_code != 200:
        logging.error('API request to start queue failed with status code %s: %s',
                      response.status_code, response.text)
    else:
        logging.info('API request to start queue successful.')

def apply_style(
    style_name: str, positive: str, negative: str = ""
) -> Tuple[str, str]:
    p, n = styles.get(style_name, styles[DEFAULT_STYLE_NAME])
    return p.replace("{prompt}", positive), n + " " + negative

def get_latest_image(folder):
    files = os.listdir(folder)
    image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    image_files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)))
    latest_image = os.path.join(folder, image_files[-1]) if image_files else None
    return latest_image


def generate_image(input_image, input_text,style_name):
    with open("workflow_api.json", "r") as file_json:
        prompt = json.load(file_json)
    styled_positive_prompt, _ = apply_style(style_name, input_text)

    prompt["3"]["inputs"]["seed"] = random.randint(1, 1500000)
    prompt["39"]["inputs"]["text"] = styled_positive_prompt
 
    
    global cached_seed
    if cached_seed == prompt["3"]["inputs"]["seed"]:
        return get_latest_image(OUTPUT_DIR)
    cached_seed = prompt["3"]["inputs"]["seed"]

    # Process and save the uploaded image
    image = Image.fromarray(np.array(input_image).astype('uint8'), 'RGB')
    min_side = min(image.size)
    scale_factor = 512 / min_side
    new_size = (round(image.size[0] * scale_factor), round(image.size[1] * scale_factor))
    resized_image = image.resize(new_size)
    image_path = os.path.join(INPUT_DIR, "uploaded_image.jpg")
    resized_image.save(image_path)
    prompt["13"]["inputs"]["image"] =image_path 
    logging.info('Saved uploaded image at %s', image_path)

    # Save the updated configuration
    with open("workflow_api_temp.json", "w") as temp_file:
        json.dump(prompt, temp_file)

    # Assuming you've modified start_queue to use the updated workflow configuration
    start_queue(prompt)
    logging.info('Started queue with seed %d', prompt["3"]["inputs"]["seed"])

    previous_image = get_latest_image(OUTPUT_DIR)
    timeout = 140 
    # Wait for new image generation
    while True:
        latest_image = get_latest_image(OUTPUT_DIR)
        if latest_image != previous_image:
           logging.info('New image generated: %s', latest_image)
           break
        time.sleep(1)

    # Return the new image
    return latest_image


demo = gr.Interface(
    fn=generate_image, title="快手變身",description=intro_text,
    inputs=[gr.Image(), gr.Text(), gr.Dropdown(choices=STYLE_NAMES, label="Select Style")], 
    outputs=gr.Image()
)
demo.launch(share=True)
