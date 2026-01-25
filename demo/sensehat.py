#!/usr/bin/env python3
"""
Sense HAT Hello World Display Script
Displays "Hello World" message on the Sense HAT LED matrix
Compatible with Raspberry Pi OS
"""

import time
from sense_hat import SenseHat

def main():
    # Initialize the Sense HAT
    sense = SenseHat()
    
    # Clear the LED matrix
    sense.clear()
    
    # Set text properties
    text_color = [255, 255, 255]  # White text
    background_color = [0, 0, 255]  # Blue background
    
    print("Displaying 'Hello World' on Sense HAT LED matrix...")
    print("Press Ctrl+C to exit")
    
    try:
        # Display scrolling text
        sense.show_message(
            "Hello World!", 
            text_colour=text_color,
            back_colour=background_color,
            scroll_speed=0.1
        )
        
        # Keep the script running and show some patterns
        while True:
            # Show a rainbow pattern
            sense.clear()
            
            # Create a simple pattern
            colors = [
                [255, 0, 0],    # Red
                [255, 165, 0],  # Orange
                [255, 255, 0],  # Yellow
                [0, 255, 0],    # Green
                [0, 0, 255],    # Blue
                [75, 0, 130],   # Indigo
                [238, 130, 238], # Violet
                [255, 255, 255]  # White
            ]
            
            # Display colorful pattern
            for i in range(8):
                for j in range(8):
                    color_index = (i + j) % len(colors)
                    sense.set_pixel(i, j, colors[color_index])
            
            time.sleep(2)
            
            # Show "Hello World" again
            sense.show_message(
                "Hello World!", 
                text_colour=[0, 255, 0],  # Green text
                back_colour=[0, 0, 0],    # Black background
                scroll_speed=0.08
            )
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nExiting...")
        sense.clear()
        print("Sense HAT display cleared. Goodbye!")

if __name__ == "__main__":
    main()