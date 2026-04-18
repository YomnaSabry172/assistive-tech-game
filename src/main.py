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
        self.small_font = pygame.font.Font(pygame.font.match_font(UI_FONT), 32)
        
        self.state = 'menu'
        self.game = Game()
        self.running = True

        # Menu Buttons
        button_w, button_h = 400, 80
        self.start_button = pygame.Rect(WINDOW_WIDTH//2 - button_w//2, WINDOW_HEIGHT//2 - 100, button_w, button_h)
        self.controls_button = pygame.Rect(WINDOW_WIDTH//2 - button_w//2, WINDOW_HEIGHT//2 + 20, button_w, button_h)
        self.back_button = pygame.Rect(50, 50, 150, 50)

    def draw_button(self, rect, text, color, hover_color):
        mouse_pos = pygame.mouse.get_pos()
        if rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.display, hover_color, rect, border_radius=15)
        else:
            pygame.draw.rect(self.display, color, rect, border_radius=15)
        
        pygame.draw.rect(self.display, 'white', rect, 3, border_radius=15)
        
        surf = self.small_font.render(text, True, 'white')
        rect_text = surf.get_rect(center=rect.center)
        self.display.blit(surf, rect_text)

    def draw_menu(self):
        self.display.fill('#242424')
        
        title_surf = self.font.render('NINJA FROG REHAB', True, '#00FF7F')
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//4))
        self.display.blit(title_surf, title_rect)
        
        self.draw_button(self.start_button, 'START GAME', '#2E8B57', '#3CB371')
        self.draw_button(self.controls_button, 'CONTROLS', '#4682B4', '#5F9EA0')

    def draw_controls(self):
        self.display.fill('#1A1A1A')
        
        title_surf = self.font.render('GESTURE CONTROLS', True, 'gold')
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH//2, 100))
        self.display.blit(title_surf, title_rect)
        
        controls = [
            ("Move Left", "Move hand to the LEFT side of the screen"),
            ("Move Right", "Move hand to the RIGHT side of the screen"),
            ("Jump", "Show an OPEN PALM to the camera"),
            ("Quit", "Press ESC to return to menu/quit")
        ]
        
        start_y = 250
        for i, (action, gesture) in enumerate(controls):
            action_surf = self.small_font.render(f"{action}:", True, 'lightblue')
            gesture_surf = self.small_font.render(gesture, True, 'white')
            
            self.display.blit(action_surf, (WINDOW_WIDTH//4, start_y + i * 80))
            self.display.blit(gesture_surf, (WINDOW_WIDTH//4 + 250, start_y + i * 80))
            
        self.draw_button(self.back_button, 'BACK', '#8B0000', '#CD5C5C')

    def draw_game_over(self):
        # Dim the screen
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(150)
        self.display.blit(overlay, (0, 0))

        # Text Setup
        go_surf = self.font.render('GAME OVER', True, 'red')
        go_rect = go_surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
        
        rest_surf = self.small_font.render('Press R to Restart or ESC to Menu', True, 'white')
        rest_rect = rest_surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50))

        score_surf = self.small_font.render(f'Final Score: {self.game.score}', True, 'yellow')
        score_rect = score_surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 100))

        self.display.blit(go_surf, go_rect)
        self.display.blit(rest_surf, rest_rect)
        self.display.blit(score_surf, score_rect)
        
        stats = self.cv_controller.stats
        stats_font = pygame.font.Font(pygame.font.match_font(UI_FONT), 24)
        
        stat_texts = [
            f"Active Time: {stats['active_time']:.1f}s",
            f"Total Jumps: {stats['jumps']}",
            f"Left Moves: {stats['left_moves']}  |  Right Moves: {stats['right_moves']}"
        ]
        
        base_y = WINDOW_HEIGHT//2 + 170
        for i, text in enumerate(stat_texts):
            surf = stats_font.render(text, True, 'lightblue')
            rect = surf.get_rect(center=(WINDOW_WIDTH//2, base_y + i * 35))
            self.display.blit(surf, rect)

    def draw_victory(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        self.display.blit(overlay, (0, 0))

        v_surf = self.font.render('VICTORY!', True, 'gold')
        v_rect = v_surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
        
        score_surf = self.small_font.render(f'Total Score: {self.game.score}', True, 'yellow')
        score_rect = score_surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50))

        rest_surf = self.small_font.render('Press R to Play Again or ESC to Menu', True, 'white')
        rest_rect = rest_surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 100))

        self.display.blit(v_surf, v_rect)
        self.display.blit(score_surf, score_rect)
        self.display.blit(rest_surf, rest_rect)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state in ['game', 'game_over', 'victory']:
                            self.state = 'menu'
                        else:
                            self.running = False
                    
                    if event.key == pygame.K_r and self.state in ['game_over', 'victory']:
                        self.game = Game()
                        self.state = 'game'

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == 'menu':
                        if self.start_button.collidepoint(event.pos):
                            self.game = Game()
                            self.state = 'game'
                        elif self.controls_button.collidepoint(event.pos):
                            self.state = 'controls'
                    elif self.state == 'controls':
                        if self.back_button.collidepoint(event.pos):
                            self.state = 'menu'

            # --- State Routing ---
            if self.state == 'menu':
                self.draw_menu()
            elif self.state == 'controls':
                self.draw_controls()
            elif self.state == 'game':
                self.cv_controller.process_frame()
                status = self.game.run(dt, self.cv_controller)
                
                if status == "game_over":
                    self.state = 'game_over'
                elif status == "next_level":
                    # Transition to next level
                    new_score = self.game.score
                    self.game = Game(self.game.level_index + 1)
                    self.game.score = new_score
                elif status == "victory":
                    self.state = 'victory'
            
            elif self.state == 'game_over':
                self.draw_game_over()
            elif self.state == 'victory':
                self.draw_victory()

            pygame.display.flip()
            
        self.cv_controller.release()
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game_manager = GameManager()
    game_manager.run()