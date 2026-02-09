import gradio as gr
from transformers import pipeline
from PIL import Image
import torch

# GPU pipeline (FP32 for safety)
pipe = pipeline(
    "image-text-to-text",
    model="google/medgemma-1.5-4b-it",
    device=0,               # GPU
    torch_dtype=torch.float32  # <-- important, do NOT use float16 here
)

def describe_xray(image: Image.Image):
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": "Describe this X-ray"}
            ]
        }
    ]
    output = pipe(text=messages, max_new_tokens=512)
    try:
        return output[0]["generated_text"][-1]["content"]
    except Exception:
        return str(output)

iface = gr.Interface(
    fn=describe_xray,
    inputs=gr.Image(type="pil", label="Upload Chest X-ray", min_width=300),
    outputs=gr.Textbox(label="MedGemma Description", lines=15, max_lines=30),
    title="MedGemma X-ray Description",
    description="Upload a chest X-ray image and MedGemma will describe it."
)

iface.launch()
