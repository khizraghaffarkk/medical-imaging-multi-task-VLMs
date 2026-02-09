
# LLaVA-Med Inference Setup & Usage Guide (Windows)

This guide explains how to install and run **LLaVA-Med** for medical image understanding on **Windows** with GPU support.

You can install LLaVA-Med in two ways:

**Option A:** Automatic installation using the PowerShell script  
**Option B:** Manual installation step-by-step (no script)

----------

### Quick Start (Download from This Repository)

If you have cloned this repository, the `LLaVA-Med` folder contains all code and a setup script:

-   `install_LLaVAMed.ps1` → PowerShell installation script
    

The script will automatically:

-   Create a Conda environment (`llava-med`)
-   Install all Python dependencies
-   Verify GPU availability
-   Guide you to launch inference

The original **[LLaVA-Med](https://github.com/microsoft/LLaVA-Med)** code has a known issue on **Windows with bitsandbytes**. Specifically, when using CUDA 12.x, bitsandbytes tries to load Linux `.so` libraries (`libbitsandbytes_cuda128.so`), which **does not work on Windows**, even if PyTorch detects the GPU. This causes the model worker to crash during inference.

To fix this on Windows normally, users would need to manually uninstall bitsandbytes, modify the `model_worker.py` file to disable 4-bit/8-bit quantization, and set environment variables.

**Modification:**  
This repository contains an **updated LLaVA-Med code** that:

-   Disables bitsandbytes on Windows
-   Forces full-precision inference

You do **not** need to clone the original Microsoft repo separately.

----------

### Project Structure

After cloning this repository, your folder should look like this:
```plaintext
medical-imaging-multi-task-vision-language-models/
├── LLaVA-Med/
│   ├── llava/                  # LLaVA-Med code & other directories
│   ├── install_LLaVAMed.ps1    # Installation & launcher script
│   └── README.md               # This README file
```
**Notes:**

-   `install_LLaVAMed.ps1` should be in the **same folder** as the `llava` code.
-   Python environment and dependencies are handled automatically by the script.
-   After setup, all three inference components (Controller, Model Worker, Web UI) can be run simultaneously.
    

----------

### Requirements

Before starting, make sure you have:

**System & Software Requirements**

-   Windows 10 / Windows 11
-   Git installed
-   NVIDIA GPU + CUDA driver installed
-   Miniconda / Anaconda
    

**GPU Requirements / Notes**

-   **Minimum GPU VRAM:**  
    A single GPU with **≥ 24 GB VRAM** is recommended for comfortable inference.  
    Examples:
    
    -   RTX 3090 (~24 GB)
    -   RTX 4090 (~24 GB)
        
-   **Multiple GPUs:**  
    If your GPU has less than 24 GB VRAM, you can try splitting the model across multiple GPUs using the `--num-gpus` flag in the `model_worker` script.
    
    **Example (split across 2 GPUs):**
    
    ```bash
    python -m llava.serve.model_worker ` --host  0.0.0.0 ` --controller http://localhost:10000 ` --port  40000 ` --worker http://localhost:40000 ` --model-path microsoft/llava-med-v1.5-mistral-7b ` --multi-modal ` --num-gpus  2
    ``` 
    
    This will attempt to share the model across 2 GPUs for inference.
    
----------

## Option A: Install & Run LLaVA-Med using PowerShell Script

This method automatically:

-   Creates Conda environment `llava-med`
-   Installs required Python packages
-   Uninstalls conflicting packages (Windows workaround)
-   Launches Controller, Model Worker, and Web UI automatically in separate PowerShell windows

----------

### 1. Save Script

Ensure `install_LLaVAMed.ps1` is in the `LLaVA-Med` folder.

----------

### 2. Run Script

Open **PowerShell** inside the `LLaVA-Med` folder and run:
```bash
Set-ExecutionPolicy  -Scope  Process  -ExecutionPolicy Bypass
.\setup-llavamed.ps1
```
The script will:

-   Check for GPU
-   Install dependencies
-   Automatically open three PowerShell windows for Controller, Model Worker, and Web UI

Once the services are running, open your browser at:
-  [http://localhost:7860](http://localhost:7860)

Upload medical images or use default images and start interacting with LLaVA-Med.


**Note:** While asking questions in the Web UI, you may occasionally see this error:

> **NETWORK ERROR DUE TO HIGH TRAFFIC. PLEASE REGENERATE OR REFRESH THIS PAGE.**

This happens if multiple requests are sent simultaneously or the model is processing a large request. Simply **refresh the page** or **regenerate the answer** to continue.

----------

## Option B: Manual Installation Step-by-Step

If you prefer to install manually without the script:

----------

### 1. Open PowerShell

Go to the `LLaVA-Med` folder:
```bash
cd C:\Users\<USERNAME>\<Your_PROJECT_DIR>\medical-imaging-multi-task-vision-language-models\LLaVA-Med` 
```
----------

### 2. Create Conda Environment
```bash
conda create -n llava-med python=3.10  -y conda activate llava-med
```
----------

### 3. Install Python Dependencies

Upgrade pip:

```bash
pip install --upgrade pip
```
Install LLaVA-Med in editable mode:
```bash
pip install -e .
```
----------

### 4. Verify GPU

```bash
python -c  "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'No GPU detected')"
```
----------

### 5. Fix Windows Compatibility

Uninstall `bitsandbytes`:
```bash
pip uninstall bitsandbytes -y
```

Pin compatible package versions:
```bash
pip install "accelerate<0.27"  "transformers<4.39"` 
```
----------

### 6. Launch Inference

Open **three separate PowerShell windows**:

**Window 1 – Controller**:
```bash
python -m llava.serve.controller --host  0.0.0.0  --port  10000
```
**Window 2 – Model Worker**:

`python -m llava.serve.model_worker --controller http://localhost:10000  --port  40000  --worker http://localhost:40000  --model-path microsoft/llava-med-v1.5-mistral-7b  --multi-modal` 

**Window 3 – Web UI (Gradio)**:

```bash
hpython -m llava.serve.gradio_web_server --controller http://localhost:10000  --port  7860
```

Open your browser at:
- [http://localhost:7860](http://localhost:7860)

Upload medical images and start interacting with LLaVA-Med.

----------

### Notes

-   Ensure Conda is initialized in PowerShell before running commands.
-   GPU support requires NVIDIA drivers + CUDA installed correctly.
-   If you encounter issues with Hugging Face model access, login with:
```bash
huggingface-cli login
```
-   You can remove the environment later if needed:
 ```bash
conda deactivate
conda env remove -n llava-med
```
