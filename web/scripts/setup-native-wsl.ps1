param(
    [ValidateSet("basic","libxc","openmp_libxc")]
    [string]$BuildMode = "basic"
)

$ErrorActionPreference = "Stop"

$repo = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$repoPath = $repo.Path
$wslRepo = "/mnt/" + $repoPath.Substring(0,1).ToLower() + $repoPath.Substring(2).Replace("\","/")

Write-Host "X2DHF native setup for Windows + WSL"
Write-Host "Repository: $repoPath"

$wsl = Get-Command wsl.exe -ErrorAction SilentlyContinue
if (-not $wsl) {
    Write-Host "WSL is not available on this Windows host."
    Write-Host "Open Administrator PowerShell and run:"
    Write-Host "  wsl --install --no-distribution"
    Write-Host "Restart Windows if prompted, then run:"
    Write-Host "  wsl --install -d Ubuntu"
    Write-Host "Launch Ubuntu once from Start Menu, create the Linux user, then run this script again."
    exit 1
}

$status = (& wsl.exe --status 2>&1) -join "`n"
if ($status -match "Virtual Machine Platform|virtualization|not supported|BIOS") {
    Write-Host "WSL is present, but Windows reports that required platform support is not ready."
    Write-Host $status
    Write-Host ""
    Write-Host "Open Administrator PowerShell and run:"
    Write-Host "  wsl --install --no-distribution"
    Write-Host "Restart Windows if prompted. If Windows still reports virtualization support errors, enable CPU virtualization in BIOS/UEFI."
    Write-Host "After that, install Ubuntu with:"
    Write-Host "  wsl --install -d Ubuntu"
    exit 1
}

$distros = (& wsl.exe -l -q) -join ""
if ([string]::IsNullOrWhiteSpace($distros)) {
    Write-Host "WSL has no Ubuntu distribution yet."
    Write-Host "Open Administrator PowerShell and run:"
    Write-Host "  wsl --install -d Ubuntu"
    Write-Host "Launch Ubuntu once from Start Menu, create the Linux user, then run this script again."
    exit 1
}

$packages = "build-essential gfortran cmake make gcc g++ gawk bc libblas-dev liblapack-dev wget ca-certificates"
Write-Host "Installing Linux dependencies..."
wsl.exe -u root bash -lc "apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y $packages"

$buildCommand = "./x2dhfctl -b"
if ($BuildMode -eq "libxc") {
    $buildCommand = "./x2dhfctl -L && ./x2dhfctl -b -l"
}
if ($BuildMode -eq "openmp_libxc") {
    $buildCommand = "./x2dhfctl -L && ./x2dhfctl -b -l -o"
}

Write-Host "Building native X2DHF: $BuildMode"
wsl.exe bash -lc "cd '$wslRepo' && chmod +x x2dhfctl bin/xhf bin/testctl && $buildCommand"

Write-Host "Native X2DHF setup complete."
Write-Host "Run the web app from the repository root:"
Write-Host "  .\web\backend\.venv\Scripts\Activate.ps1; python manage.py runserver"
