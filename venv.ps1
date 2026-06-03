#!/bin/bash
# This script creates a virtual environment and installs the required packages.
python.exe -m venv venv
venv/Scripts/Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt