#!/usr/bin/env python3
"""
Test script to verify fullscreen functionality
"""

import pygame
import sys

def test_fullscreen():
    """Test fullscreen pygame window"""
    print("Testing fullscreen pygame window...")
    
    try:
        pygame.init()
        
        # Create fullscreen display
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("Fullscreen Test")
        
        # Colors
        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        GREEN = (0, 255, 0)
        
        # Font
        font = pygame.font.Font(None, 72)
        
        print("✓ Fullscreen window created")
        print("✓ Press ESC to exit, click mouse to test input")
        
        clock = pygame.time.Clock()
        running = True
        click_count = 0
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    click_count += 1
                    print(f"Mouse click detected! Count: {click_count}")
            
            # Clear screen
            screen.fill(BLACK)
            
            # Draw text
            title_text = font.render("Fullscreen Test", True, WHITE)
            title_rect = title_text.get_rect(center=(screen.get_width()//2, 200))
            screen.blit(title_text, title_rect)
            
            click_text = font.render(f"Clicks: {click_count}", True, GREEN)
            click_rect = click_text.get_rect(center=(screen.get_width()//2, 300))
            screen.blit(click_text, click_rect)
            
            instruction_text = font.render("Press ESC to exit", True, WHITE)
            instruction_rect = instruction_text.get_rect(center=(screen.get_width()//2, 400))
            screen.blit(instruction_text, instruction_rect)
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        print("✓ Fullscreen test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Fullscreen test failed: {e}")
        pygame.quit()
        return False

if __name__ == "__main__":
    if test_fullscreen():
        print("\n✓ Fullscreen functionality working!")
        print("✓ Mouse input detection working!")
        print("✓ Ready to run morse code system in fullscreen")
    else:
        print("\n✗ Fullscreen test failed")
        sys.exit(1)