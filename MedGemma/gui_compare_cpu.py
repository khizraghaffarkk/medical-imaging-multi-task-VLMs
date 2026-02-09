import os
from transformers import pipeline
from PIL import Image
import torch
import numpy as np
import skimage
import gradio as gr

# ------------------------------
# Setup Model
# ------------------------------
os.environ["CUDA_VISIBLE_DEVICES"] = ""  # CPU only
torch._dynamo.disable()

pipe = pipeline(
    "image-text-to-text",
    model="google/medgemma-1.5-4b-it",
    device=-1,
    torch_dtype=torch.float32
)
pipe.model.generation_config.do_sample = False

# ------------------------------
# Image preprocessing functions
# ------------------------------
def pad_image_to_square(image: Image.Image) -> Image.Image:
    image_array = np.array(image)
    image_array = skimage.util.img_as_ubyte(image_array)
    if len(image_array.shape) < 3:
        image_array = skimage.color.gray2rgb(image_array)
    if image_array.shape[2] == 4:
        image_array = skimage.color.rgba2rgb(image_array)
    h, w = image_array.shape[:2]
    if h < w:
        pad_top = (w - h) // 2
        pad_bottom = w - h - pad_top
        image_array = np.pad(image_array, ((pad_top, pad_bottom), (0, 0), (0, 0)))
    elif w < h:
        pad_left = (h - w) // 2
        pad_right = h - w - pad_left
        image_array = np.pad(image_array, ((0, 0), (pad_left, pad_right), (0, 0)))
    return Image.fromarray(image_array)

def resize_for_display(image: Image.Image, max_size: int = 300) -> Image.Image:
    ratio = max_size / max(image.size)
    return image.resize((int(image.width * ratio), int(image.height * ratio)))

# ------------------------------
# Compare function
# ------------------------------
def compare_xrays(image1: Image.Image, image2: Image.Image):
    image1 = pad_image_to_square(image1)
    image2 = pad_image_to_square(image2)
    
    prompt = (
        "Provide a comparison of these two images and include details from "
        "the image which students should take note of when reading longitudinal CXR"
    )
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image1},
                {"type": "image", "image": image2},
                {"type": "text", "text": prompt}
            ]
        }
    ]
    output = pipe(text=messages, max_new_tokens=600)
    try:
        response = output[0]["generated_text"][-1]["content"]
    except Exception:
        response = str(output)
    
    return resize_for_display(image1), resize_for_display(image2), response

# ------------------------------
# Gradio Blocks layout
# ------------------------------
with gr.Blocks(title="MedGemma X-ray Longitudinal Comparison") as demo:
    gr.Markdown("Upload two chest X-ray images and MedGemma will compare them longitudinally.")
    
    with gr.Row():
        # Left column: CXR1 and CXR2 side by side
        with gr.Column(scale=1):
            with gr.Row():  # Side-by-side images
                cxr1 = gr.Image(type="pil", label="Upload Chest X-ray 1")
                cxr2 = gr.Image(type="pil", label="Upload Chest X-ray 2")
            out_cxr1 = gr.Image(label="CXR 1 (resized)")
            out_cxr2 = gr.Image(label="CXR 2 (resized)")
        
        # Right column: MedGemma comparison text
        with gr.Column(scale=1):
            out_text = gr.Textbox(label="MedGemma Longitudinal Comparison", lines=20, max_lines=50)

    compare_btn = gr.Button("Compare X-rays")
    compare_btn.click(
        fn=compare_xrays,
        inputs=[cxr1, cxr2],
        outputs=[out_cxr1, out_cxr2, out_text]
    )

demo.launch()
