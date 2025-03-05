#!/bin/bash

# Create a virtual environment
python3 -m venv taskmaster-venv

# Update pip and setuptools
# pip3 install -U pip setuptools

# Activate the virtual environment
source taskmaster-venv/bin/activate

# Install the required packages
pip3 install -r requirements.txt