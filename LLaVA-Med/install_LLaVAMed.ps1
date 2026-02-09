# ================================
# LLaVA-Med Inference Setup Script
# ================================

# --- Step 0: Variables ---
$envName = "llava-med2"
$pythonVersion = "3.10"
$modelName = "microsoft/llava-med-v1.5-mistral-7b"

# Detect script folder (so script can run from anywhere)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptDir

# --- Step 1: Repo folder (current folder) ---
$repoFolder = $ScriptDir

Write-Host "Using LLaVA-Med folder at: $repoFolder"

# --- Step 2: Create Conda environment if not exists ---
$envs = conda env list | Out-String
if ($envs -notmatch $envName) {
    conda create -n $envName python=$pythonVersion -y
} else {
    Write-Host "Conda environment '$envName' already exists."
}

# --- Step 3: Activate environment ---
conda activate $envName

# --- Step 4: Upgrade pip and install repo in editable mode ---
python -m pip install --upgrade pip

# Install torch first (CUDA)
pip uninstall torch torchvision torchaudio -y
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

# Then install repo
pip install -e .

# --- Step 5: Verify GPU availability ---
$gpuCheck = python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'No GPU detected')"
Write-Host "`nGPU Check:"
Write-Host $gpuCheck

# --- Step 6: Uninstall bitsandbytes (Windows workaround) ---
pip uninstall bitsandbytes -y

# --- Step 7: Pin compatible package versions ---
pip install "accelerate<0.27" "transformers<4.39"
# --- Step 8: Auto Launch Inference Services ---
Write-Host "`nStarting LLaVA-Med Inference..."
Write-Host "This script will automatically open THREE separate PowerShell windows:"
Write-Host "  (1) Controller"
Write-Host "  (2) Model Worker"
Write-Host "  (3) Gradio Web UI"
Write-Host "`nPlease wait until all services finish loading..."
Write-Host "Then open your browser at: http://localhost:7860"
Write-Host "Upload medical images and ask questions to the LLaVA-Med model or use default images."

$controllerCmd = "cd `"$ScriptDir`"; conda activate $envName; python -m llava.serve.controller --host 0.0.0.0 --port 10000"
$workerCmd = "cd `"$ScriptDir`"; conda activate $envName; python -m llava.serve.model_worker --controller http://localhost:10000 --port 40000 --worker http://localhost:40000 --model-path $modelName --multi-modal"
$gradioCmd = "cd `"$ScriptDir`"; conda activate $envName; python -m llava.serve.gradio_web_server --controller http://localhost:10000 --port 7860"

Start-Process powershell "-NoExit -Command $controllerCmd"
Start-Process powershell "-NoExit -Command $workerCmd"
Start-Process powershell "-NoExit -Command $gradioCmd"
