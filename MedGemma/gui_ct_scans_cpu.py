
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import io
import base64
import concurrent.futures
from PIL import Image
import numpy as np
import pydicom
import torch
from transformers import pipeline
import gradio as gr

#./input_images/ct_scan/dicoms
# -------------------------
# Config
# -------------------------
MAX_SLICES = 20  # Max slices to feed MedGemma

WINDOWS = [
    (-1024, 1024),  # Red: Wide window
    (-135, 215),    # Green: Soft tissue
    (0, 80)         # Blue: Brain
]

# instruction_text = (
#     "You are an instructor teaching medical students. "
#     "You are analyzing a contiguous block of CT slices from the abdomen. "
#     "Focus on the liver and surrounding abdominal organs."
# )

# query_text = (
#     "Based on the visual evidence in the slices provided above, "
#     "is this image a good teaching example of liver pathology? "
#     "Comment on any hypodense lesions, liver irregularities, or other relevant abdominal findings. "
#     "Do not comment on findings outside the abdomen. "
#     "Please provide reasoning and conclude with 'Final Answer: yes' or 'Final Answer: no'."
# )

instruction_text = (
    "You are a radiologist reviewing an abdominal CT scan. "
    "Focus on liver, spleen, pancreas, and kidneys."
)

query_text = (
    "Evaluate the scan for the following abdominal organs: liver, spleen, pancreas, kidneys, adrenal glands, "
    "bowel, lymph nodes, and presence of free fluid. "
    "For each organ, provide a short line about its status (e.g., 'Liver: normal'). "
    "At the end, provide an IMPRESSION line summarizing overall findings. "
    "Conclude with 'Final Answer: normal' or 'Final Answer: abnormal'. "
    "Use the following format strictly:\n\n"
    "FINDINGS:\n"
    "Liver: ...\n"
    "Spleen: ...\n"
    "Pancreas: ...\n"
    "Kidneys: ...\n"
    "Adrenal glands: ...\n"
    "Bowel: ...\n"
    "Lymph nodes: ...\n"
    "Free fluid: ...\n"
    "IMPRESSION: ...\n"
    "Final Answer: ..."
)


# -------------------------
# Helper Functions
# -------------------------
def load_dicom_folder(folder_path):
    dicom_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".dcm")]
    dicom_instances = []
    for f in dicom_files:
        try:
            ds = pydicom.dcmread(f)
            dicom_instances.append(ds)
        except Exception:
            continue
    if not dicom_instances:
        raise RuntimeError("No valid DICOM files found in folder.")
    dicom_instances.sort(key=lambda x: int(getattr(x, "InstanceNumber", 0)))
    if len(dicom_instances) > MAX_SLICES:
        dicom_instances = [
            dicom_instances[int(round(i / MAX_SLICES * (len(dicom_instances) - 1)))]
            for i in range(1, MAX_SLICES + 1)
        ]
    return dicom_instances

def extract_pixels(dicom_instances):
    def load_pixel_array(ds):
        arr = ds.pixel_array
        if hasattr(ds, "RescaleSlope") and hasattr(ds, "RescaleIntercept"):
            arr = arr * ds.RescaleSlope + ds.RescaleIntercept
        return arr
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        return list(executor.map(load_pixel_array, dicom_instances))

def window_and_normalize(slice_array):
    channels = []
    for win_min, win_max in WINDOWS:
        slice_clipped = np.clip(slice_array, win_min, win_max)
        norm = ((slice_clipped - win_min) / (win_max - win_min) * 255.0).astype(np.uint8)
        channels.append(norm)
    return np.stack(channels, axis=-1)

# def create_gif(rgb_slices):
#     images = [Image.fromarray(s) for s in rgb_slices]
#     with io.BytesIO() as buffer:
#         images[0].save(
#             buffer,
#             save_all=True,
#             append_images=images[1:],
#             format="GIF",
#             duration=len(images) * 3,
#             loop=0
#         )
#         buffer.seek(0)
#         return buffer.read()

def encode_base64(slice_array):
    with io.BytesIO() as buffer:
        Image.fromarray(slice_array).save(buffer, format="jpeg")
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"

def build_messages(rgb_slices):
    content = [{"type": "text", "text": instruction_text}]
    for s in rgb_slices:
        content.append({"type": "image", "image": encode_base64(s)})
    content.append({"type": "text", "text": query_text})
    return [{"role": "user", "content": content}]

# -------------------------
# Load MedGemma model once
# -------------------------
print("Loading MedGemma model. This may take a few minutes...")
pipe = pipeline(
    "image-text-to-text",
    model="google/medgemma-1.5-4b-it",
    device=-1,  # CPU; set device=0 for GPU
    torch_dtype=torch.float32
)
pipe.model.generation_config.do_sample = False
print("MedGemma loaded.")

# -------------------------
# Main function for Gradio
# -------------------------
def analyze_dicom_folder(folder_path):
    dicom_instances = load_dicom_folder(folder_path)
    ct_slices = extract_pixels(dicom_instances)
    rgb_slices = [window_and_normalize(s) for s in ct_slices]

    # Convert GIF bytes to PIL Image for Gradio
    # Show first slice as preview
    preview_image = Image.fromarray(rgb_slices[0])


    messages = build_messages(rgb_slices)

    # Run MedGemma
    output = pipe(text=messages, max_new_tokens=800)
    try:
        response_text = output[0]["generated_text"][-1]["content"]
    except Exception:
        response_text = str(output)

    return preview_image, response_text

# -------------------------
# Gradio GUI
# -------------------------
with gr.Blocks(title="MedGemma CT Analyzer") as demo:
    gr.Markdown("Upload a folder of CT DICOMs and MedGemma will analyze the slices.")
    dicom_folder_input = gr.Textbox(label="Path to DICOM folder", placeholder="./input_images/ct_scan/dicoms")
    preview_output = gr.Image(label="Preview CT Slice", type="pil")  


    text_output = gr.Textbox(label="MedGemma Analysis", lines=20)
    analyze_btn = gr.Button("Analyze DICOM Folder")
    analyze_btn.click(fn=analyze_dicom_folder, inputs=[dicom_folder_input], outputs=[preview_output, text_output])

demo.launch()
