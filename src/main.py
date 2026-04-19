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
        # Cursors
        try:
            self.cursor_out = pygame.image.load("../assets/cursors/out.png").convert_alpha()
            self.cursor_hover = pygame.image.load("../assets/cursors/hover.png").convert_alpha()
            self.cursor_click = pygame.image.load("../assets/cursors/click.png").convert_alpha()
            self.cursor_out = pygame.transform.scale(self.cursor_out, (32, 32))
            self.cursor_hover = pygame.transform.scale(self.cursor_hover, (32, 32))
            self.cursor_click = pygame.transform.scale(self.cursor_click, (32, 32))
        except FileNotFoundError:
            self.cursor_out = pygame.Surface((20, 20)); self.cursor_out.fill('white')
            self.cursor_hover = pygame.Surface((20, 20)); self.cursor_hover.fill('yellow')
            self.cursor_click = pygame.Surface((20, 20)); self.cursor_click.fill('green')

        # Gesture Icons
        self.gesture_icons = {}
        gesture_files = {
            "Move Left": ["../assets/handGestures/Thumb-Index.png"],
            "Move Right": ["../assets/handGestures/Thumb-Pinky.png"],
            "Jump": ["../assets/handGestures/Open_Palm-removebg-preview.png"],
            "Attack": ["../assets/handGestures/Knuckle bend.png"],
            "Select/Click": ["../assets/handGestures/Fist.png"],
            "jump & move right" : ["../assets/handGestures/Thumb-Ring.png"],
            "jump & move left" : ["../assets/handGestures/Thumb-Middle.png"],
            "special barrier spell": ["../assets/handGestures/Fist.png", "../assets/handGestures/Karate Chop.png"]
        }
        for action, paths in gesture_files.items():
            try:
                
                imgs = [pygame.image.load(path).convert_alpha() for path in paths]
                imgs = [pygame.transform.scale(img, (60, 80)) for img in imgs]
                if action == "special barrier spell" or action == "Attack" or action == "Select/Click":
                    imgs = [pygame.transform.flip(img, True, False) for img in imgs]
                self.gesture_icons[action] = imgs
            except Exception as e:
                print(f"Error loading {paths}: {e}")
        
        self.knockback_timer = 0.0
        self.hand_cursor_pos = pygame.math.Vector2(0, 0)
        self.cursor_image = self.cursor_out
        self.cursor_rect = self.cursor_image.get_rect()
        self.font = pygame.font.Font(pygame.font.match_font(UI_FONT), 64)
        self.small_font = pygame.font.Font(pygame.font.match_font(UI_FONT), 32)
        
        self.state = 'menu'
        self.game = Game()
        self.running = True

        # Music Assets
        pygame.mixer.init()
        self.current_music = None
        self.music_game = "../assets/soundtracks/mondamusic-retro-arcade-game-music-512837.mp3"
        self.music_menu = "../assets/soundtracks/samc44-mother-transistion-scene-189070.mp3"
        self.music_lose = "../assets/soundtracks/floraphonic-classic-game-action-negative-18-224576.mp3"

        # Menu Buttons
        button_w, button_h = 400, 80
        self.start_button = pygame.Rect(WINDOW_WIDTH//2 - button_w//2, WINDOW_HEIGHT//2 - 100, button_w, button_h)
        self.controls_button = pygame.Rect(WINDOW_WIDTH//2 - button_w//2, WINDOW_HEIGHT//2 + 20, button_w, button_h)
        self.back_button = pygame.Rect(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 280, 150, 50)

    def play_music(self, path, loops=-1):
        if self.current_music == path:
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(loops)
            pygame.mixer.music.set_volume(0.1)
            self.current_music = path
        except Exception as e:
            print(f"Could not play music {path}: {e}")

    def draw_button(self, rect, text, color, hover_color):
        # Check both real mouse and hand cursor
        is_hovered = rect.collidepoint(pygame.mouse.get_pos()) or \
                     (self.state in ['menu', 'controls'] and rect.collidepoint(self.hand_cursor_pos))
        
        if is_hovered:
            pygame.draw.rect(self.display, hover_color, rect, border_radius=15)
        else:
            pygame.draw.rect(self.display, color, rect, border_radius=15)
        
        pygame.draw.rect(self.display, 'white', rect, 3, border_radius=15)
        
        surf = self.small_font.render(text, True, 'white')
        rect_text = surf.get_rect(center=rect.center)
        self.display.blit(surf, rect_text)

    def draw_menu(self):
        self.display.fill(BG_COLOR)
        
        # Camera Preview
        if self.cv_controller and self.cv_controller.surface:
            pip_surf = pygame.transform.scale(self.cv_controller.surface, (240, 180))
            self.display.blit(pip_surf, (20, 20))
            pygame.draw.rect(self.display, 'white', (20, 20, 240, 180), 2)

        title_surf = self.font.render('NINJA FROG REHAB', True, TEXT_COLOR)
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//4))
        self.display.blit(title_surf, title_rect)
        
        self.draw_button(self.start_button, 'START GAME', '#2E8B57', '#3CB371')
        self.draw_button(self.controls_button, 'CONTROLS', '#4682B4', '#5F9EA0')

    def draw_controls(self):
        self.display.fill('#FAF9F6') # Off-white
        
        # Camera Preview
        if self.cv_controller and self.cv_controller.surface:
            pip_surf = pygame.transform.scale(self.cv_controller.surface, (240, 180))
            self.display.blit(pip_surf, (20, 20))
            pygame.draw.rect(self.display, '#333333', (20, 20, 240, 180), 2)

        title_surf = self.font.render('Hand Gesture Controls', True, '#333333')
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH//2, 100))
        self.display.blit(title_surf, title_rect)
        
        controls = [
            ("Move Left", "Thumb & Index", "Move Left"),
            ("Move Right", "Thumb & Pinky", "Move Right"),
            ("Jump", "Open Palm", "Jump"),
            ("Jump & Right", "Thumb & Ring", "jump & move right"),
            ("Jump & Left", "Thumb & Middle", "jump & move left"),
            ("Attack", "Knuckle Bend", "Attack"),
            ("Barrier", "Fist + Chop", "special barrier spell"),
            ("Select", "Fist", "Select/Click")
        ]
        
        start_y = 220
        # Two columns layout
        left_col_x = WINDOW_WIDTH // 8
        right_col_x = WINDOW_WIDTH // 2 + 50
        
        for i, (action_disp, gesture_name, action_key) in enumerate(controls):
            col = i % 2
            row = i // 2
            
            y_pos = start_y + row * 110
            base_x = right_col_x if col == 1 else left_col_x
            
            action_surf = self.small_font.render(f"{action_disp}:", True, '#2C5282')
            gesture_surf = self.small_font.render(gesture_name, True, '#222222')
            
            # Action text
            self.display.blit(action_surf, (base_x, y_pos))
            
            # Icons
            offsets = 0
            if action_key in self.gesture_icons:
                for icon in self.gesture_icons[action_key]:
                    self.display.blit(icon, (base_x + 230 + offsets, y_pos - 25))
                    offsets += icon.get_width() + 10
            
            # Gesture name
            self.display.blit(gesture_surf, (base_x + 230 + offsets + 20, y_pos))
            
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
            
            # --- Hand Interaction Logic ---
            if self.state in ['menu', 'controls']:
                self.cv_controller.process_frame()
                self.hand_cursor_pos.x = self.cv_controller.hand_pos.x * WINDOW_WIDTH
                self.hand_cursor_pos.y = self.cv_controller.hand_pos.y * WINDOW_HEIGHT
                self.cursor_rect.center = self.hand_cursor_pos
                
                # Check hover and click
                buttons = []
                if self.state == 'menu': buttons = [self.start_button, self.controls_button]
                elif self.state == 'controls': buttons = [self.back_button]
                
                any_hover = False
                for btn in buttons:
                    if btn.collidepoint(self.hand_cursor_pos):
                        any_hover = True
                        if self.cv_controller.is_clicking:
                            self.cursor_image = self.cursor_click
                            # Trigger Click
                            if self.state == 'menu':
                                if btn == self.start_button:
                                    self.game = Game()
                                    self.state = 'game'
                                elif btn == self.controls_button:
                                    self.state = 'controls'
                            elif self.state == 'controls':
                                if btn == self.back_button:
                                    self.state = 'menu'
                        else:
                            self.cursor_image = self.cursor_hover
                        break
                
                if not any_hover:
                    self.cursor_image = self.cursor_out

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
                self.play_music(self.music_menu)
                self.draw_menu()
            elif self.state == 'controls':
                self.play_music(self.music_menu)
                self.draw_controls()
            elif self.state == 'game':
                self.play_music(self.music_game)
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
                self.play_music(self.music_lose, loops=0)
                self.draw_game_over()
            elif self.state == 'victory':
                self.play_music(self.music_menu)
                self.draw_victory()

            # Draw Hand Cursor
            if self.state in ['menu', 'controls']:
                self.display.blit(self.cursor_image, self.cursor_rect)

            pygame.display.flip()
            
        self.cv_controller.release()
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game_manager = GameManager()
    game_manager.run()
