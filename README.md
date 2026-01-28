# Morse Code Input System for Raspberry Pi with Sense HAT

A fun and educational Morse code input system that runs on Raspberry Pi with Sense HAT. Type messages using mouse clicks (dots and dashes), see them displayed on the LED matrix, and hear them read aloud!

## Features

- Mouse-based Morse code input (left click = dot, long press = dash)
- Real-time character display on Sense HAT 8x8 LED matrix
- Audio feedback with beeps for dots and dashes
- Text-to-speech message readout
- Mario theme celebration tune on message completion
- Fullscreen pygame display showing current input and message
- Auto-start at boot capability
- Multiple exit options (ESC key or hold both mouse buttons for 5 seconds)

## Demo Video: https://youtube.com/shorts/ZdcvvNTYktU

## Hardware Requirements

- Raspberry Pi (3, 4, or 5)
- Sense HAT
- USB Mouse
- Speaker/Audio output (for beeps and TTS)
- Display (HDMI)

## Software Requirements

```bash
pip3 install sense-hat pygame pyttsx3 numpy
```

For text-to-speech fallback:
```bash
sudo apt-get install espeak
```

## Controls

| Action | Input |
|--------|-------|
| Dot (.) | Short left click |
| Dash (-) | Long left click (>200ms) |
| Complete character | 1.5 second pause |
| Next word | 3 second pause |
| Complete message & read aloud | Right click |
| Reset session | Double right click |
| Exit application | ESC key |
| Exit application (alternative) | Hold left + right click for 5 seconds |

## Running the Application

```bash
cd morse
python3 morse_code_sense_hat.py
```

### Auto-start at Boot

To install as a systemd service:
```bash
python3 morse_code_sense_hat.py --install-service
```

## Project Structure

```
├── README.md
├── morse/
│   ├── morse_code_sense_hat.py    # Main application
│   ├── install_morse_system.sh    # Installation script
│   ├── run_morse_system.sh        # Run script
│   └── morse-code-sense-hat.service  # Systemd service file
└── demo/
    ├── sensehat.py                # Sense HAT demo
    └── test.py                    # Test scripts
```

---

## How This Project Was Developed

This project was developed using **Amazon Kiro**, an AI-powered IDE that makes complex development tasks accessible to everyone, especially students and hobbyists exploring hardware projects.

### The Development Journey

What started as a simple idea — "Can I type Morse code on a Raspberry Pi?" — evolved into a full-featured application with LED displays, audio feedback, text-to-speech, and celebration tunes. Here's how Kiro helped make this happen:

#### 1. Initial Setup and Architecture

Kiro helped design the overall architecture, suggesting the use of:
- **pygame** for fullscreen display and mouse input handling
- **sense-hat** library for LED matrix control
- **pyttsx3** for text-to-speech
- **Threading** for handling timeouts without blocking the UI

#### 2. Iterative Feature Development

Each feature was added through natural conversation:
- "Add mouse click detection for dots and dashes"
- "Display characters on the Sense HAT LED"
- "Add a Mario tune when the message is complete"
- "Let me exit by holding both mouse buttons for 5 seconds"

Kiro understood the context and implemented each feature while maintaining code quality.

#### 3. Real-time Debugging

When issues arose (like scrambled LED displays or duplicate words), describing the problem was enough:
- "The LED shows scrambled text when I reset during a message"
- "It shows 'AT AT' instead of just 'AT'"

Kiro diagnosed the threading race conditions and implemented proper locks and state management.

#### 4. Hardware-Specific Adjustments

Physical setup varies for everyone. Simple requests like:
- "Rotate the LED display 90 degrees anti-clockwise"
- "Change the exit hold time from 10 to 5 seconds"

Were handled instantly, adapting the software to the actual hardware orientation.

### Why Kiro is Perfect for Student Projects

#### Lowering the Barrier to Entry

Hardware projects traditionally require knowledge of:
- Python programming
- Threading and concurrency
- Hardware interfaces (GPIO, I2C)
- Audio processing
- Event-driven programming

With Kiro, students can focus on **what** they want to build rather than **how** to implement every detail. Describe your idea, and Kiro helps bring it to life.

#### Learning by Doing

Instead of reading documentation for hours, students can:
1. Start with a simple idea
2. See working code immediately
3. Understand the implementation through Kiro's explanations
4. Iterate and experiment freely

#### Complex Concepts Made Accessible

This project demonstrates several advanced concepts:
- **Multi-threading** for responsive UI during blocking operations
- **State machines** for Morse code timing detection
- **Audio synthesis** using numpy for generating tunes
- **Hardware abstraction** with graceful fallbacks when hardware isn't available

Kiro handles the complexity while students learn the concepts.

#### Rapid Prototyping

Ideas can be tested quickly:
- "Add an achievement tune" → implemented in minutes
- "Actually, use Mario tune instead" → switched instantly
- "Make it 3 seconds instead of 5" → done

This rapid iteration cycle keeps students engaged and experimenting.

### Real-World Skills

Working with Kiro on projects like this teaches:
- How to break down problems into smaller tasks
- How to describe technical requirements clearly
- How to debug by observing and describing behavior
- How professional software is structured

### Getting Started with Your Own Project

1. **Start simple**: "I want to make the LED display show a smiley face"
2. **Add features incrementally**: "Now make it change color when I press a button"
3. **Describe problems naturally**: "The colors look wrong on my setup"
4. **Experiment freely**: "What if we added sound effects?"

Kiro makes the Raspberry Pi + Sense HAT combination an incredible learning platform where imagination is the only limit.

---

## License

This project is open source and available for educational purposes.

## Acknowledgments

- Developed with assistance from Amazon Kiro
- Inspired by the classic Morse code communication system
- Mario theme tune adapted for educational demonstration
