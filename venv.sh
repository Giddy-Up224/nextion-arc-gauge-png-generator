#!/bin/bash
# This script creates a virtual environment and installs the required packages.
python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt