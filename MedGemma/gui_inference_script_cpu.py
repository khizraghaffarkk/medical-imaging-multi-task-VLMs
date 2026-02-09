import os
import gradio as gr
from transformers import pipeline
from PIL import Image
import torch

# Hide all GPUs
os.environ["CUDA_VISIBLE_DEVICES"] = ""
# Disable TorchDynamo / Inductor to avoid Triton errors
torch._dynamo.disable()

# CPU-only pipeline
pipe = pipeline(
    "image-text-to-text",
    model="google/medgemma-1.5-4b-it",
    device=-1,               # CPU only
    torch_dtype=torch.float32
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
    # Extract safely
    try:
        return output[0]["generated_text"][-1]["content"]
    except Exception:
        return str(output)

iface = gr.Interface(
    fn=describe_xray,
    inputs=gr.Image(type="pil", label="Upload Chest X-ray",  min_width=300),
    outputs=gr.Textbox(
        label="MedGemma Description",
        lines=15,         # <-- increase number of visible lines
        max_lines=30      # optional: allow scrolling if text is longer
    ),
    title="MedGemma X-ray Description",
    description="Upload a chest X-ray image and MedGemma will describe it."
)

iface.launch()
