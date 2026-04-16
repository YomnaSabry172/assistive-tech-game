import pygame
from settings import *

class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()
        
        self.half_w = self.display_surface.get_size()[0] // 2
        self.half_h = self.display_surface.get_size()[1] // 2

        # Load Background Tile
        try:
            self.bg_tile = pygame.image.load("Brown.png").convert()
            self.bg_w, self.bg_h = self.bg_tile.get_size()
        except FileNotFoundError:
            # Fallback if image isn't found
            self.bg_tile = pygame.Surface((64, 64))
            self.bg_tile.fill('gray')
            self.bg_w, self.bg_h = (64, 64)

    def custom_draw(self, target):
        # 1. Calculate the offset based on the target (Player)
        self.offset.x = target.rect.centerx - self.half_w
        self.offset.y = target.rect.centery - self.half_h

        # 2. Draw Infinite Tiled Background
        # The math here ensures the tiles shift smoothly with the camera
        start_x = -int(self.offset.x % self.bg_w)
        start_y = -int(self.offset.y % self.bg_h)
        
        for x in range(start_x, WINDOW_WIDTH, self.bg_w):
            for y in range(start_y, WINDOW_HEIGHT, self.bg_h):
                self.display_surface.blit(self.bg_tile, (x, y))

        # 3. Draw everything with the offset applied
        for sprite in self.sprites():
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

class Tile(pygame.sprite.Sprite):
    def __init__(self, groups, image, pos):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)