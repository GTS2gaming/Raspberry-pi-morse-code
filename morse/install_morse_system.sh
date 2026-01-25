#!/bin/bash

# Morse Code Sense HAT System Installation Script
# This script installs all dependencies and sets up auto-start at boot

echo "=== Morse Code Sense HAT System Installation ==="
echo "Installing dependencies and configuring system..."

# Update package list
echo "Updating package list..."
sudo apt update

# Install system packages
echo "Installing system packages..."
sudo apt install -y \
    sense-hat \
    python3-sense-hat \
    python3-pip \
    python3-pygame \
    espeak \
    espeak-data \
    libespeak1 \
    libespeak-dev \
    festival \
    festvox-kallpc16k \
    alsa-utils \
    pulseaudio

# Install Python packages
echo "Installing Python packages..."
pip3 install --user \
    sense-hat \
    pygame \
    pynput \
    pyttsx3

# Enable I2C for Sense HAT
echo "Enabling I2C..."
sudo raspi-config nonint do_i2c 0

# Add user to required groups
echo "Adding user to required groups..."
sudo usermod -a -G i2c,audio,input $USER

# Make scripts executable
echo "Making scripts executable..."
chmod +x morse_code_sense_hat.py
chmod +x install_morse_system.sh

# Test audio system
echo "Testing audio system..."
if command -v speaker-test &> /dev/null; then
    echo "Audio test (2 seconds)..."
    timeout 2s speaker-test -t sine -f 1000 -l 1 &> /dev/null || true
fi

# Create desktop shortcut
echo "Creating desktop shortcut..."
cat > ~/Desktop/morse_code_system.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Morse Code System
Comment=Morse Code Input with Sense HAT
Exec=python3 $(pwd)/morse_code_sense_hat.py
Icon=input-keyboard
Terminal=true
Categories=Utility;
EOF

chmod +x ~/Desktop/morse_code_system.desktop

# Install systemd service for auto-start
echo "Installing systemd service for auto-start..."
python3 morse_code_sense_hat.py --install-service

echo ""
echo "=== Installation Complete! ==="
echo ""
echo "IMPORTANT: Please reboot your Raspberry Pi to ensure all changes take effect:"
echo "sudo reboot"
echo ""
echo "After reboot, the Morse Code System will:"
echo "1. Start automatically at boot"
echo "2. Be available via desktop shortcut"
echo "3. Be controllable via systemd commands"
echo ""
echo "Manual start options:"
echo "python3 morse_code_sense_hat.py          # Run directly"
echo "sudo systemctl start morse-code-sense-hat.service  # Start service"
echo ""
echo "System controls:"
echo "sudo systemctl stop morse-code-sense-hat.service   # Stop service"
echo "sudo systemctl disable morse-code-sense-hat.service # Disable auto-start"
echo "sudo systemctl enable morse-code-sense-hat.service  # Enable auto-start"
echo ""
echo "Usage Instructions:"
echo "- Left click: Dot (.)"
echo "- Left long press (>500ms): Dash (-)"
echo "- 3 second pause: Next word"
echo "- Right click: End message and read aloud"
echo "- Double right click: Reset for new message"
echo ""
echo "Make sure your Sense HAT is properly connected to the GPIO pins!"