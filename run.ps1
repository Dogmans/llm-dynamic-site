# LLM Dynamic Site - Setup and Run Script
# This script handles virtual environment setup, dependency installation, and application startup

param(
    [switch]$Setup,
    [switch]$Start,
    [switch]$Dev,
    [switch]$Clean,
    [switch]$Help
)

$ErrorActionPreference = "Stop"

# Configuration
$VenvPath = ".venv"
$ProjectName = "LLM Dynamic Site"
$ActivateScript = "$VenvPath\Scripts\Activate.ps1"

function Show-Help {
    Write-Host "`n$ProjectName - PowerShell Management Script`n" -ForegroundColor Cyan
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\run.ps1 -Setup     # Initial setup: create venv, install dependencies"
    Write-Host "  .\run.ps1 -Start     # Start the application (setup if needed)"
    Write-Host "  .\run.ps1 -Dev       # Start with development tools installed"
    Write-Host "  .\run.ps1 -Clean     # Clean up virtual environment"
    Write-Host "  .\run.ps1 -Help      # Show this help message"
    Write-Host "`nExamples:" -ForegroundColor Yellow
    Write-Host "  .\run.ps1 -Setup     # First time setup"
    Write-Host "  .\run.ps1 -Start     # Daily use"
    Write-Host "  .\run.ps1 -Dev       # Development with pytest, black, etc."
    Write-Host ""
}

function Test-VenvExists {
    return (Test-Path $VenvPath) -and (Test-Path $ActivateScript)
}

function New-VirtualEnvironment {
    Write-Host "Creating virtual environment..." -ForegroundColor Green
    
    if (Test-VenvExists) {
        Write-Host "Virtual environment already exists at $VenvPath" -ForegroundColor Yellow
        return
    }
    
    python -m venv $VenvPath
    
    if (-not (Test-VenvExists)) {
        Write-Error "Failed to create virtual environment"
    }
    
    Write-Host "Virtual environment created successfully" -ForegroundColor Green
}

function Install-Dependencies {
    param([switch]$DevDependencies)
    
    Write-Host "Installing dependencies..." -ForegroundColor Green
    
    # Activate virtual environment
    & $ActivateScript
    
    # Upgrade pip
    Write-Host "Upgrading pip..." -ForegroundColor Blue
    python -m pip install --upgrade pip
    
    # Install setuptools first to avoid build issues
    Write-Host "Installing setuptools..." -ForegroundColor Blue
    python -m pip install "setuptools>=61.0" wheel
    
    # Install project dependencies
    Write-Host "Installing core dependencies..." -ForegroundColor Blue
    python -m pip install "fastapi[standard]>=0.118.0" "smolagents>=1.22.0" "pymemcache>=4.0.0" "transformers>=4.40.0" "torch>=2.0.0"
    
    if ($DevDependencies) {
        Write-Host "Installing development dependencies..." -ForegroundColor Blue
        python -m pip install "pytest>=7.0.0" "pytest-asyncio>=0.21.0" "httpx>=0.24.0" "black>=23.0.0" "isort>=5.12.0" "flake8>=6.0.0"
    }
    
    # Try to install in editable mode (may fail due to network issues)
    Write-Host "Attempting editable install..." -ForegroundColor Blue
    try {
        if ($DevDependencies) {
            pip install -e ".[dev]"
        } else {
            pip install -e .
        }
        Write-Host "Editable install successful" -ForegroundColor Green
    } catch {
        Write-Host "Editable install failed, but core dependencies are installed" -ForegroundColor Yellow
        Write-Host "You can run the app directly with: python -m app.main" -ForegroundColor Yellow
    }
    
    Write-Host "Dependencies installation completed" -ForegroundColor Green
}

function Start-Application {
    Write-Host "Starting $ProjectName..." -ForegroundColor Green
    
    # Check if setup is needed
    if (-not (Test-VenvExists)) {
        Write-Host "Virtual environment not found. Running setup..." -ForegroundColor Yellow
        Setup-Project
    }
    
    # Activate virtual environment
    & $ActivateScript
    
    # Check if Redis is running (optional check)
    Write-Host "Checking prerequisites..." -ForegroundColor Blue
    Write-Host "Note: Redis is optional - will use in-memory cache if Redis unavailable" -ForegroundColor Yellow
    
    # Start the application
    Write-Host "Launching application at http://localhost:8000" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
    Write-Host ""
    
    try {
        llm-site
    } catch {
        Write-Host "Failed to start using 'llm-site' command. Trying direct execution..." -ForegroundColor Yellow
        python -m app.main
    }
}

function Setup-Project {
    param([switch]$DevDependencies)
    
    Write-Host "`n=== $ProjectName Setup ===" -ForegroundColor Cyan
    Write-Host "Setting up development environment...`n" -ForegroundColor White
    
    # Check Python installation
    try {
        $pythonVersion = python --version 2>$null
        Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Error "Python not found. Please install Python 3.9 or higher."
    }
    
    # Create virtual environment
    New-VirtualEnvironment
    
    # Install dependencies
    Install-Dependencies -DevDependencies:$DevDependencies
    
    Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
    Write-Host "You can now start the application with: .\run.ps1 -Start" -ForegroundColor Cyan
    Write-Host ""
}

function Remove-VirtualEnvironment {
    Write-Host "Cleaning up virtual environment..." -ForegroundColor Yellow
    
    if (Test-VenvExists) {
        Remove-Item -Recurse -Force $VenvPath
        Write-Host "Virtual environment removed" -ForegroundColor Green
    } else {
        Write-Host "No virtual environment found to clean" -ForegroundColor Yellow
    }
}

# Main script logic
try {
    if ($Help -or ($args.Count -eq 0 -and -not $Setup -and -not $Start -and -not $Dev -and -not $Clean)) {
        Show-Help
        exit 0
    }
    
    if ($Clean) {
        Remove-VirtualEnvironment
        exit 0
    }
    
    if ($Setup) {
        Setup-Project
        exit 0
    }
    
    if ($Dev) {
        if (-not (Test-VenvExists)) {
            Setup-Project -DevDependencies
        }
        Start-Application
        exit 0
    }
    
    if ($Start) {
        Start-Application
        exit 0
    }
    
} catch {
    Write-Host "`nError: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Run '.\run.ps1 -Help' for usage information" -ForegroundColor Yellow
    exit 1
}