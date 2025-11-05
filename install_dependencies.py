#!/usr/bin/env python3
"""
Installation script for Kelantan Flood Prediction Webapp
Handles Python 3.12.3 compatibility and dependency installation
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description=""):
    """Run a command and handle errors"""
    print(f"{'='*50}")
    print(f"Running: {description or command}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Warnings:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major != 3 or version.minor < 8:
        print("ERROR: Python 3.8+ is required")
        return False
    
    if version.minor >= 12:
        print("✅ Python 3.12+ detected - using compatible dependencies")
    
    return True

def install_python_dependencies():
    """Install Python dependencies with compatibility handling"""
    print("Installing Python dependencies...")
    
    # First, upgrade pip
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install core dependencies first
    core_deps = [
        "fastapi>=0.104.1,<0.110.0",
        "uvicorn[standard]>=0.24.0,<0.30.0",
        "pydantic>=2.5.0,<3.0.0",
        "pydantic-settings>=2.1.0,<3.0.0",
    ]
    
    for dep in core_deps:
        if not run_command(f"{sys.executable} -m pip install '{dep}'", f"Installing {dep}"):
            print(f"Warning: Failed to install {dep}")
    
    # Install data science dependencies
    data_deps = [
        "pandas>=2.1.3,<2.3.0",
        "numpy>=1.26.0,<2.0.0",
        "scikit-learn>=1.3.2,<1.5.0",
        "joblib>=1.3.2,<1.5.0",
    ]
    
    for dep in data_deps:
        if not run_command(f"{sys.executable} -m pip install '{dep}'", f"Installing {dep}"):
            print(f"Warning: Failed to install {dep}")
    
    # Install other dependencies
    other_deps = [
        "requests>=2.31.0,<3.0.0",
        "aiohttp>=3.9.1,<4.0.0",
        "python-multipart>=0.0.6,<0.1.0",
        "sqlalchemy>=2.0.23,<2.1.0",
        "python-dotenv>=1.0.0,<2.0.0",
        "httpx>=0.25.2,<0.28.0",
    ]
    
    for dep in other_deps:
        if not run_command(f"{sys.executable} -m pip install '{dep}'", f"Installing {dep}"):
            print(f"Warning: Failed to install {dep}")
    
    # Try to install geospatial dependencies (may fail on some systems)
    geo_deps = [
        "shapely>=2.0.2,<3.0.0",
        "folium>=0.15.0,<0.16.0",
    ]
    
    for dep in geo_deps:
        if not run_command(f"{sys.executable} -m pip install '{dep}'", f"Installing {dep}"):
            print(f"Warning: Failed to install {dep} - geospatial features may be limited")
    
    # Try to install visualization dependencies
    viz_deps = [
        "plotly>=5.17.0,<6.0.0",
        "matplotlib>=3.8.2,<4.0.0",
        "seaborn>=0.13.0,<0.14.0",
    ]
    
    for dep in viz_deps:
        if not run_command(f"{sys.executable} -m pip install '{dep}'", f"Installing {dep}"):
            print(f"Warning: Failed to install {dep} - some visualizations may not work")
    
    return True

def install_node_dependencies():
    """Install Node.js dependencies"""
    print("Installing Node.js dependencies...")
    
    # Check if npm is available
    try:
        subprocess.run(["npm", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Warning: npm not found. Please install Node.js to run the frontend.")
        return False
    
    return run_command("npm install", "Installing Node.js packages")

def create_directories():
    """Create necessary directories"""
    directories = [
        "backend/models",
        "backend/config", 
        "backend/services",
        "data/climada",
        "data/results",
        "models"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def main():
    """Main installation function"""
    print("🌊 Kelantan Flood Prediction Webapp - Installation Script")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("❌ Failed to install some Python dependencies")
        print("The application may still work with reduced functionality")
    else:
        print("✅ Python dependencies installed successfully")
    
    # Install Node.js dependencies
    if install_node_dependencies():
        print("✅ Node.js dependencies installed successfully")
    else:
        print("❌ Failed to install Node.js dependencies")
        print("Frontend may not work properly")
    
    print("\n" + "=" * 60)
    print("🎉 Installation completed!")
    print("\nTo run the application:")
    print("1. Backend: cd backend && python main.py")
    print("2. Frontend: npm run dev")
    print("\nAccess the app at: http://localhost:12000")
    print("API documentation: http://localhost:12001/docs")

if __name__ == "__main__":
    main()