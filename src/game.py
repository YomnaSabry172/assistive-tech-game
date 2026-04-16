import pygame
from settings import *
from sprites import CameraGroup, Tile
from player import Player

# Helper Function to extract and scale tiles
def get_tile(sheet, x, y, width, height, scale):
    image = pygame.Surface((width, height), pygame.SRCALPHA)
    image.blit(sheet, (0, 0), (x, y, width, height))
    return pygame.transform.scale(image, (width * scale, height * scale))

class Game:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        
        # Sprite Groups
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()

        # Load and slice the terrain sprite sheet
        terrain_sheet = pygame.image.load("../assets/Terrain/Terrain (16x16).png").convert_alpha()
        scale_factor = TILE_SIZE // 16 # Scales 16px to 48px
        
        self.tiles = {
            'G': get_tile(terrain_sheet, 96, 0, 16, 16, scale_factor),   # Grass
            'D': get_tile(terrain_sheet, 96, 16, 16, 16, scale_factor),  # Dirt
            'P': get_tile(terrain_sheet, 192, 0, 16, 16, scale_factor),  # Pyramid/Block
            'O': get_tile(terrain_sheet, 96, 96, 16, 16, scale_factor)   # Slime/Spike
        }

        self.setup_level()

    def setup_level(self):
        level_map = [
            "...................",
            "...................",
            "...................",
            ".......P...........",
            ".......P...........",
            ".......P...........",
            "...................",
            "...................",
            ".......GGGG........",
            "....GGGDDDD........",
            "OOOODDDDDDD...GGGGG",
            "OOOODDDDDDD...DDDDD",
            "OOOODDDDDDD...DDDDD"
        ]

        for row_index, row in enumerate(level_map):
            for col_index, char in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE
                
                if char != '.':
                    # Get the correct image from our dictionary
                    tile_image = self.tiles.get(char)
                    if tile_image:
                        Tile((self.all_sprites, self.collision_sprites), tile_image, (x, y))

        # Spawn Player
        self.player = Player((self.all_sprites,), (100, 100), self.collision_sprites)

    def run(self, dt):
        # 1. Update everything
        self.all_sprites.update(dt)

        # 2. Draw everything using the dynamic camera
        self.all_sprites.custom_draw(self.player)