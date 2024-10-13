#!/bin/bash

# Ensure script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

# Variables
REPO_URL="https://github.com/kneoio/QTracker.git"  # Public GitHub repo URL
REPO_DIR="/home/qtracker/QTracker"
ENV_FILE="/home/qtracker/.env"  # Update to match the location of your .env file
PYTHON_VERSION="python3.11"
DAEMON_MODE=false

# Parse command line options
while getopts "d" opt; do
  case $opt in
    d)
      DAEMON_MODE=true
      ;;
    *)
      echo "Usage: $0 [-d] (run as daemon)"
      exit 1
      ;;
  esac
done

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
    git clone $REPO_URL "$REPO_DIR" || {
      echo "Failed to clone the repository."
      exit 1
    }
    cd "$REPO_DIR" || exit
  fi
}

# Create virtual environment and install dependencies
setup_python_env() {
  echo "Setting up Python virtual environment..."
  if [ ! -d "$REPO_DIR/venv" ]; then
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
    echo "Error: .env file not found at $ENV_FILE."
    exit 1
  else
    echo ".env file exists, using it for environment variables."
  fi
}

# Function to create and run the service as a daemon using systemd
run_as_daemon() {
  SERVICE_FILE="/etc/systemd/system/qtracker.service"

  echo "Creating systemd service for QTracker..."
  cat << EOF > $SERVICE_FILE
[Unit]
Description=QTracker Python Application
After=network.target

[Service]
User=aida
WorkingDirectory=$REPO_DIR
EnvironmentFile=$ENV_FILE
ExecStart=$REPO_DIR/venv/bin/python $REPO_DIR/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

  # Reload systemd and enable/start the service
  echo "Reloading systemd daemon and starting QTracker service..."
  systemctl daemon-reload
  systemctl enable qtracker
  systemctl start qtracker

  echo "QTracker is running as a systemd service!"
}

# Main process
main() {
  install_dependencies
  deploy_repository
  setup_python_env
  verify_env_file  # Check if .env file exists

  if [ "$DAEMON_MODE" = true ]; then
    run_as_daemon
  else
    echo "Starting QTracker manually..."
    set -a
    source $ENV_FILE
    set +a
    $REPO_DIR/venv/bin/python $REPO_DIR/main.py
  fi
}

main "$@"
