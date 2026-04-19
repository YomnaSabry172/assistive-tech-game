# game.py
import pygame
from settings import *
from sprites import CameraGroup, Tile, Fruit, Enemy, Trap, Goal
from player import Player
from levels import LEVELS

def get_tile(sheet, x, y, width, height, scale):
    image = pygame.Surface((width, height), pygame.SRCALPHA)
    image.blit(sheet, (0, 0), (x, y, width, height))
    return pygame.transform.scale(image, (width * scale, height * scale))

class Game:
    def __init__(self, level_index=0):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(pygame.font.match_font(UI_FONT), UI_FONT_SIZE)
        
        self.level_index = level_index
        self.max_levels = len(LEVELS)
        self.game_over = False
        self.victory = False

        # Sprite Groups
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        self.fruit_sprites = pygame.sprite.Group()
        self.hazard_sprites = pygame.sprite.Group()
        self.goal_sprites = pygame.sprite.Group()

        # Game Stats
        self.score = 0
        
        # Load and slice the terrain sprite sheet
        try:
            terrain_sheet = pygame.image.load("../assets/Terrain/Terrain (16x16).png").convert_alpha()
            scale_factor = TILE_SIZE // 16 
            
            self.tiles = {
                'g': get_tile(terrain_sheet, 160, 0, 16, 16, scale_factor),
                'o': get_tile(terrain_sheet, 160, 96, 16, 16, scale_factor),
                'p': get_tile(terrain_sheet, 160, 192, 16, 16, scale_factor),
                'd': get_tile(terrain_sheet, 112, 16, 16, 16, scale_factor),
                'u': get_tile(terrain_sheet, 112, 112, 16, 16, scale_factor),
                'b': get_tile(terrain_sheet, 112, 208, 16, 16, scale_factor),
                'S': get_tile(terrain_sheet, 64, 16, 16, 16, scale_factor),
                'W': get_tile(terrain_sheet, 64, 112, 16, 16, scale_factor),
                'C': get_tile(terrain_sheet, 64, 208, 16, 16, scale_factor),
                'R': get_tile(terrain_sheet, 304, 112, 16, 16, scale_factor),
                'G': get_tile(terrain_sheet, 288, 208, 16, 16, scale_factor),
                'P': get_tile(terrain_sheet, 192, 16, 16, 16, scale_factor),
                'Y': get_tile(terrain_sheet, 192, 112, 16, 16, scale_factor),
                'O': get_tile(terrain_sheet, 192, 144, 16, 16, scale_factor),
                '-': get_tile(terrain_sheet, 304, 0, 16, 16, scale_factor)
            }
        except FileNotFoundError:
            self.tiles = {}
    
        self.setup_level()

    def setup_level(self):
        level_map = LEVELS[self.level_index]

        for row_index, row in enumerate(level_map):
            for col_index, char in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE
                
                if char in self.tiles:
                    Tile((self.all_sprites, self.collision_sprites), self.tiles[char], (x, y))
                elif char == '*':
                    Fruit((self.all_sprites, self.fruit_sprites), (x, y))
                elif char == 'M':
                    Enemy((self.all_sprites, self.hazard_sprites), (x, y))
                elif char == 'X':
                    Trap((self.all_sprites, self.hazard_sprites), (x, y), 'spike')
                elif char == 'B':
                    Trap((self.all_sprites, self.hazard_sprites), (x, y), 'ball')
                elif char == 'E':
                    Goal((self.all_sprites, self.goal_sprites), (x, y))

        self.player = Player((self.all_sprites,), (150, 650), self.collision_sprites)

    def check_collisions(self, dt):
        # Check fruit pickup
        collided_fruits = pygame.sprite.spritecollide(self.player, self.fruit_sprites, True)
        if collided_fruits:
            self.score += 100 * len(collided_fruits)

        # Check hazards
        if pygame.sprite.spritecollide(self.player, self.hazard_sprites, False, collided = lambda spr1, spr2: spr1.hitbox.colliderect(spr2.hitbox)) and (pygame.time.get_ticks() - self.player.last_hit_time >= self.player.hit_cooldown):
            if self.player.lives > 1:
                self.player.lives -= 1
                self.player.status = "hit"
                self.player.last_hit_time = pygame.time.get_ticks()
                self.player.animate(dt)
                print(self.player.lives)

                
            else:
                return "death"

        # Check Goal
        if pygame.sprite.spritecollide(self.player, self.goal_sprites, False, collided = lambda spr1, spr2: spr1.hitbox.colliderect(spr2.hitbox)):
            if not self.fruit_sprites:
                return "goal"
            else:
                return "locked_goal"

        return "alive"

    def draw_ui(self, cv_controller=None):
        score_surf = self.font.render(f'SCORE: {self.score} | LEVEL: {self.level_index + 1}', True, TEXT_COLOR)
        score_rect = score_surf.get_rect(topleft=(30, 20))
        self.display_surface.blit(score_surf, score_rect)
        
        if cv_controller and cv_controller.surface:
            pip_w, pip_h = 320, 240
            pip_surf = pygame.transform.scale(cv_controller.surface, (pip_w, pip_h))
            x, y = WINDOW_WIDTH - pip_w - 20, WINDOW_HEIGHT - pip_h - 20
            pygame.draw.rect(self.display_surface, (255, 215, 0), (x-2, y-2, pip_w+4, pip_h+4), 2)
            self.display_surface.blit(pip_surf, (x, y))

            gesture_surf = self.font.render(f'GESTURE: {cv_controller.gesture_label}', True, 'white')
            gesture_rect = gesture_surf.get_rect(bottomleft=(x, y - 10))
            pygame.draw.rect(self.display_surface, (0, 0, 0, 150), gesture_rect.inflate(10, 5))
            self.display_surface.blit(gesture_surf, gesture_rect)

    def run(self, dt, cv_controller=None):
        if cv_controller:
            self.player.cv_direction_x = cv_controller.direction_x
            self.player.cv_jump = cv_controller.jump
            
        self.all_sprites.update(dt)
        
        # Unlock goal if all fruits are collected
        if not self.fruit_sprites:
            for goal in self.goal_sprites:
                if hasattr(goal, 'unlock'):
                    goal.unlock()

        status = self.check_collisions(dt)

        if status == "death":
            return "game_over"
        elif status == "goal":
            if self.level_index + 1 < self.max_levels:
                return "next_level"
            else:
                return "victory"

        self.all_sprites.custom_draw(self.player)
        self.draw_ui(cv_controller)
        return "playing"
