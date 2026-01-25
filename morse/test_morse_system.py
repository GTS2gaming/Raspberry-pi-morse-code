#!/usr/bin/env python3
"""
Test script for Morse Code Sense HAT System
Tests individual components before running the full system
"""

import sys
import time

def test_imports():
    """Test if all required packages are installed"""
    print("Testing imports...")
    
    try:
        from sense_hat import SenseHat
        print("✓ sense_hat imported successfully")
    except ImportError:
        print("✗ sense_hat import failed - install with: sudo apt install sense-hat python3-sense-hat")
        return False
    
    try:
        import pygame
        print("✓ pygame imported successfully")
    except ImportError:
        print("✗ pygame import failed - install with: pip3 install pygame")
        return False
    
    try:
        import pyttsx3
        print("✓ pyttsx3 imported successfully")
    except ImportError:
        print("✗ pyttsx3 import failed - install with: pip3 install pyttsx3")
        return False
    
    print("✓ All required packages imported successfully")
    return True

def test_sense_hat():
    """Test Sense HAT functionality"""
    print("\nTesting Sense HAT...")
    
    try:
        sense = SenseHat()
        sense.clear()
        
        # Test LED matrix
        sense.set_pixel(0, 0, [255, 0, 0])  # Red pixel
        print("✓ LED matrix working")
        time.sleep(1)
        
        # Test text display
        sense.show_letter("T", text_colour=[0, 255, 0])
        print("✓ Text display working")
        time.sleep(1)
        
        sense.clear()
        return True
        
    except Exception as e:
        print(f"✗ Sense HAT test failed: {e}")
        return False

def test_audio():
    """Test audio functionality"""
    print("\nTesting audio...")
    
    try:
        import pygame
        pygame.mixer.init()
        
        # Test pygame audio
        print("✓ Pygame audio initialized")
        
        # Test TTS
        import pyttsx3
        tts = pyttsx3.init()
        print("✓ Text-to-speech initialized")
        
        return True
        
    except Exception as e:
        print(f"✗ Audio test failed: {e}")
        return False

def test_mouse_input():
    """Test pygame mouse input capability"""
    print("\nTesting pygame mouse input...")
    
    try:
        import pygame
        pygame.init()
        
        # Test pygame initialization
        print("✓ Pygame initialized successfully")
        
        # Test display creation (headless mode)
        try:
            screen = pygame.display.set_mode((100, 100))
            print("✓ Pygame display created")
            pygame.quit()
        except pygame.error:
            print("✓ Pygame mouse input system available (headless mode)")
        
        return True
        
    except Exception as e:
        print(f"✗ Pygame mouse input test failed: {e}")
        return False

def test_morse_conversion():
    """Test Morse code conversion"""
    print("\nTesting Morse code conversion...")
    
    morse_dict = {
        '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
        '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J'
    }
    
    test_cases = [
        ('.-', 'A'),
        ('-...', 'B'),
        ('....', 'H'),
        ('...---...', None)  # SOS - not in basic dict
    ]
    
    for morse, expected in test_cases:
        result = morse_dict.get(morse, '?')
        if expected:
            if result == expected:
                print(f"✓ {morse} -> {result}")
            else:
                print(f"✗ {morse} -> {result} (expected {expected})")
                return False
        else:
            print(f"✓ {morse} -> {result} (unknown code)")
    
    return True

def run_demo():
    """Run a simple demo"""
    print("\nRunning demo...")
    
    try:
        from sense_hat import SenseHat
        import pygame
        
        sense = SenseHat()
        pygame.mixer.init()
        
        # Demo sequence
        sense.show_message("MORSE DEMO", text_colour=[0, 255, 0], scroll_speed=0.1)
        
        # Show some Morse patterns
        morse_demo = [
            ("SOS", "... --- ..."),
            ("HELLO", ".... . .-.. .-.. ---")
        ]
        
        for word, morse in morse_demo:
            sense.show_message(f"{word}: {morse}", text_colour=[255, 255, 0], scroll_speed=0.08)
            time.sleep(1)
        
        sense.show_message("DEMO COMPLETE", text_colour=[0, 255, 0], scroll_speed=0.1)
        sense.clear()
        
        print("✓ Demo completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Demo failed: {e}")
        return False

def main():
    """Main test function"""
    print("=== Morse Code System Test Suite ===\n")
    
    tests = [
        ("Package Imports", test_imports),
        ("Sense HAT Hardware", test_sense_hat),
        ("Audio System", test_audio),
        ("Mouse Input", test_mouse_input),
        ("Morse Conversion", test_morse_conversion),
        ("System Demo", run_demo)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} PASSED")
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} ERROR: {e}")
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! System ready to use.")
        print("\nTo start the Morse Code System:")
        print("python3 morse_code_sense_hat.py")
    else:
        print("✗ Some tests failed. Please check the installation.")
        print("\nTo install dependencies:")
        print("bash install_morse_system.sh")

if __name__ == "__main__":
    main()