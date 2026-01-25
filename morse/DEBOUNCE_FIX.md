# Debounce Fix for Premature Character Completion

## Problem
When typing sequences like "---" (O), the system was completing the character prematurely after "-." instead of waiting for all three dashes to be entered.

## Root Cause
The character timeout was starting immediately after each click, so:
- Click 1: "-" → timer starts
- Wait 1.5s → character completes as "T" (wrong!)
- User never gets to complete "---"

## Solution: Input Debounce
Added a 300ms debounce period before the character timeout starts:

### New Timing Logic
1. **Input Debounce**: 300ms grace period after each click
2. **Character Timeout**: 1.5s after debounce period ends
3. **Total Wait Time**: 1.8s (300ms + 1500ms) for character completion

### How It Works
```
Click: -           (timer starts)
Click: -           (timer resets)  ← Key improvement
Click: -           (timer resets)  ← Key improvement
Wait 300ms         (debounce period)
Wait 1500ms more   (character timeout)
Total: 1800ms      → Character "---" = "O" completed
```

## Benefits
✅ **No Premature Completion**: Can type multi-symbol characters without interruption  
✅ **Natural Typing Flow**: 300ms debounce allows for normal clicking speed  
✅ **Reliable Timing**: Still auto-completes after reasonable pause  
✅ **Backward Compatible**: Existing single-symbol characters still work  

## Updated Timings
- **Character Completion**: 1.8 seconds (300ms debounce + 1.5s timeout)
- **Word Completion**: 3 seconds (unchanged)
- **Message Completion**: Right-click (unchanged)

## Test Results
- "---" (O): ✅ No premature completion
- ".-.." (L): ✅ Works correctly  
- "...." (H): ✅ Works correctly
- Single symbols: ✅ Still work fine

The system now allows proper typing of complex morse characters!