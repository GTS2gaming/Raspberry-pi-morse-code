#!/usr/bin/env python3
"""
Complete flow test for the updated timing system
"""

import time

class CompleteFlowTest:
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
        print(f"Input: {symbol} -> Morse: '{self.current_morse}'")
    
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
    
    def process_word(self):
        """Process current message to word"""
        if self.current_message:
            self.words.append(self.current_message)
            print(f"  ✓ Word: '{self.current_message}'")
            self.current_message = ""
            self.last_input_time = 0
            print(f"  Words: {self.words}")
    
    def check_timeouts(self):
        """Check for timeouts"""
        if self.last_input_time == 0:
            return False
        
        current_time = time.time()
        time_since_input = current_time - self.last_input_time
        
        if (time_since_input >= self.character_timeout and 
            self.current_morse and 
            time_since_input < self.word_timeout):
            print(f"⏰ Character timeout ({time_since_input:.1f}s)")
            self.process_character()
            return True
        
        elif (time_since_input >= self.word_timeout and 
              self.current_message and
              not self.current_morse):
            print(f"⏰ Word timeout ({time_since_input:.1f}s)")
            self.process_word()
            return True
        
        return False

def simulate_typing_with_pauses():
    print("=== Complete Flow Test: 'HELLO' ===")
    test = CompleteFlowTest()
    
    # Type 'H' (.... )
    print("\n1. Typing 'H' (....):")
    test.add_input('.')
    test.add_input('.')
    test.add_input('.')
    test.add_input('.')
    
    # Wait for character timeout
    print("   Waiting 1.5s for character...")
    for i in range(16):
        time.sleep(0.1)
        if test.check_timeouts():
            break
    
    # Type 'E' (.)
    print("\n2. Typing 'E' (.):")
    test.add_input('.')
    
    # Wait for character timeout
    print("   Waiting 1.5s for character...")
    for i in range(16):
        time.sleep(0.1)
        if test.check_timeouts():
            break
    
    # Type 'L' (.-..)
    print("\n3. Typing 'L' (.-..):")
    test.add_input('.')
    test.add_input('-')
    test.add_input('.')
    test.add_input('.')
    
    # Wait for character timeout
    print("   Waiting 1.5s for character...")
    for i in range(16):
        time.sleep(0.1)
        if test.check_timeouts():
            break
    
    # Type 'L' again
    print("\n4. Typing 'L' (.-..) again:")
    test.add_input('.')
    test.add_input('-')
    test.add_input('.')
    test.add_input('.')
    
    # Wait for character timeout
    print("   Waiting 1.5s for character...")
    for i in range(16):
        time.sleep(0.1)
        if test.check_timeouts():
            break
    
    # Type 'O' (---)
    print("\n5. Typing 'O' (---):")
    test.add_input('-')
    test.add_input('-')
    test.add_input('-')
    
    # Wait for character timeout
    print("   Waiting 1.5s for character...")
    for i in range(16):
        time.sleep(0.1)
        if test.check_timeouts():
            break
    
    # Wait for word timeout
    print("\n6. Waiting 3s for word completion...")
    for i in range(35):
        time.sleep(0.1)
        if test.check_timeouts():
            break
    
    print(f"\n✅ Final result: {test.words}")
    return test.words == ['HELLO']

# Run the test
success = simulate_typing_with_pauses()
print(f"\n{'✅ TEST PASSED' if success else '❌ TEST FAILED'}")