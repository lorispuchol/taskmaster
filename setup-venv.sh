#!/bin/bash

# Create a virtual environment
python3 -m venv taskmaster-venv

# Activate the virtual environment
source taskmaster-venv/bin/activate

# Install the required packages
pip install -r requirements.txt