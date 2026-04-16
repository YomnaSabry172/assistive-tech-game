import pygame
import sys
from settings import *
from game import Game

class GameManager:
    def __init__(self):
        pygame.init()
        self.display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Ninja Frog Upgrade')
        self.clock = pygame.time.Clock()
        
        # --- STATE MACHINE ---
        self.state = 'game'  # Can be 'menu', 'game', 'pause', etc.
        
        self.game = Game()
        self.running = True

    def run(self):
        while self.running:
            # Calculate Delta Time (dt)
            dt = self.clock.tick(FPS) / 1000.0
            
            # Event Loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False

            # State Machine Routing
            if self.state == 'menu':
                pass # self.main_menu.update()
            elif self.state == 'game':
                self.game.run(dt)
            elif self.state == 'pause':
                pass # self.pause_menu.update()

            pygame.display.flip()
            
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game_manager = GameManager()
    game_manager.run()