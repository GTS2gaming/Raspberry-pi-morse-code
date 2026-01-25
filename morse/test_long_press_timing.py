#!/usr/bin/env python3
"""
Test to verify that long press timing works correctly
Simulates holding mouse button down for several seconds
"""

import time

class LongPressTimingTest:
    def __init__(self):
        self.current_morse = ""
        self.current_message = ""
        self.words = []
        self.last_input_time = 0
        self.character_timeout = 1.5
        self.word_timeout = 3.0
        self.input_debounce = 0.3
        self.long_press_threshold = 0.5
        
        self.morse_dict = {
            '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
            '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
            '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
            '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
            '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
            '--..': 'Z'
        }
    
    def simulate_mouse_press(self, press_duration):
        """Simulate a mouse press for given duration"""
        press_start = time.time()
        print(f"Mouse button DOWN (simulating {press_duration}s press)")
        
        # Simulate holding the button down
        time.sleep(press_duration)
        
        # Mouse button UP - this is when input is registered
        release_time = time.time()
        actual_duration = release_time - press_start
        
        if actual_duration >= self.long_press_threshold:
            # Long press = dash
            self.current_morse += "-"
            print(f"Mouse button UP after {actual_duration:.2f}s -> Dash (-)")
        else:
            # Short press = dot
            self.current_morse += "."
            print(f"Mouse button UP after {actual_duration:.2f}s -> Dot (.)")
        
        # Set timing from button RELEASE, not press
        self.last_input_time = release_time
        print(f"Timing reset to button release time - Current morse: '{self.current_morse}'")
        
        return actual_duration
    
    def process_character(self):
        """Process current morse to character"""
        if not self.current_morse:
            return
        
        char = self.morse_dict.get(self.current_morse, '?')
        print(f"  ✓ Character: '{self.current_morse}' -> '{char}'")
        
        self.current_message += char
        self.current_morse = ""
        
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
            print(f"⏰ Character timeout ({time_since_input:.1f}s since button release)")
            self.process_character()
            return True
        
        return False

def test_long_press_scenario():
    print("=== Testing Long Press Timing ===")
    test = LongPressTimingTest()
    
    print("\n1. Simulating 3-second dash press:")
    press_duration = test.simulate_mouse_press(3.0)
    
    print(f"\n2. Waiting for character timeout (should be 1.8s from button RELEASE):")
    print("   The 3-second press time should NOT count toward character timeout")
    
    start_wait = time.time()
    timeout_triggered = False
    
    # Wait up to 2.5 seconds for timeout
    for i in range(25):
        time.sleep(0.1)
        if test.check_timeouts():
            timeout_triggered = True
            actual_wait = time.time() - start_wait
            print(f"   ✓ Timeout triggered after {actual_wait:.1f}s of waiting")
            break
    
    if not timeout_triggered:
        print("   ❌ Timeout never triggered!")
        return False
    
    # Verify the character is correct
    expected_char = 'T'  # Single dash = T
    if test.current_message == expected_char:
        print(f"   ✓ Correct character: '{expected_char}'")
        return True
    else:
        print(f"   ❌ Wrong character: expected '{expected_char}', got '{test.current_message}'")
        return False

def test_multiple_long_presses():
    print("\n=== Testing Multiple Long Presses for '---' (O) ===")
    test = LongPressTimingTest()
    
    print("\n1. First 2-second dash:")
    test.simulate_mouse_press(2.0)
    
    print("\n2. Second 1.5-second dash (within debounce period):")
    time.sleep(0.2)  # Short gap
    test.simulate_mouse_press(1.5)
    
    print("\n3. Third 2.5-second dash (within debounce period):")
    time.sleep(0.1)  # Very short gap
    test.simulate_mouse_press(2.5)
    
    print(f"\n4. Current morse should be '---': '{test.current_morse}'")
    
    print("\n5. Waiting for character timeout:")
    start_wait = time.time()
    
    for i in range(25):
        time.sleep(0.1)
        if test.check_timeouts():
            actual_wait = time.time() - start_wait
            print(f"   ✓ Timeout after {actual_wait:.1f}s")
            break
    
    return test.current_message == 'O'

# Run tests
print("Testing long press timing behavior...")
test1_passed = test_long_press_scenario()
test2_passed = test_multiple_long_presses()

print(f"\n{'✅ ALL TESTS PASSED' if test1_passed and test2_passed else '❌ SOME TESTS FAILED'}")
print("Long press timing should now work correctly!")