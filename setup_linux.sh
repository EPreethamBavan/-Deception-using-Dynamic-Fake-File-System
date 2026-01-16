#!/bin/bash

# Configuration - STEALTH MODE
APP_DIR="/opt/sys_integrity"
SRC_DIR="$APP_DIR/src"
CONFIG_DIR="$APP_DIR/config"
LOG_DIR="$APP_DIR/logs"
VENV_DIR="$APP_DIR/venv"
SERVICE_NAME="sys-integrity-daemon"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

echo "[*] Starting System Integrity Service Installation..."

# 1. Create Directories (Stealth paths)
echo "[+] Creating Directory Structure at $APP_DIR..."
mkdir -p "$SRC_DIR"
mkdir -p "$CONFIG_DIR"
mkdir -p "$LOG_DIR"

# Copy Source Files
echo "[+] Installing Source Code..."
cp sys_core.py LLM_Provider.py ContentManager.py StrategyManager.py ActiveDefense.py "$SRC_DIR/"

# Copy Config if present
if [ -f ".env" ]; then
    echo "[+] Deploying bundled configuration..."
    cp ".env" "$CONFIG_DIR/.env"
fi

# 2. Setup Virtual Environment
echo "[+] Setting up Python Virtual Environment..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo "    - venv created."
else
    echo "    - venv exists."
fi

# 3. Upgrade Pip & Install Dependencies
"$VENV_DIR/bin/pip" install --upgrade pip
echo "[+] Installing Dependencies..."
"$VENV_DIR/bin/pip" install google-generativeai

# 4. Create Systemd Service (Disguised)
echo "[+] Creating Stealth Systemd Service ($SERVICE_NAME)..."
cat <<EOF > "$SERVICE_FILE"
[Unit]
Description=System Integrity Verification Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$APP_DIR
Environment="GEMINI_API_KEY=YOUR_KEY_HERE"
Environment="CONFIG_DIR=$CONFIG_DIR"
# We deliberately name the process something generic in the command line if possible, 
# but for now we run the orchestrator (sys_core). 
ExecStart=$VENV_DIR/bin/python -u src/sys_core.py --strategy-hybrid --llm
Restart=always
RestartSec=10
StandardOutput=append:$LOG_DIR/sys_monitor.log
StandardError=append:$LOG_DIR/sys_error.log

[Install]
WantedBy=multi-user.target
EOF

# 5. Reload Systemd
echo "[+] Reloading Systemd..."
systemctl daemon-reload

echo "[*] Installation Complete!"
echo "------------------------------------------------"
echo "NEXT STEPS (Stealth Operations):"
echo "1. Copy your python files to $SRC_DIR"
echo "2. Edit $SERVICE_FILE to add your API Key."
echo "3. Run: systemctl enable --now $SERVICE_NAME"
echo "------------------------------------------------"
