#!/usr/bin/env python3
"""
Debug script to test timing logic without full GUI
"""

import time

class TimingTest:
    def __init__(self):
        self.current_morse = ""
        self.current_message = ""
        self.words = []
        self.last_input_time = 0
        self.character_timeout = 1.5
        self.word_timeout = 3.0
        
        self.morse_dict = {
            '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
            '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
            '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
            '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
            '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
            '--..': 'Z'
        }
    
    def add_input(self, symbol):
        """Add dot or dash"""
        self.current_morse += symbol
        self.last_input_time = time.time()
        print(f"Added {symbol} -> Current morse: '{self.current_morse}'")
    
    def process_character(self):
        """Process current morse to character"""
        if not self.current_morse:
            return
        
        char = self.morse_dict.get(self.current_morse, '?')
        print(f"Character processed: '{self.current_morse}' -> '{char}'")
        
        self.current_message += char
        self.current_morse = ""
        # Don't reset last_input_time - keep it for word timeout
        
        print(f"Current message: '{self.current_message}'")
    
    def process_word(self):
        """Process current message to word"""
        if self.current_message:
            self.words.append(self.current_message)
            print(f"Word completed: '{self.current_message}'")
            self.current_message = ""
            self.last_input_time = 0
            print(f"Words so far: {self.words}")
    
    def check_timeouts(self):
        """Check for timeouts"""
        if self.last_input_time == 0:
            return
        
        current_time = time.time()
        time_since_input = current_time - self.last_input_time
        
        if (time_since_input >= self.character_timeout and 
            self.current_morse and 
            time_since_input < self.word_timeout):
            print(f"CHARACTER TIMEOUT ({time_since_input:.1f}s)")
            self.process_character()
        
        elif (time_since_input >= self.word_timeout and 
              self.current_message and
              not self.current_morse):
            print(f"WORD TIMEOUT ({time_since_input:.1f}s)")
            self.process_word()

# Test the timing logic
print("=== Timing Logic Test ===")
test = TimingTest()

print("\n1. Testing character timeout:")
test.add_input('.')
test.add_input('-')
print("Waiting for character timeout...")

for i in range(20):  # Wait 2 seconds
    time.sleep(0.1)
    test.check_timeouts()

print("\n2. Testing next character:")
test.add_input('.')
print("Waiting for character timeout...")

for i in range(20):  # Wait 2 seconds
    time.sleep(0.1)
    test.check_timeouts()

print("\n3. Testing word timeout:")
print("Waiting for word timeout...")

for i in range(35):  # Wait 3.5 seconds
    time.sleep(0.1)
    test.check_timeouts()

print(f"\nFinal result: Words = {test.words}, Current message = '{test.current_message}'")