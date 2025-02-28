#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Run the Python script
python github_repo_cleaner.py

# Optionally deactivate the virtual environment
deactivate
