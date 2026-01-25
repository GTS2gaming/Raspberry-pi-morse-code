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
    import pyttsx3
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Please run: pip3 install sense-hat pygame pyttsx3")
    sys.exit(1)

class MorseCodeSystem:
    def __init__(self):
        # Initialize Sense HAT with error handling
        self.sense = None
        self.sense_available = False
        try:
            self.sense = SenseHat()
            self.sense.clear()
            self.sense_available = True
            print("✓ Sense HAT initialized successfully")
        except Exception as e:
            print(f"⚠ Sense HAT initialization failed: {e}")
            print("⚠ Sense HAT display will be disabled, but system will continue")
            self.sense_available = False
        
        # Initialize text-to-speech with error handling
        self.tts = None
        self.tts_available = False
        try:
            self.tts = pyttsx3.init()
            # Try to set a working voice with better error handling
            voices = self.tts.getProperty('voices')
            if voices:
                # Try to find an English voice
                english_voice = None
                for voice in voices:
                    if 'en' in voice.id.lower() or 'english' in voice.name.lower():
                        english_voice = voice
                        break
                
                if english_voice:
                    self.tts.setProperty('voice', english_voice.id)
                else:
                    # Use first available voice
                    self.tts.setProperty('voice', voices[0].id)
            
            # Set speech properties
            self.tts.setProperty('rate', 150)  # Speed of speech
            self.tts.setProperty('volume', 0.8)  # Volume level
            
            self.tts_available = True
            print("✓ Text-to-speech initialized successfully")
        except Exception as e:
            print(f"⚠ Text-to-speech initialization failed: {e}")
            print("⚠ TTS will be disabled, but system will continue to work")
            self.tts_available = False
        
        # Initialize pygame for audio and display
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Create fullscreen display
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("Morse Code System")
        
        # Colors for pygame display
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.YELLOW = (255, 255, 0)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 0, 255)
        
        # Font for display
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        
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
        self.character_timeout = 1.5  # 1.5 seconds for character completion
        self.word_timeout = 3.0  # 3.0 seconds for word separation
        self.long_press_threshold = 0.2  # 200ms for dash
        self.double_click_threshold = 0.5
        self.last_right_click_time = 0
        self.right_click_count = 0
        self.processing_character = False  # Flag to prevent duplicate processing
        
        # Threading
        self.running = True
        self.input_thread = None
        self.timeout_thread = None
        self.input_lock = threading.Lock()  # Lock to prevent race conditions
        
        print("Morse Code System initialized!")
        print("Controls:")
        print("- Left click: Dot (.)")
        print("- Left long press (>200ms): Dash (-)")
        print("- 1.5 second pause: Complete character")
        print("- 3 second pause: Next word")
        print("- Right click: Complete message and read aloud")
        print("- Double right click: Reset")
        print("- ESC key: Exit fullscreen")
        
        # Initial screen update
        self.update_display()
        
    def speak_with_espeak(self, text):
        """Fallback TTS using espeak command directly"""
        try:
            subprocess.run(['espeak', text], check=False, capture_output=True)
            print("✓ Message spoken using espeak")
        except Exception as e:
            print(f"⚠ Espeak fallback failed: {e}")
            print("⚠ Audio output not available - message displayed only")

    def update_display(self):
        """Update the fullscreen display - thread safe"""
        try:
            # Only update display from main thread
            if threading.current_thread() is threading.main_thread():
                self._do_display_update()
            else:
                # Schedule display update for main thread
                pass  # Display will be updated in main loop
        except Exception as e:
            print(f"Display update error: {e}")
    
    def _do_display_update(self):
        """Internal display update method"""
        self.screen.fill(self.BLACK)
        
        # Title
        title_text = self.font_large.render("Morse Code System", True, self.WHITE)
        title_rect = title_text.get_rect(center=(self.screen.get_width()//2, 80))
        self.screen.blit(title_text, title_rect)
        
        # Current morse code
        if self.current_morse:
            morse_text = self.font_medium.render(f"Current: {self.current_morse}", True, self.YELLOW)
            morse_rect = morse_text.get_rect(center=(self.screen.get_width()//2, 150))
            self.screen.blit(morse_text, morse_rect)
        
        # Current message
        if self.current_message:
            msg_text = self.font_medium.render(f"Message: {self.current_message}", True, self.GREEN)
            msg_rect = msg_text.get_rect(center=(self.screen.get_width()//2, 200))
            self.screen.blit(msg_text, msg_rect)
        
        # Complete words
        if self.words:
            words_text = self.font_small.render(f"Words: {' '.join(self.words)}", True, self.BLUE)
            words_rect = words_text.get_rect(center=(self.screen.get_width()//2, 250))
            self.screen.blit(words_text, words_rect)
        
        # TIMER DEBUG INFORMATION
        current_time = time.time()
        
        # Time since last input
        if self.last_input_time > 0:
            time_since_input = current_time - self.last_input_time
            timer_color = self.RED if time_since_input > self.character_timeout else self.YELLOW
            timer_text = self.font_small.render(f"Time since input: {time_since_input:.1f}s", True, timer_color)
            timer_rect = timer_text.get_rect(center=(self.screen.get_width()//2, 300))
            self.screen.blit(timer_text, timer_rect)
            
            # Character timeout countdown
            char_remaining = self.character_timeout - time_since_input
            if char_remaining > 0 and self.current_morse:
                char_color = self.RED if char_remaining < 1.0 else self.YELLOW
                char_text = self.font_small.render(f"Character timeout in: {char_remaining:.1f}s", True, char_color)
                char_rect = char_text.get_rect(center=(self.screen.get_width()//2, 330))
                self.screen.blit(char_text, char_rect)
            
            # Word timeout countdown
            word_remaining = self.word_timeout - time_since_input
            if word_remaining > 0 and self.current_message and not self.current_morse:
                word_color = self.RED if word_remaining < 1.0 else self.BLUE
                word_text = self.font_small.render(f"Word timeout in: {word_remaining:.1f}s", True, word_color)
                word_rect = word_text.get_rect(center=(self.screen.get_width()//2, 360))
                self.screen.blit(word_text, word_rect)
        else:
            no_timer_text = self.font_small.render("No active timer", True, self.WHITE)
            no_timer_rect = no_timer_text.get_rect(center=(self.screen.get_width()//2, 300))
            self.screen.blit(no_timer_text, no_timer_rect)
        
        # Processing status
        if self.processing_character:
            proc_text = self.font_small.render("PROCESSING CHARACTER...", True, self.RED)
            proc_rect = proc_text.get_rect(center=(self.screen.get_width()//2, 390))
            self.screen.blit(proc_text, proc_rect)
        
        # Timer configuration display
        config_y = 420
        config_text = self.font_small.render(f"Config: Char={self.character_timeout}s, Word={self.word_timeout}s", True, self.WHITE)
        config_rect = config_text.get_rect(center=(self.screen.get_width()//2, config_y))
        self.screen.blit(config_text, config_rect)
        
        # Instructions (moved down)
        instructions = [
            "Left Click: Dot (.)",
            "Left Long Press: Dash (-)",
            "1.5s Pause: Complete Character",
            "3s Pause: Next Word",
            "Right Click: Complete Message",
            "Double Right Click: Reset",
            "ESC: Exit"
        ]
        
        y_offset = self.screen.get_height() - 220
        for instruction in instructions:
            inst_text = self.font_small.render(instruction, True, self.WHITE)
            inst_rect = inst_text.get_rect(center=(self.screen.get_width()//2, y_offset))
            self.screen.blit(inst_text, inst_rect)
            y_offset += 25
        
        pygame.display.flip()

    def play_beep(self, frequency=800, duration=0.1):
        """Play a beep sound"""
        try:
            # Try to use numpy for better audio generation
            try:
                import numpy as np
                sample_rate = 22050
                frames = int(duration * sample_rate)
                
                # Create sine wave
                arr = np.sin(2 * np.pi * frequency * np.linspace(0, duration, frames))
                arr = (arr * 32767).astype(np.int16)
                
                # Convert to stereo
                stereo_arr = np.zeros((frames, 2), dtype=np.int16)
                stereo_arr[:, 0] = arr
                stereo_arr[:, 1] = arr
                
                sound = pygame.sndarray.make_sound(stereo_arr)
                sound.play()
                time.sleep(duration)
            except ImportError:
                # Fallback without numpy
                sample_rate = 22050
                frames = int(duration * sample_rate)
                
                # Simple square wave generation
                arr = []
                for i in range(frames):
                    # Generate square wave
                    cycle_length = sample_rate // frequency
                    if (i % cycle_length) < (cycle_length // 2):
                        sample = 16384  # Half volume
                    else:
                        sample = -16384
                    arr.append([sample, sample])
                
                # Convert to pygame sound
                import array
                sound_array = array.array('h', [item for sublist in arr for item in sublist])
                sound = pygame.sndarray.make_sound(sound_array.reshape((-1, 2)))
                sound.play()
                time.sleep(duration)
                
        except Exception as e:
            print(f"Audio error: {e}")
            # Fallback: just print beep
            print(f"BEEP: {frequency}Hz for {duration}s")
    
    def display_character(self, char, color='green'):
        """Display a character on the Sense HAT"""
        if self.sense_available:
            try:
                self.sense.show_letter(char, text_colour=self.colors[color])
                # Don't sleep here - it blocks the main thread and causes duplicate processing
                # time.sleep(1)  # Removed to prevent threading issues
            except Exception as e:
                print(f"⚠ Sense HAT display error: {e}")
        else:
            print(f"Character displayed: {char} (Sense HAT not available)")
    
    def display_morse_pattern(self, morse_code):
        """Display morse code pattern on LED matrix"""
        if not self.sense_available:
            print(f"Morse pattern: {morse_code} (Sense HAT not available)")
            return
            
        try:
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
        except Exception as e:
            print(f"⚠ Sense HAT pattern display error: {e}")
    
    def process_morse_character(self):
        """Convert current morse code to character and display it"""
        if not self.current_morse:
            print("DEBUG: process_morse_character called but no morse to process")
            return
            
        # Prevent duplicate processing by clearing morse immediately
        morse_to_process = self.current_morse
        self.current_morse = ""
        
        print(f"DEBUG: Processing morse '{morse_to_process}' (cleared current_morse)")
        
        char = self.morse_dict.get(morse_to_process, '?')
        
        print(f"Character completed: {morse_to_process} -> {char}")
        
        # Display character on Sense HAT
        self.display_character(char)
        
        # Play character sound
        if char != '?':
            self.play_beep(frequency=1000, duration=0.2)
        else:
            self.play_beep(frequency=400, duration=0.3)  # Error sound
        
        # Add to current message
        self.current_message += char
        print(f"Current message: '{self.current_message}'")
        
        # Reset last_input_time to current time so the next character's timeout starts fresh
        # This prevents premature timeouts on subsequent characters
        self.last_input_time = time.time()
        
        # Update display
        self.update_display()
    
    def process_word_break(self):
        """Process word break (3 second pause)"""
        if self.current_message:
            self.words.append(self.current_message)
            print(f"Word completed: '{self.current_message}'")
            
            # Display word completion
            if self.sense_available:
                try:
                    self.sense.show_message(
                        f"WORD: {self.current_message}",
                        text_colour=self.colors['blue'],
                        scroll_speed=0.08
                    )
                except Exception as e:
                    print(f"⚠ Sense HAT word display error: {e}")
            
            self.current_message = ""
            
            # Update display
            self.update_display()
    
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
        if self.sense_available:
            try:
                self.sense.show_message(
                    f"MSG: {complete_msg}",
                    text_colour=self.colors['green'],
                    back_colour=self.colors['black'],
                    scroll_speed=0.1
                )
            except Exception as e:
                print(f"⚠ Sense HAT message display error: {e}")
        
        # Read out the message
        if self.tts_available:
            try:
                self.tts.say(f"Message complete: {complete_msg}")
                self.tts.runAndWait()
                print("✓ Message read aloud")
            except Exception as e:
                print(f"⚠ TTS playback failed: {e}")
                # Try fallback espeak command
                self.speak_with_espeak(f"Message complete: {complete_msg}")
        else:
            # Try fallback espeak command
            self.speak_with_espeak(f"Message complete: {complete_msg}")
        
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
        if self.sense_available:
            try:
                self.sense.clear()
                
                # Show ready indicator
                self.sense.show_message(
                    "READY",
                    text_colour=self.colors['white'],
                    scroll_speed=0.1
                )
            except Exception as e:
                print(f"⚠ Sense HAT reset display error: {e}")
        
        # Play reset sound
        self.play_beep(frequency=600, duration=0.3)
        
        # Update display
        self.update_display()
    
    def handle_mouse_event(self, event):
        """Handle pygame mouse events"""
        current_time = time.time()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left button
                # Start of press
                self.press_start_time = current_time
                self.is_long_press = False
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left button
                # End of press - this is when we actually register the input
                press_duration = current_time - self.press_start_time
                
                print(f"DEBUG: Mouse button UP detected, press duration: {press_duration:.2f}s")
                
                # Use lock to prevent race condition with timeout monitor
                with self.input_lock:
                    if press_duration >= self.long_press_threshold:
                        # Long press = dash
                        self.current_morse += "-"
                        print(f"Dash (-) after {press_duration:.2f}s press - Current: {self.current_morse}")
                        self.play_beep(frequency=600, duration=0.3)
                    else:
                        # Short press = dot
                        self.current_morse += "."
                        print(f"Dot (.) after {press_duration:.2f}s press - Current: {self.current_morse}")
                        self.play_beep(frequency=800, duration=0.1)
                    
                    # Update last input time to NOW (when button was released)
                    # This starts the character timeout from the button release, not press
                    old_time = self.last_input_time
                    self.last_input_time = current_time
                    print(f"DEBUG: Input timing reset from {old_time} to {current_time}, character timeout will start from button release")
                
                # Display current morse pattern
                self.display_morse_pattern(self.current_morse)
                
                # Update display
                self.update_display()
                
            elif event.button == 3:  # Right button
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
        """Monitor for timeouts (character completion and word breaks)"""
        while self.running:
            current_time = time.time()
            
            if self.last_input_time > 0 and not self.processing_character:
                time_since_input = current_time - self.last_input_time
                
                # Check for character timeout
                # Only process if we have morse code AND enough time has passed
                if (time_since_input >= self.character_timeout and 
                    self.current_morse and 
                    time_since_input < self.word_timeout):
                    
                    # Use lock to safely check and process
                    with self.input_lock:
                        # Re-check conditions after acquiring lock
                        time_since_input = time.time() - self.last_input_time
                        if (time_since_input >= self.character_timeout and 
                            self.current_morse and 
                            time_since_input < self.word_timeout):
                            
                            print(f"DEBUG: Character timeout triggered - time_since_input={time_since_input:.1f}s, current_morse='{self.current_morse}'")
                            self.processing_character = True
                            self.process_morse_character()
                            self.processing_character = False
                
                # Check for word timeout - only if we have a current message and no pending morse
                elif (time_since_input >= self.word_timeout and 
                      self.current_message and
                      not self.current_morse):
                    
                    print(f"DEBUG: Word timeout triggered - time_since_input={time_since_input:.1f}s, current_message='{self.current_message}'")
                    self.process_word_break()
                    # Reset timeout after word completion
                    self.last_input_time = 0
                    print(f"DEBUG: Reset last_input_time to 0 after word completion")
            
            time.sleep(0.1)
    
    def start(self):
        """Start the Morse code system"""
        print("Starting Morse Code System...")
        
        # Show startup message
        if self.sense_available:
            try:
                self.sense.show_message(
                    "MORSE READY",
                    text_colour=self.colors['green'],
                    scroll_speed=0.1
                )
            except Exception as e:
                print(f"⚠ Sense HAT startup display error: {e}")
        
        # Start timeout monitor thread
        self.timeout_thread = threading.Thread(target=self.timeout_monitor, daemon=True)
        self.timeout_thread.start()
        
        # Main pygame event loop
        clock = pygame.time.Clock()
        
        try:
            print("Fullscreen application started. System ready!")
            print("Press ESC to exit fullscreen mode")
            
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.running = False
                    elif event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
                        self.handle_mouse_event(event)
                
                # Update display (thread-safe)
                self._do_display_update()
                clock.tick(60)  # 60 FPS
                
        except Exception as e:
            print(f"Event loop error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the system"""
        print("Stopping Morse Code System...")
        self.running = False
        if self.sense_available:
            try:
                self.sense.clear()
            except Exception as e:
                print(f"⚠ Sense HAT cleanup error: {e}")
        pygame.mixer.quit()
        pygame.quit()

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