# main.py
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
        self.font = pygame.font.Font(pygame.font.match_font(UI_FONT), 64)
        
        self.state = 'game'
        self.game = Game()
        self.running = True

    def draw_game_over(self):
        # Dim the screen
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(150)
        self.display.blit(overlay, (0, 0))

        # Text Setup
        go_surf = self.font.render('GAME OVER', True, 'red')
        go_rect = go_surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
        
        restart_font = pygame.font.Font(pygame.font.match_font(UI_FONT), 32)
        rest_surf = restart_font.render('Press R to Restart or ESC to Quit', True, 'white')
        rest_rect = rest_surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50))

        score_surf = restart_font.render(f'Final Score: {self.game.score}', True, 'yellow')
        score_rect = score_surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 100))

        self.display.blit(go_surf, go_rect)
        self.display.blit(rest_surf, rest_rect)
        self.display.blit(score_surf, score_rect)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    # Restart Logic
                    if event.key == pygame.K_r and self.state == 'game_over':
                        self.game = Game() # Reset the game instance
                        self.state = 'game'

            # --- State Routing ---
            if self.state == 'game':
                # self.game.run(dt) returns False if the player hits a hazard
                is_alive = self.game.run(dt)
                if not is_alive:
                    self.state = 'game_over'
            
            elif self.state == 'game_over':
                self.draw_game_over()

            pygame.display.flip()
            
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game_manager = GameManager()
    game_manager.run()