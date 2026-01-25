#!/usr/bin/env python3
"""
Morse Code Input System for Raspberry Pi with Sense HAT
Features:
- Mouse input for Morse code (left click = dot, long press = dash)
- Real-time character display on Sense HAT
- Audio feedback with speaker
- Auto-start at boot capability
- Complete message display and text-to-speech
- Reset functionality with double right-click

Author: Kiro AI Assistant
Compatible with Raspberry Pi OS
"""

import time
import threading
import subprocess
import os
import sys
from collections import defaultdict
from datetime import datetime

try:
    from sense_hat import SenseHat
    import pygame
    import pynput
    from pynput import mouse
    import pyttsx3
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Please run: pip3 install sense-hat pygame pynput pyttsx3")
    sys.exit(1)

class MorseCodeSystem:
    def __init__(self):
        # Initialize Sense HAT
        self.sense = SenseHat()
        self.sense.clear()
        
        # Initialize text-to-speech
        self.tts = pyttsx3.init()
        self.tts.setProperty('rate', 150)  # Speed of speech
        
        # Initialize pygame for audio
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Morse code dictionary
        self.morse_dict = {
            '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
            '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
            '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
            '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
            '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
            '--..': 'Z', '.----': '1', '..---': '2', '...--': '3',
            '....-': '4', '.....': '5', '-....': '6', '--...': '7',
            '---..': '8', '----.': '9', '-----': '0', '--..--': ',',
            '.-.-.-': '.', '..--..': '?', '.----.': "'", '-.-.--': '!',
            '-..-.': '/', '-.--.': '(', '-.--.-': ')', '.-...': '&',
            '---...': ':', '-.-.-.': ';', '-...-': '=', '.-.-.': '+',
            '-....-': '-', '..--.-': '_', '.-..-.': '"', '...-..-': '$',
            '.--.-.': '@'
        }
        
        # Colors for display
        self.colors = {
            'red': [255, 0, 0],
            'green': [0, 255, 0],
            'blue': [0, 0, 255],
            'yellow': [255, 255, 0],
            'white': [255, 255, 255],
            'black': [0, 0, 0],
            'orange': [255, 165, 0],
            'purple': [128, 0, 128]
        }
        
        # State variables
        self.current_morse = ""
        self.current_message = ""
        self.words = []
        self.is_long_press = False
        self.press_start_time = 0
        self.last_input_time = 0
        self.word_timeout = 3.0  # 3 seconds for word separation
        self.long_press_threshold = 0.5  # 500ms for dash
        self.double_click_threshold = 0.5
        self.last_right_click_time = 0
        self.right_click_count = 0
        
        # Threading
        self.running = True
        self.input_thread = None
        self.timeout_thread = None
        
        print("Morse Code System initialized!")
        print("Controls:")
        print("- Left click: Dot (.)")
        print("- Left long press (>500ms): Dash (-)")
        print("- 3 second pause: Next word")
        print("- Right click: End message")
        print("- Double right click: Reset")
        
    def play_beep(self, frequency=800, duration=0.1):
        """Play a beep sound"""
        try:
            # Generate a simple beep
            sample_rate = 22050
            frames = int(duration * sample_rate)
            arr = []
            for i in range(frames):
                wave = 4096 * (i % (sample_rate // frequency) < (sample_rate // frequency) // 2)
                arr.append([wave, wave])
            
            sound = pygame.sndarray.make_sound(pygame.array.array('i', arr))
            sound.play()
            time.sleep(duration)
        except Exception as e:
            print(f"Audio error: {e}")
    
    def display_character(self, char, color='green'):
        """Display a character on the Sense HAT"""
        self.sense.show_letter(char, text_colour=self.colors[color])
        time.sleep(1)
    
    def display_morse_pattern(self, morse_code):
        """Display morse code pattern on LED matrix"""
        self.sense.clear()
        
        # Display dots and dashes as patterns
        row = 3  # Middle row
        col = 0
        
        for symbol in morse_code:
            if col >= 8:
                break
                
            if symbol == '.':
                # Single pixel for dot
                self.sense.set_pixel(col, row, self.colors['yellow'])
                col += 1
            elif symbol == '-':
                # Three pixels for dash
                for i in range(min(3, 8 - col)):
                    self.sense.set_pixel(col + i, row, self.colors['orange'])
                col += 3
            
            col += 1  # Space between symbols
        
        time.sleep(0.5)
    
    def process_morse_character(self):
        """Convert current morse code to character and display it"""
        if not self.current_morse:
            return
            
        char = self.morse_dict.get(self.current_morse, '?')
        
        print(f"Morse: {self.current_morse} -> Character: {char}")
        
        # Display character on Sense HAT
        self.display_character(char)
        
        # Play character sound
        if char != '?':
            self.play_beep(frequency=1000, duration=0.2)
        else:
            self.play_beep(frequency=400, duration=0.3)  # Error sound
        
        # Add to current message
        self.current_message += char
        
        # Clear current morse
        self.current_morse = ""
    
    def process_word_break(self):
        """Process word break (3 second pause)"""
        if self.current_message:
            self.words.append(self.current_message)
            print(f"Word completed: '{self.current_message}'")
            
            # Display word completion
            self.sense.show_message(
                f"WORD: {self.current_message}",
                text_colour=self.colors['blue'],
                scroll_speed=0.08
            )
            
            self.current_message = ""
    
    def complete_message(self):
        """Complete the entire message"""
        # Process any remaining character
        if self.current_morse:
            self.process_morse_character()
        
        # Add current message to words if exists
        if self.current_message:
            self.words.append(self.current_message)
        
        if not self.words:
            print("No message to complete")
            return
        
        # Create complete message
        complete_msg = " ".join(self.words)
        print(f"\nComplete message: '{complete_msg}'")
        
        # Display complete message on Sense HAT
        self.sense.show_message(
            f"MSG: {complete_msg}",
            text_colour=self.colors['green'],
            back_colour=self.colors['black'],
            scroll_speed=0.1
        )
        
        # Read out the message
        try:
            self.tts.say(f"Message complete: {complete_msg}")
            self.tts.runAndWait()
        except Exception as e:
            print(f"TTS error: {e}")
        
        # Play completion sound
        for _ in range(3):
            self.play_beep(frequency=1200, duration=0.2)
            time.sleep(0.1)
    
    def reset_system(self):
        """Reset the system for next message"""
        print("\nSystem reset - ready for new message")
        
        self.current_morse = ""
        self.current_message = ""
        self.words = []
        
        # Clear display
        self.sense.clear()
        
        # Show ready indicator
        self.sense.show_message(
            "READY",
            text_colour=self.colors['white'],
            scroll_speed=0.1
        )
        
        # Play reset sound
        self.play_beep(frequency=600, duration=0.3)
    
    def on_click(self, x, y, button, pressed):
        """Handle mouse click events"""
        current_time = time.time()
        
        if button == mouse.Button.left:
            if pressed:
                # Start of press
                self.press_start_time = current_time
                self.is_long_press = False
            else:
                # End of press
                press_duration = current_time - self.press_start_time
                
                if press_duration >= self.long_press_threshold:
                    # Long press = dash
                    self.current_morse += "-"
                    print(f"Dash (-) - Current: {self.current_morse}")
                    self.play_beep(frequency=600, duration=0.3)
                else:
                    # Short press = dot
                    self.current_morse += "."
                    print(f"Dot (.) - Current: {self.current_morse}")
                    self.play_beep(frequency=800, duration=0.1)
                
                # Display current morse pattern
                self.display_morse_pattern(self.current_morse)
                
                # Update last input time
                self.last_input_time = current_time
        
        elif button == mouse.Button.right and pressed:
            # Handle right click for message completion or reset
            time_since_last = current_time - self.last_right_click_time
            
            if time_since_last <= self.double_click_threshold:
                # Double right click = reset
                self.right_click_count += 1
                if self.right_click_count >= 2:
                    self.reset_system()
                    self.right_click_count = 0
            else:
                # Single right click = complete message
                self.right_click_count = 1
                threading.Timer(self.double_click_threshold + 0.1, self.handle_single_right_click).start()
            
            self.last_right_click_time = current_time
    
    def handle_single_right_click(self):
        """Handle single right click after timeout"""
        if self.right_click_count == 1:
            self.complete_message()
            self.right_click_count = 0
    
    def timeout_monitor(self):
        """Monitor for timeouts (word breaks)"""
        while self.running:
            current_time = time.time()
            
            # Check for word timeout
            if (self.last_input_time > 0 and 
                current_time - self.last_input_time >= self.word_timeout and
                self.current_morse):
                
                # Process current character
                self.process_morse_character()
                
                # Process word break
                self.process_word_break()
                
                # Reset timeout
                self.last_input_time = 0
            
            time.sleep(0.1)
    
    def start(self):
        """Start the Morse code system"""
        print("Starting Morse Code System...")
        
        # Show startup message
        self.sense.show_message(
            "MORSE READY",
            text_colour=self.colors['green'],
            scroll_speed=0.1
        )
        
        # Start timeout monitor thread
        self.timeout_thread = threading.Thread(target=self.timeout_monitor, daemon=True)
        self.timeout_thread.start()
        
        # Start mouse listener
        try:
            with mouse.Listener(on_click=self.on_click) as listener:
                print("Mouse listener started. System ready!")
                listener.join()
        except Exception as e:
            print(f"Mouse listener error: {e}")
    
    def stop(self):
        """Stop the system"""
        print("Stopping Morse Code System...")
        self.running = False
        self.sense.clear()
        pygame.mixer.quit()

def create_systemd_service():
    """Create systemd service for auto-start at boot"""
    service_content = f"""[Unit]
Description=Morse Code Sense HAT System
After=multi-user.target

[Service]
Type=simple
User=pi
WorkingDirectory={os.getcwd()}
ExecStart=/usr/bin/python3 {os.path.join(os.getcwd(), 'morse_code_sense_hat.py')}
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
    
    service_path = "/etc/systemd/system/morse-code-sense-hat.service"
    
    try:
        with open("/tmp/morse-code-sense-hat.service", "w") as f:
            f.write(service_content)
        
        # Copy to systemd directory (requires sudo)
        subprocess.run(["sudo", "cp", "/tmp/morse-code-sense-hat.service", service_path], check=True)
        subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
        subprocess.run(["sudo", "systemctl", "enable", "morse-code-sense-hat.service"], check=True)
        
        print(f"Systemd service created at {service_path}")
        print("Service will start automatically at boot")
        print("To start now: sudo systemctl start morse-code-sense-hat.service")
        print("To stop: sudo systemctl stop morse-code-sense-hat.service")
        print("To disable auto-start: sudo systemctl disable morse-code-sense-hat.service")
        
    except subprocess.CalledProcessError as e:
        print(f"Error creating systemd service: {e}")
        print("You may need to run this script with sudo privileges")

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--install-service":
        create_systemd_service()
        return
    
    # Create and start the Morse code system
    morse_system = MorseCodeSystem()
    
    try:
        morse_system.start()
    except KeyboardInterrupt:
        print("\nShutting down...")
        morse_system.stop()
    except Exception as e:
        print(f"Error: {e}")
        morse_system.stop()

if __name__ == "__main__":
    main()