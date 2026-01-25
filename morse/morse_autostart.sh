#!/bin/bash

# Morse Code System Auto-Start Script
# This script ensures the application starts with proper display environment

# Wait for desktop environment to be ready
sleep 10

# Set display environment
export DISPLAY=:0
export XAUTHORITY=/home/gt/.Xauthority

# Change to the application directory
cd "$(dirname "$0")"

# Start the Morse code system
python3 morse_code_sense_hat.py

# Log any errors
echo "Morse Code System started at $(date)" >> /tmp/morse_startup.log