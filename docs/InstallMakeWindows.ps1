<#
.SYNOPSIS
    Installs 'make' via winget (if missing) and adds it to the system PATH.
#>

# Check if 'make' is already available
$makeAvailable = (Get-Command make -ErrorAction SilentlyContinue) -ne $null

if ($makeAvailable) {
    Write-Host "'make' is already available in your PATH." -ForegroundColor Green
    Write-Host "Version info:" -ForegroundColor Cyan
    make --version
    exit 0
}

# If not, install via winget
Write-Host "'make' not found. Installing via winget..." -ForegroundColor Yellow
try {
    winget install --id GnuWin32.make --accept-package-agreements --accept-source-agreements
    Write-Host "'make' installed successfully." -ForegroundColor Green
} catch {
    Write-Host "Failed to install 'make' via winget." -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}

# Define the default GnuWin32 bin path
$gnuWinPath = "C:\Program Files (x86)\GnuWin32\bin"

# Check if the path exists
if (Test-Path $gnuWinPath) {
    # Check if the path is already in the system PATH
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    if ($currentPath -notlike "*$gnuWinPath*") {
        # Add to PATH
        [Environment]::SetEnvironmentVariable("Path", "$currentPath;$gnuWinPath", "Machine")
        Write-Host "Added GnuWin32 to system PATH." -ForegroundColor Green
    } else {
        Write-Host "GnuWin32 is already in the system PATH." -ForegroundColor Yellow
    }

    # Verify make is now available
    $makePath = Join-Path $gnuWinPath "make.exe"
    if (Test-Path $makePath) {
        Write-Host "`nVerification: 'make' is now available at $makePath" -ForegroundColor Green
        Write-Host "Restart your terminal and try 'make --version'." -ForegroundColor Cyan
    } else {
        Write-Host "`nError: 'make.exe' not found in $gnuWinPath" -ForegroundColor Red
    }
} else {
    Write-Host "`nError: GnuWin32 not found at $gnuWinPath" -ForegroundColor Red
    Write-Host "Please check the installation path or install manually." -ForegroundColor Cyan
}
