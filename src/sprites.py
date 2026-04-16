# sprites.py
import pygame
from settings import *

# Helper function to slice any sprite sheet
def import_sprite_sheet(path, width, height, scale):
    try:
        sheet = pygame.image.load(path).convert_alpha()
        num_frames = sheet.get_width() // width
        frames = []
        for i in range(num_frames):
            frame = pygame.Surface((width, height), pygame.SRCALPHA)
            frame.blit(sheet, (0, 0), (i * width, 0, width, height))
            frame = pygame.transform.scale(frame, (width * scale, height * scale))
            frames.append(frame)
        return frames
    except FileNotFoundError:
        print(f"Error loading {path}. Returning empty red square.")
        surf = pygame.Surface((width * scale, height * scale))
        surf.fill('red')
        return [surf]

class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()
        self.half_w = self.display_surface.get_size()[0] // 2
        self.half_h = self.display_surface.get_size()[1] // 2

        try:
            self.bg_tile = pygame.image.load("Brown.png").convert()
            self.bg_w, self.bg_h = self.bg_tile.get_size()
        except FileNotFoundError:
            self.bg_tile = pygame.Surface((64, 64))
            self.bg_tile.fill('gray')
            self.bg_w, self.bg_h = (64, 64)

    def custom_draw(self, target):
        self.offset.x = target.rect.centerx - self.half_w
        self.offset.y = target.rect.centery - self.half_h

        start_x = -int(self.offset.x % self.bg_w)
        start_y = -int(self.offset.y % self.bg_h)
        
        for x in range(start_x, WINDOW_WIDTH, self.bg_w):
            for y in range(start_y, WINDOW_HEIGHT, self.bg_h):
                self.display_surface.blit(self.bg_tile, (x, y))

        for sprite in self.sprites():
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

class Tile(pygame.sprite.Sprite):
    def __init__(self, groups, image, pos):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)

# --- NEW ASSET CLASSES ---

class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, groups, pos, frames, animation_speed):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.animation_speed = animation_speed
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, dt):
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

class Fruit(AnimatedSprite):
    def __init__(self, groups, pos):
        # Assumes Strawberry.png frames are 32x32, scaling by 1.5 to match 48px tile size
        frames = import_sprite_sheet("../assets/Items/Fruits/Strawberry.png", 32, 32, 1.5)
        super().__init__(groups, pos, frames, 15)

# sprites.py

class Enemy(AnimatedSprite):
    def __init__(self, groups, pos):
        frames = import_sprite_sheet("../assets/Main Characters/Mask Dude/Idle (32x32).png", 32, 32, 1.5)
        super().__init__(groups, pos, frames, 12)
        # Rect for drawing
        self.rect = self.image.get_rect(bottomleft=(pos[0], pos[1] + TILE_SIZE))
        # Hitbox for dying (Shrink 20px horizontally, 10px vertically)
        self.hitbox = self.rect.inflate(-20, -10)
class Trap(pygame.sprite.Sprite):
    def __init__(self, groups, pos, trap_type):
        super().__init__(groups)
        if trap_type == 'spike':
            try:
                # Assuming Idle.png is a 16x16 spike trap
                img = pygame.image.load("../assets/Traps/Spikes/Idle.png").convert_alpha()
                self.image = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE // 2))
                self.rect = self.image.get_rect(bottomleft=(pos[0], pos[1] + TILE_SIZE))
                self.hitbox = self.rect.inflate(-24, -4) 
            except:
                self.image = pygame.Surface((TILE_SIZE, TILE_SIZE//2))
                self.image.fill('gray')
                self.rect = self.image.get_rect(bottomleft=(pos[0], pos[1] + TILE_SIZE))
                
        elif trap_type == 'ball':
            try:
                img = pygame.image.load("../assets/Traps/Spiked Ball/Spiked Ball.png").convert_alpha()
                self.image = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                self.rect = self.image.get_rect(center=(pos[0] + TILE_SIZE//2, pos[1] + TILE_SIZE//2))
                self.hitbox = self.rect.inflate(-16, -16)

            except:
                self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
                self.image.fill('gray')
                self.rect = self.image.get_rect(topleft=pos)