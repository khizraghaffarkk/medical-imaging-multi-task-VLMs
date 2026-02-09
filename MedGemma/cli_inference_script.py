import gradio as gr
from transformers import pipeline
from PIL import Image

# -------------------------
# Initialize MedGemma Pipeline (CPU only)
# -------------------------
pipe = pipeline(
    task="image-text-to-text",
    model="google/medgemma-1.5-4b-it",
    device_map={"": "cpu"},   # explicit CPU
    torch_dtype="float32"
)

# -------------------------
# Gradio Inference Function
# -------------------------
def analyze_image(image, question):
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": question}
            ]
        }
    ]
    
    output = pipe(text=messages, max_new_tokens=512)
    
    # Extract generated text safely
    try:
        result = output[0]["generated_text"][-1]["content"]
    except Exception:
        result = str(output)
    return result

# -------------------------
# Gradio GUI
# -------------------------
iface = gr.Interface(
    fn=analyze_image,
    inputs=[
        gr.Image(type="pil", label="Upload Image"),
        gr.Textbox(label="Ask a question about the image", placeholder="e.g., Describe this X-ray")
    ],
    outputs=gr.Textbox(label="Model Output"),
    title="MedGemma Image-QA",
    description="Upload a medical image (X-ray, CT, MRI) and ask any question. The model will generate a textual description or answer based on the image.",
    allow_flagging="never"
)

iface.launch()
