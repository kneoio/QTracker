#!/bin/bash

# Ensure script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

# Check for the -d flag (daemon mode)
DAEMON_MODE=false
while getopts "d" option; do
  case $option in
    d) DAEMON_MODE=true ;;
    *) echo "Usage: $0 [-d] (run as a service)"; exit 1 ;;
  esac
done

# Debugging output to verify if daemon mode is recognized
echo "Daemon mode: $DAEMON_MODE"

# Update and install core utilities
echo "Updating package list and installing core utilities..."
apt update && apt install -y python3 python3-venv git

# Stop Telegram Bot service if running
echo "Stopping Telegram Bot service if it exists..."
systemctl stop telegrambot || true

# Clone/update the Telegram bot project
REPO_DIR="/home/telegrambot"
if [ -d "$REPO_DIR" ]; then
  echo "Updating Telegram bot project from GitHub..."
  git -C $REPO_DIR pull origin master
else
  echo "Cloning Telegram bot project from GitHub..."
  git clone https://github.com/your-repo/telegram-bot.git $REPO_DIR
fi

# Navigate to the bot's directory
cd $REPO_DIR

# Create a virtual environment and install dependencies
if [ ! -d "$REPO_DIR/venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

echo "Activating virtual environment and installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Option to run as service or in the current terminal
if [ "$DAEMON_MODE" = true ]; then
  echo "Setting up to run as a systemd service..."

  # Create systemd service file
  SERVICE_FILE="/etc/systemd/system/telegrambot.service"
  echo "Creating systemd service for Telegram Bot..."
  cat << EOF > $SERVICE_FILE
[Unit]
Description=Telegram Bot Service
After=network.target

[Service]
User=aida
WorkingDirectory=$REPO_DIR
ExecStart=$REPO_DIR/venv/bin/python $REPO_DIR/your_bot_script.py
Environment="API_TOKEN=your_token"
Environment="CLAUDE_API_ENDPOINT=your_endpoint"
Environment="CLAUDE_API_KEY=your_key"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

  # Reload systemd and enable/start the service
  echo "Reloading systemd daemon and starting Telegram Bot service..."
  systemctl daemon-reload
  systemctl enable telegrambot
  systemctl start telegrambot

  echo "Service is running as a daemon!"
else
  echo "Running Telegram Bot in the current terminal..."
  $REPO_DIR/venv/bin/python $REPO_DIR/your_bot_script.py
fi
