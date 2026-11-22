# Smart PC-Scanning Installer for AI Video Editing Skills & Pipeline (Windows)
$ErrorActionPreference = "Stop"
Write-Host "=== AI Video Editing Skills - Smart PC Scanner ===" -ForegroundColor Cyan

# 1. Scan existing tools (never reinstall what is already installed!)
function Check-Tool($name, $wingetId) {
    $cmd = Get-Command $name -ErrorAction SilentlyContinue
    if ($cmd) {
        Write-Host "[OK] $name already installed: $($cmd.Source)" -ForegroundColor Green
        return $true
    }
    Write-Host "[MISSING] $name not found." -ForegroundColor Yellow
    if ($wingetId) {
        $ans = Read-Host "Install $name via winget? [Y/n]"
        if ($ans -eq "" -or $ans -match "^[Yy]") {
            winget install --id $wingetId -e --accept-package-agreements --accept-source-agreements
            return $true
        }
    }
    return $false
}

Check-Tool "python" "Python.Python.3.12" | Out-Null
Check-Tool "ffmpeg" "Gyan.FFmpeg.Essentials" | Out-Null
Check-Tool "git" "Git.Git" | Out-Null

# 2. GPU Scan
Write-Host "`n--- Hardware / GPU Scan ---" -ForegroundColor Cyan
$gpu = Get-Command nvidia-smi -ErrorAction SilentlyContinue
if ($gpu) {
    nvidia-smi --query-gpu=name,memory.total,compute_cap --format=csv,noheader
    Write-Host "[INFO] Note: PyTorch CUDA acceleration for OmniVoice requires 6GB+ VRAM and Compute Capability >= 7.0 (GTX 16xx / RTX series)." -ForegroundColor DarkCyan
} else {
    Write-Host "[INFO] No NVIDIA GPU detected (CPU mode works great with edge-tts!)." -ForegroundColor Yellow
}

# 3. Create isolated .venv & install Python dependencies
Write-Host "`n--- Python Environment (.venv) ---" -ForegroundColor Cyan
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    python -m venv .venv
}
& ".venv\Scripts\pip.exe" install -q --upgrade pip
& ".venv\Scripts\pip.exe" install -q -r requirements.txt
Write-Host "[OK] Python packages installed in .venv" -ForegroundColor Green

# 4. Install Global Antigravity Skills
$skillsTarget = Join-Path $env:USERPROFILE ".gemini\config\skills"
New-Item -ItemType Directory -Force -Path $skillsTarget | Out-Null
Copy-Item -Path "skills\*" -Destination $skillsTarget -Recurse -Force
Write-Host "[OK] All 9 video skills installed to $skillsTarget" -ForegroundColor Green

# 5. Optional OmniVoice Voice Cloning Setup
Write-Host "`n--- Optional: Voice Cloning (OmniVoice) ---" -ForegroundColor Cyan
$vc = Read-Host "Do you want to install OmniVoice local voice cloning (~3GB models)? [y/N]"
if ($vc -match "^[Yy]") {
    & ".venv\Scripts\pip.exe" install -q omnivoice torchaudio
    Write-Host "[OK] OmniVoice package installed! Models will download on first run." -ForegroundColor Green
} else {
    Write-Host "[SKIP] Using fast cloud edge-tts mode (zero-glitch Hindi narration)." -ForegroundColor DarkGray
}

Write-Host "`n=== Setup Complete! ===" -ForegroundColor Green
Write-Host "Next: Copy .env.example to .env if you want Telegram delivery, and run any script with .venv\Scripts\python.exe!"
