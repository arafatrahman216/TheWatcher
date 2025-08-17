#!/bin/bash
# Setup script for backend installation

set -e

cd "$(dirname "$0")/backend"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
  python3 -m venv venv
  echo "Virtual environment created."
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

echo "Dependencies installed."

# Copy .env.example to .env if .env does not exist
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo ".env file created from .env.example."
fi

echo "Backend setup complete."
