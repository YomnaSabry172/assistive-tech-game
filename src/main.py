import pygame
import sys
from settings import *
from game import Game
from cv_controller import CVController

class GameManager:
    def __init__(self):
        self.cv_controller = CVController()
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
        
        stats = self.cv_controller.stats
        stats_font = pygame.font.Font(pygame.font.match_font(UI_FONT), 24)
        
        stat_texts = [
            f"Active Time: {stats['active_time']:.1f}s",
            f"Total Jumps: {stats['jumps']}",
            f"Max Openness: {stats['max_openness']:.2f}",
            f"Left Moves: {stats['left_moves']}  |  Right Moves: {stats['right_moves']}"
        ]
        
        base_y = WINDOW_HEIGHT//2 + 150
        for i, text in enumerate(stat_texts):
            surf = stats_font.render(text, True, 'lightblue')
            rect = surf.get_rect(center=(WINDOW_WIDTH//2, base_y + i * 35))
            self.display.blit(surf, rect)

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
                self.cv_controller.process_frame()
                # self.game.run(dt, self.cv_controller) returns False if the player hits a hazard
                is_alive = self.game.run(dt, self.cv_controller)
                if not is_alive:
                    self.state = 'game_over'
            
            elif self.state == 'game_over':
                self.draw_game_over()

            pygame.display.flip()
            
        self.cv_controller.release()
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game_manager = GameManager()
    game_manager.run()