# ================================
# MedGemma Setup and Inference Script
# ================================

# --- Step 0: Variables ---
$envName = "med-gemma"
$pythonVersion = "3.10"

# Detect script folder
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptDir
Write-Host "MedGemma folder at: $ScriptDir"

# --- Step 1: Create Conda environment if not exists ---
$envs = conda env list | Out-String
if ($envs -notmatch $envName) {
    Write-Host "Creating Conda environment '$envName'..."
    conda create -n $envName python=$pythonVersion -y
} else {
    Write-Host "Conda environment '$envName' already exists."
}

# --- Step 2: Activate environment ---
conda activate $envName

# --- Step 3: Upgrade pip ---
python -m pip install --upgrade pip

# --- Step 4: Install PyTorch with CUDA (if GPU available) ---
pip uninstall torch torchvision torchaudio -y
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

# --- Step 5: Install all other Python dependencies ---
pip install gradio transformers Pillow numpy scikit-image pydicom

# --- Step 6: Install additional dependencies from requirements.txt if exists ---
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
}

# --- Step 7: Verify GPU availability ---
$gpuCheck = python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'No GPU detected')"
Write-Host "`nGPU Check:"
Write-Host $gpuCheck

# --- Step 8: Inference Controller ---
do {
    Write-Host "`nSelect which inference to run:"
    Write-Host "1: Analyze single CT image"
    Write-Host "2: Longitudinal comparison (multiple scans over time)"
    Write-Host "3: Analyze CT scan to generate report"
    $choice = Read-Host "Enter 1, 2, or 3"

    switch ($choice) {
        "1" {
            if ($gpuCheck -match "True") {
                $gpuChoice = Read-Host "GPU detected. Run on GPU? (y/n)"
                if ($gpuChoice -eq "y") {
                    $scriptName = "gui_inference_script_gpu.py"
                } else {
                    $scriptName = "gui_inference_script_cpu.py"
                }
            } else {
                Write-Host "No GPU detected. Using CPU version."
                $scriptName = "gui_inference_script_cpu.py"
            }
        }
        "2" {
            if ($gpuCheck -match "True") {
                $gpuChoice = Read-Host "GPU detected. Run on GPU? (y/n)"
                if ($gpuChoice -eq "y") {
                    $scriptName = "gui_compare_gpu.py"
                } else {
                    $scriptName = "gui_compare_cpu.py"
                }
            } else {
                Write-Host "No GPU detected. Using CPU version."
                $scriptName = "gui_compare_cpu.py"
            }
        }
        "3" {
            Write-Host "This script runs on CPU only."
            $scriptName = "gui_ct_scans_cpu.py"
        }
        default {
            Write-Host "Invalid choice. Try again."
            continue
        }
    }

    $runCmd = "cd `"$ScriptDir`"; conda activate $envName; python `"$scriptName`""
    Write-Host "`nRunning $scriptName..."
    Start-Process powershell "-NoExit -Command $runCmd"

    $again = Read-Host "`nDo you want to run another inference? (y/n)"
} while ($again -eq "y")

Write-Host "`nAll done. Exiting script."
