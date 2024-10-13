#!/bin/bash

# Ensure script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

# Variables
REPO_URL="https://github.com/kneoio/QTracker.git"  # Public GitHub repo URL
REPO_DIR="QTracker"
ENV_FILE="$REPO_DIR/.env"
PYTHON_VERSION="python3.11"

# Function to check and install missing dependencies
install_dependencies() {
  echo "Installing core utilities and Python..."
  apt update && apt install -y $PYTHON_VERSION $PYTHON_VERSION-venv git || {
    echo "Failed to install dependencies."
    exit 1
  }
}

# Clone or pull the latest code from the repository
deploy_repository() {
  # Check if the repository directory exists
  if [ -d "$REPO_DIR/.git" ]; then
    echo "QTracker repository found. Pulling latest changes..."
    cd "$REPO_DIR" || exit
    git pull origin master || {
      echo "Failed to pull latest changes."
      exit 1
    }
  else
    echo "Cloning QTracker repository..."
    git clone $REPO_URL || {
      echo "Failed to clone the repository."
      exit 1
    }
    cd "$REPO_DIR" || exit
  fi
}

# Create virtual environment and install dependencies
setup_python_env() {
  echo "Setting up Python virtual environment..."
  if [ ! -d "venv" ]; then
    $PYTHON_VERSION -m venv venv || {
      echo "Failed to create virtual environment."
      exit 1
    }
  fi

  echo "Activating virtual environment and installing dependencies..."
  source venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt || {
    echo "Failed to install Python dependencies."
    exit 1
  }
  deactivate
}

# Verify .env file exists (no creation, just check)
verify_env_file() {
  if [ ! -f "$ENV_FILE" ]; then
    echo "Error: .env file not found in $REPO_DIR."
    exit 1
  else
    echo ".env file exists, using it for environment variables."
  fi
}

# Main process
main() {
  install_dependencies
  deploy_repository
  setup_python_env
  verify_env_file  # Check if .env file exists
}

main "$@"
