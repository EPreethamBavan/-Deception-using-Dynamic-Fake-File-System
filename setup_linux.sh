#!/bin/bash
#
# Deception Engine - Linux Deployment Script
# Research Paper: "Deception using Dynamic Fake File System"
#
# This script installs the deception engine as a systemd service
# with stealth naming to avoid detection by attackers.
#

set -e  # Exit on error

# ============================================
# Configuration - Stealth Mode Naming
# ============================================
APP_DIR="/opt/sys_integrity"
SRC_DIR="$APP_DIR/src"
CONFIG_DIR="$APP_DIR/config"
LOG_DIR="$APP_DIR/logs"
VENV_DIR="$APP_DIR/venv"
SERVICE_NAME="sys-integrity-daemon"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================
# Helper Functions
# ============================================
log_info() {
    echo -e "${GREEN}[+]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (sudo)"
        exit 1
    fi
}

# ============================================
# Pre-flight Checks
# ============================================
preflight_checks() {
    log_info "Running pre-flight checks..."

    # Check Python 3
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed. Please install it first."
        exit 1
    fi

    # Check pip/venv
    if ! python3 -m venv --help &> /dev/null; then
        log_warn "python3-venv not found. Attempting to install..."
        apt-get update && apt-get install -y python3-venv python3-pip
    fi

    # Check git (needed for fake repos)
    if ! command -v git &> /dev/null; then
        log_warn "Git not installed. Installing..."
        apt-get update && apt-get install -y git
    fi

    log_info "Pre-flight checks passed."
}

# ============================================
# Create Directory Structure
# ============================================
create_directories() {
    log_info "Creating directory structure at $APP_DIR..."

    mkdir -p "$SRC_DIR"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$LOG_DIR"

    # Create persona home directories
    log_info "Creating persona home directories..."
    mkdir -p /home/dev_alice
    mkdir -p /home/sys_bob
    mkdir -p /var/lib/jenkins

    # Set permissions
    chmod 755 "$APP_DIR"
    chmod 755 "$SRC_DIR"
    chmod 700 "$CONFIG_DIR"  # Restrict config access
    chmod 755 "$LOG_DIR"
}

# ============================================
# Install Source Code
# ============================================
install_source() {
    log_info "Installing source code to $SRC_DIR..."

    # Core Python files
    local src_files=(
        "sys_core.py"
        "LLM_Provider.py"
        "ContentManager.py"
        "StrategyManager.py"
        "ActiveDefense.py"
        "AntiFingerprint.py"
        "UserArtifactGenerator.py"
        "PromptEngine.py"
    )

    for file in "${src_files[@]}"; do
        if [[ -f "$file" ]]; then
            cp "$file" "$SRC_DIR/"
            log_info "  - Copied $file"
        else
            log_error "Source file not found: $file"
            exit 1
        fi
    done

    # Copy tests directory
    if [[ -d "tests" ]]; then
        cp -r "tests" "$SRC_DIR/"
        log_info "  - Copied tests directory"
    else
        log_warn "  - Tests directory not found (optional)"
    fi
}

# ============================================
# Install Configuration Files
# ============================================
install_config() {
    log_info "Installing configuration files to $CONFIG_DIR..."

    # Config files
    local config_files=(
        "worker-spec.json"
        "config.json"
        "templates.json"
        "triggers.json"
        "monthly_plan.json"
    )

    for file in "${config_files[@]}"; do
        if [[ -f "$file" ]]; then
            cp "$file" "$CONFIG_DIR/"
            log_info "  - Copied $file"
        else
            log_warn "  - Config file not found (will use defaults): $file"
        fi
    done

    # Handle .env file separately (contains secrets)
    if [[ -f ".env" ]]; then
        cp ".env" "$CONFIG_DIR/.env"
        chmod 600 "$CONFIG_DIR/.env"
        log_info "  - Copied .env (permissions: 600)"
    else
        log_warn "  - No .env file found. You must create one with your GEMINI_API_KEY"
        cat > "$CONFIG_DIR/.env" << 'ENVEOF'
# Deception Engine Configuration
# Add your Gemini API key below
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-1.5-flash
ENVEOF
        chmod 600 "$CONFIG_DIR/.env"
    fi
}

# ============================================
# Setup Python Virtual Environment
# ============================================
setup_venv() {
    log_info "Setting up Python virtual environment..."

    if [[ ! -d "$VENV_DIR" ]]; then
        python3 -m venv "$VENV_DIR"
        log_info "  - Created new venv at $VENV_DIR"
    else
        log_info "  - Using existing venv"
    fi

    # Upgrade pip
    "$VENV_DIR/bin/pip" install --upgrade pip -q

    # Install dependencies
    log_info "Installing Python dependencies..."
    if [[ -f "requirements.txt" ]]; then
        "$VENV_DIR/bin/pip" install -r requirements.txt -q
    else
        "$VENV_DIR/bin/pip" install google-generativeai -q
    fi

    log_info "  - Dependencies installed successfully"
}

# ============================================
# Create Systemd Service
# ============================================
create_service() {
    log_info "Creating systemd service: $SERVICE_NAME..."

    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=System Integrity Verification Service
Documentation=man:integrity(8)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=$APP_DIR

# Environment Configuration
EnvironmentFile=$CONFIG_DIR/.env
Environment="CONFIG_DIR=$CONFIG_DIR"
Environment="PYTHONUNBUFFERED=1"

# Main Process - Hybrid Strategy with LLM enabled
ExecStart=$VENV_DIR/bin/python -u $SRC_DIR/sys_core.py --loop --strategy-hybrid --llm

# Restart Policy
Restart=always
RestartSec=30
StartLimitIntervalSec=300
StartLimitBurst=5

# Security Hardening (optional - uncomment for production)
# NoNewPrivileges=true
# ProtectSystem=strict
# ReadWritePaths=$APP_DIR /home/dev_alice /home/sys_bob /var/lib/jenkins

# Logging
StandardOutput=append:$LOG_DIR/sys_monitor.log
StandardError=append:$LOG_DIR/sys_error.log

[Install]
WantedBy=multi-user.target
EOF

    chmod 644 "$SERVICE_FILE"
    log_info "  - Service file created at $SERVICE_FILE"
}

# ============================================
# Create Log Rotation Config
# ============================================
setup_logrotate() {
    log_info "Setting up log rotation..."

    cat > /etc/logrotate.d/sys-integrity << EOF
$LOG_DIR/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 root root
}
EOF

    log_info "  - Log rotation configured"
}

# ============================================
# Create Management Scripts
# ============================================
create_management_scripts() {
    log_info "Creating management scripts..."

    # Status script
    cat > "$APP_DIR/status.sh" << 'EOF'
#!/bin/bash
echo "=== Deception Engine Status ==="
systemctl status sys-integrity-daemon --no-pager
echo ""
echo "=== Recent Logs ==="
tail -20 /opt/sys_integrity/logs/sys_monitor.log
EOF
    chmod +x "$APP_DIR/status.sh"

    # Generate monthly plan script
    cat > "$APP_DIR/generate-plan.sh" << 'EOF'
#!/bin/bash
cd /opt/sys_integrity
source venv/bin/activate
export CONFIG_DIR=/opt/sys_integrity/config
python src/sys_core.py --llm --generate-monthly
EOF
    chmod +x "$APP_DIR/generate-plan.sh"

    # Refresh content script
    cat > "$APP_DIR/refresh-content.sh" << 'EOF'
#!/bin/bash
cd /opt/sys_integrity
source venv/bin/activate
export CONFIG_DIR=/opt/sys_integrity/config
python src/sys_core.py --llm --refresh-content
EOF
    chmod +x "$APP_DIR/refresh-content.sh"

    # Dry run test script
    cat > "$APP_DIR/test-dry-run.sh" << 'EOF'
#!/bin/bash
cd /opt/sys_integrity
source venv/bin/activate
export CONFIG_DIR=/opt/sys_integrity/config
python src/sys_core.py --dry-run --llm --strategy-hybrid
EOF
    chmod +x "$APP_DIR/test-dry-run.sh"

    log_info "  - Management scripts created in $APP_DIR"
}

# ============================================
# Finalize Installation
# ============================================
finalize() {
    log_info "Finalizing installation..."

    # Reload systemd
    systemctl daemon-reload

    # Create symlink for easy access
    ln -sf "$APP_DIR/status.sh" /usr/local/bin/deception-status 2>/dev/null || true

    log_info "Installation complete!"
    echo ""
    echo "============================================"
    echo "  DECEPTION ENGINE INSTALLATION COMPLETE"
    echo "============================================"
    echo ""
    echo "IMPORTANT: Before starting the service:"
    echo ""
    echo "1. Add your Gemini API key:"
    echo "   nano $CONFIG_DIR/.env"
    echo ""
    echo "2. (Optional) Generate initial monthly plan:"
    echo "   $APP_DIR/generate-plan.sh"
    echo ""
    echo "3. Test with dry-run mode first:"
    echo "   $APP_DIR/test-dry-run.sh"
    echo ""
    echo "4. Start the service:"
    echo "   systemctl enable --now $SERVICE_NAME"
    echo ""
    echo "5. Check status:"
    echo "   systemctl status $SERVICE_NAME"
    echo "   or: deception-status"
    echo ""
    echo "Log files: $LOG_DIR/"
    echo "============================================"
}

# ============================================
# Uninstall Function
# ============================================
uninstall() {
    log_warn "Uninstalling Deception Engine..."

    # Stop and disable service
    systemctl stop "$SERVICE_NAME" 2>/dev/null || true
    systemctl disable "$SERVICE_NAME" 2>/dev/null || true

    # Remove service file
    rm -f "$SERVICE_FILE"
    systemctl daemon-reload

    # Remove application directory
    rm -rf "$APP_DIR"

    # Remove symlink
    rm -f /usr/local/bin/deception-status

    # Remove logrotate config
    rm -f /etc/logrotate.d/sys-integrity

    log_info "Uninstallation complete."
    log_warn "Note: Persona home directories (/home/dev_alice, etc.) were NOT removed."
}

# ============================================
# Main Entry Point
# ============================================
main() {
    echo ""
    echo "============================================"
    echo "  DECEPTION ENGINE - LINUX INSTALLER"
    echo "  Research: Dynamic Fake File System"
    echo "============================================"
    echo ""

    # Parse arguments
    case "${1:-install}" in
        install)
            check_root
            preflight_checks
            create_directories
            install_source
            install_config
            setup_venv
            create_service
            setup_logrotate
            create_management_scripts
            finalize
            ;;
        uninstall)
            check_root
            uninstall
            ;;
        *)
            echo "Usage: $0 [install|uninstall]"
            exit 1
            ;;
    esac
}

main "$@"
