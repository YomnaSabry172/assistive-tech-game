# game.py
import pygame
from settings import *
from sprites import CameraGroup, Tile, Fruit, Enemy, Trap
from player import Player

def get_tile(sheet, x, y, width, height, scale):
    image = pygame.Surface((width, height), pygame.SRCALPHA)
    image.blit(sheet, (0, 0), (x, y, width, height))
    return pygame.transform.scale(image, (width * scale, height * scale))

class Game:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(pygame.font.match_font(UI_FONT), UI_FONT_SIZE)
        
        # Sprite Groups
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        
        # New Groups for interaction
        self.fruit_sprites = pygame.sprite.Group()
        self.hazard_sprites = pygame.sprite.Group() # Enemies + Traps

        # Game Stats
        self.score = 0
        
        # Load and slice the terrain sprite sheet
        try:
            terrain_sheet = pygame.image.load("../assets/Terrain/t.png").convert_alpha()
            scale_factor = TILE_SIZE // 16 
            
            # --- THE COMPLETE TERRAIN DICTIONARY ---
            self.tiles = {
                # --- Grass Variants (Standalone 1x1 blocks) ---
                'g': get_tile(terrain_sheet, 160, 0, 16, 16, scale_factor),   # Green Grass
                'o': get_tile(terrain_sheet, 160, 96, 16, 16, scale_factor),  # Orange Grass
                'p': get_tile(terrain_sheet, 160, 192, 16, 16, scale_factor), # Pink Grass

                # --- Dirt Variants (Center repeating blocks) ---
                'd': get_tile(terrain_sheet, 112, 16, 16, 16, scale_factor),  # Brown Dirt
                'u': get_tile(terrain_sheet, 112, 112, 16, 16, scale_factor), # Orange Dirt
                'b': get_tile(terrain_sheet, 112, 208, 16, 16, scale_factor), # Pink Dirt

                # --- Solid Blocks (Solid 2x2 clusters) ---
                'S': get_tile(terrain_sheet, 64, 16, 16, 16, scale_factor),   # Gray Stone
                'W': get_tile(terrain_sheet, 64, 112, 16, 16, scale_factor),  # Wood Block
                'C': get_tile(terrain_sheet, 64, 208, 16, 16, scale_factor),  # Cyan Stone
                
                # --- Bricks & Gold ---
                'R': get_tile(terrain_sheet, 304, 112, 16, 16, scale_factor), # Red Brick
                'G': get_tile(terrain_sheet, 288, 208, 16, 16, scale_factor), # Gold Block
                
                # --- Squares & Pyramids (Standalone 1x1 bases) ---
                'P': get_tile(terrain_sheet, 192, 16, 16, 16, scale_factor),  # Pyramid Base
                'Y': get_tile(terrain_sheet, 192, 112, 16, 16, scale_factor), # Gray Square
                'O': get_tile(terrain_sheet, 192, 208, 16, 16, scale_factor), # Orange Square
                
                # --- Platforms ---
                '-': get_tile(terrain_sheet, 304, 0, 16, 16, scale_factor)    # Yellow Bridge
            }
        except FileNotFoundError:
            print("Error: Could not find t.png at the specified path.")
            self.tiles = {}
    
        self.setup_level()

    def setup_level(self):
        level_map = [
            "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",
            "PP......................................***.......................PP",
            "PP.....................................GGGGG......................PP",
            "PP.......................*.............RRRRR...................B..PP",
            "PP......................---.......................................PP",
            "PP................................---.............................PP",
            "PP..........*..........................................*..........PP",
            "PP.........---............B...............oo........M.---.........PP",
            "PP....................................oo..........pppppppp........PP",
            "PP..*................M........*....oo.........P...bbbbbbbb........PP",
            "PP............P....ooooooooo.---.............P.P..bbbbbbbb........PP",
            "PP.---.......P.P.........................g..P...P.bbbbbbbb........PP",
            "PP..........P...P.............XX.........d.P.....Pbbbbbbbb..W..C..PP",
            "PP.........P.....P...........gggg........d.PPPPPPPbbbbbbbb..W..C..PP",
            "PP.dddddd.PPPPPPPP...........dddd........d.dddddddbbbbbbbb..W..C..PP",
            "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP"
        ]

        for row_index, row in enumerate(level_map):
            for col_index, char in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE
                
                # THE FIX: Only check if the character is a key in the tiles dictionary!
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

        self.player = Player((self.all_sprites,), (100, 100), self.collision_sprites)

    def check_collisions(self):
        # Check fruit pickup
        collided_fruits = pygame.sprite.spritecollide(self.player, self.fruit_sprites, True)
        if collided_fruits:
            self.score += 100 * len(collided_fruits)
            # Future enhancement: Spawn the Collected.png animation here!

        # Check hazards (Enemies and Traps)
        if pygame.sprite.spritecollide(self.player, self.hazard_sprites, False, collided = lambda spr1, spr2: spr1.hitbox.colliderect(spr2.hitbox)):
            return False # Player died!

        return True # Player is alive

    def draw_ui(self):
        score_surf = self.font.render(f'SCORE: {self.score}', True, TEXT_COLOR)
        score_rect = score_surf.get_rect(topleft=(20, 20))
        self.display_surface.blit(score_surf, score_rect)

    def run(self, dt):
        # Update
        self.all_sprites.update(dt)

        # Collisions logic (return False if dead)
        is_alive = self.check_collisions()

        # Draw
        self.all_sprites.custom_draw(self.player)
        self.draw_ui()

        return is_alive