#!/bin/bash

# Navigate to the QTracker directory
REPO_DIR="QTracker"
if [ ! -d "$REPO_DIR" ]; then
  echo "Error: QTracker directory not found. Please ensure the repository is cloned."
  exit 1
fi

cd "$REPO_DIR" || exit 1

# Check if the virtual environment exists
if [ ! -d "venv" ]; then
  echo "Error: Python virtual environment not found. Please set up the environment first."
  exit 1
fi

# Activate the virtual environment
source venv/bin/activate

# Run the QTracker application
python main.py

# Deactivate the virtual environment after the app exits
deactivate
