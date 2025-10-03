#!/usr/bin/env python3
"""
Setup script for LLM Dynamic Site development environment.

This script creates a Python virtual environment and installs dependencies.
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False


def main():
    """Set up the development environment."""
    print("🚀 Setting up LLM Dynamic Site development environment...")
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Create virtual environment
    venv_path = Path(".venv")
    if not venv_path.exists():
        if not run_command("python -m venv .venv", "Creating virtual environment"):
            sys.exit(1)
    else:
        print("✅ Virtual environment already exists")
    
    # Determine activation script based on OS
    if os.name == 'nt':  # Windows
        activate_script = ".venv\\Scripts\\activate"
        pip_cmd = ".venv\\Scripts\\pip"
    else:  # Unix-like
        activate_script = "source .venv/bin/activate"
        pip_cmd = ".venv/bin/pip"
    
    print(f"Virtual environment created at: {venv_path.absolute()}")
    
    # Upgrade pip
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip"):
        sys.exit(1)
    
    # Install main dependencies
    if not run_command(f"{pip_cmd} install -e .", "Installing main dependencies"):
        sys.exit(1)
    
    # Install development dependencies
    if not run_command(f"{pip_cmd} install -e \".[dev]\"", "Installing development dependencies"):
        sys.exit(1)
    
    print("\\n🎉 Development environment setup complete!")
    print("\\nNext steps:")
    print(f"1. Activate the virtual environment:")
    if os.name == 'nt':
        print("   .venv\\Scripts\\activate")
    else:
        print("   source .venv/bin/activate")
    
    print("\\n2. Install and start Memcached:")
    print("   Windows: Download from https://memcached.org/downloads")
    print("   Linux: sudo apt-get install memcached && systemctl start memcached")
    print("   Mac: brew install memcached && brew services start memcached")
    
    print("\\n3. Run the application:")
    print("   fastapi dev app/main.py")
    
    print("\\n4. Visit http://localhost:8000/about/ to see the demo")


if __name__ == "__main__":
    main()