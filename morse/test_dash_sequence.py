#!/usr/bin/env python3
"""
Test for typing dash sequences like "---" (O) without premature completion
"""

import time

class DashSequenceTest:
    def __init__(self):
        self.current_morse = ""
        self.current_message = ""
        self.words = []
        self.last_input_time = 0
        self.character_timeout = 1.5
        self.word_timeout = 3.0
        self.input_debounce = 0.3  # 300ms debounce period
        
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
        print(f"Input: {symbol} -> Morse: '{self.current_morse}' (time reset)")
    
    def process_character(self):
        """Process current morse to character"""
        if not self.current_morse:
            return
        
        char = self.morse_dict.get(self.current_morse, '?')
        print(f"  ✓ Character: '{self.current_morse}' -> '{char}'")
        
        self.current_message += char
        self.current_morse = ""
        # Keep last_input_time for word timeout
        
        print(f"  Message: '{self.current_message}'")
    
    def check_timeouts(self):
        """Check for timeouts"""
        if self.last_input_time == 0:
            return False
        
        current_time = time.time()
        time_since_input = current_time - self.last_input_time
        
        # Character timeout with debounce
        if (time_since_input >= (self.input_debounce + self.character_timeout) and 
            self.current_morse and 
            time_since_input < self.word_timeout):
            print(f"⏰ Character timeout ({time_since_input:.1f}s) - debounce + timeout = {self.input_debounce + self.character_timeout}s")
            self.process_character()
            return True
        
        return False

def test_dash_sequence():
    print("=== Testing '---' (O) with debounce ===")
    test = DashSequenceTest()
    
    print("\n1. Typing first dash:")
    test.add_input('-')
    
    # Wait 0.5 seconds (less than debounce + timeout)
    print("   Waiting 0.5s...")
    for i in range(5):
        time.sleep(0.1)
        if test.check_timeouts():
            print("   ❌ PREMATURE TIMEOUT!")
            return False
    
    print("   ✓ No premature timeout")
    
    print("\n2. Typing second dash:")
    test.add_input('-')
    
    # Wait 0.8 seconds (still less than debounce + timeout)
    print("   Waiting 0.8s...")
    for i in range(8):
        time.sleep(0.1)
        if test.check_timeouts():
            print("   ❌ PREMATURE TIMEOUT!")
            return False
    
    print("   ✓ No premature timeout")
    
    print("\n3. Typing third dash:")
    test.add_input('-')
    
    # Wait 1.0 second (still less than debounce + timeout = 1.8s)
    print("   Waiting 1.0s...")
    for i in range(10):
        time.sleep(0.1)
        if test.check_timeouts():
            print("   ❌ PREMATURE TIMEOUT!")
            return False
    
    print("   ✓ No premature timeout")
    
    print("\n4. Waiting for proper timeout (1.8s total):")
    print("   Waiting additional 0.9s to reach 1.8s total...")
    for i in range(9):
        time.sleep(0.1)
        if test.check_timeouts():
            print("   ✓ Proper timeout triggered!")
            break
    else:
        print("   ❌ Timeout didn't trigger!")
        return False
    
    return test.current_message == 'O'

# Run the test
success = test_dash_sequence()
print(f"\n{'✅ TEST PASSED - No premature timeouts!' if success else '❌ TEST FAILED'}")