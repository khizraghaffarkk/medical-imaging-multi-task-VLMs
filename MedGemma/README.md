
# MedGemma Installation & Usage Guide (Windows)

This guide explains how to install and run **MedGemma** on **Windows**, using GPU acceleration if available.

You can install MedGemma in two ways:

**Option A:** Automatic installation using a PowerShell script  
**Option B:** Manual installation step-by-step

----------

### Quick Start (Download from This Repository)

If you have downloaded the following files from this repository:

-   `install_MedGemma.ps1`
-   `gui_inference_script_gpu.py`
-   `gui_inference_script_cpu.py`
-   `gui_compare_gpu.py`
-   `gui_compare_cpu.py`
-   `gui_ct_scans_cpu.py`    

The script will automatically create a conda environment, install Python packages, verify GPU availability, and allow you to run inference scripts interactively.

----------

### Project Structure

After downloading all files from this repository, your folder should look like this:

```plaintext
 MedGemma/
├── install_MedGemma.ps1        # PowerShell installation & launcher script
├── gui_inference_script_gpu.py  # Python script to analyze single CT image using GPU
├── gui_inference_script_cpu.py  # Python script to analyze single CT image using CPU
├── gui_compare_gpu.py           # Python script for longitudinal comparison using GPU
├── gui_compare_cpu.py           # Python script for longitudinal comparison using CPU
├── gui_ct_scans_cpu.py          # Python script to analyze CT scan and generate report
├── requirements.txt             # Optional: additional dependencies
├── README.md                    # This README file` 
```

----------

### Requirements

Before starting, make sure you have:

#### System & Software Requirements

-   Windows 10 / 11
-   Git installed
-   NVIDIA GPU (for GPU scripts)
-   CUDA driver installed
-   At least **20 GB RAM** (more recommended for large CT scans)
-   Miniconda / Anaconda installed
-   Python 3.10 environment


----------

## Option A: Install & Run MedGemma using PowerShell Script

This method automatically:

-   Creates a conda environment (`med-gemma`)
-   Installs PyTorch with CUDA (GPU support)
-   Installs required Python packages (`gradio`, `transformers`, `Pillow`, `numpy`, `scikit-image`, `pydicom`)
-   Runs the inference controller to select which task to run
    

----------

### 1. Save Script

Download the PowerShell script from this repository:

📄 `install_MedGemma.ps1`

----------

### 2. Run Script

Open **PowerShell** in the folder where the script is saved and run:
```bash
Set-ExecutionPolicy  -Scope  Process  -ExecutionPolicy Bypass
.\install_MedGemma.ps1
```    

----------

### 3. Select Inference Task

After running the script, select one of the following options:

1.  **Analyze single CT image** – GPU/CPU version available
2.  **Longitudinal comparison** (multiple scans over time) – GPU/CPU version available
3.  **Analyze CT scan to generate report** – CPU only
    
The script will automatically launch the corresponding Python script.

----------

## Option B: Manual Installation Step-by-Step (No Script)

If you prefer to install manually:

----------

### 1. Open PowerShell

Navigate to your working folder:
```bash
cd C:\Users\<USER_NAME>\Documents\MedGemma
```

----------

### 2. Create Conda Environment

```bash
conda create -n med-gemma2 python=3.10  -y 
conda activate med-gemma2
```

----------

### 3. Upgrade pip
```bash
python -m pip install --upgrade pip
```

----------

### 4. Install PyTorch with CUDA

`pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128` 

----------

### 5. Install Other Python Dependencies
```bash
pip install gradio transformers Pillow numpy scikit-image pydicom
```
----------

### 6. Verify GPU

Run:
```bash
python -c  "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'No GPU detected')"
```

----------

### 7. Run Inference Scripts

Run the script corresponding to your task:

- `python gui_inference_script_gpu.py # Single CT analysis using GPU`
- `python gui_inference_script_cpu.py # Single CT analysis using CPU`
- `python gui_compare_gpu.py # Longitudinal comparison using GPU` 
- `python gui_compare_cpu.py # Longitudinal comparison using CPU` 
- `python gui_ct_scans_cpu.py # Generate CT scan report (CPU only)` 

----------

### Notes

-   GPU support requires **NVIDIA drivers + CUDA** installed correctly.
-   Scripts `gui_inference_script_gpu.py` and `gui_compare_gpu.py` require GPU; CPU scripts work without GPU.
-   You can remove the conda environment after use:
```bash
conda deactivate
conda env remove -n med-gemma2
```
