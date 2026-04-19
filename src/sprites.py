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
            self.bg_tile = pygame.image.load("../assets/Background/Brown.png").convert()
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

class Enemy(pygame.sprite.Sprite):
    def __init__(self, groups, pos, collision_sprites):
        super().__init__(groups)
        self.import_assets()
        self.status = 'idle'
        self.frame_index = 0
        self.animation_speed = 12
        
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(bottomleft=(pos[0], pos[1] + TILE_SIZE))
        self.hitbox = self.rect.inflate(-10, -10)
        
        # Movement
        self.direction = 1
        self.speed = 100
        self.collision_sprites = collision_sprites

    def import_assets(self):
        self.animations = {'idle': [], 'run': []}
        path = "../assets/Main Characters/Mask Dude/"
        
        for state in self.animations.keys():
            full_path = f"{path}{state.title()} (32x32).png"
            self.animations[state] = import_sprite_sheet(full_path, 32, 32, 1.5)

    def animate(self, dt):
        animation = self.animations[self.status]
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(animation):
            self.frame_index = 0
            
        current_frame = animation[int(self.frame_index)]
        if self.direction < 0:
            self.image = pygame.transform.flip(current_frame, True, False)
        else:
            self.image = current_frame

    def get_status(self):
        self.status = 'run' if self.speed > 0 else 'idle'

    def check_edges(self):
        # Look ahead to see if there is floor
        look_dist = 20
        sensor_x = self.hitbox.centerx + (self.direction * look_dist)
        sensor_y = self.hitbox.bottom + 10
        
        has_floor = False
        for sprite in self.collision_sprites:
            if sprite.rect.collidepoint(sensor_x, sensor_y):
                has_floor = True
                break
        
        # Check for walls
        hit_wall = False
        wall_sensor_x = self.hitbox.centerx + (self.direction * 20)
        wall_sensor_y = self.hitbox.centery
        for sprite in self.collision_sprites:
            if sprite.rect.collidepoint(wall_sensor_x, wall_sensor_y):
                hit_wall = True
                break

        if not has_floor or hit_wall:
            return True # Should turn
        return False

    def move(self, dt):
        if self.check_edges():
            self.direction *= -1

        self.hitbox.x += self.direction * self.speed * dt
        self.rect.centerx = self.hitbox.centerx

    def update(self, dt):
        self.move(dt)
        self.get_status()
        self.animate(dt)

    def update(self, dt):
        self.move(dt)
        self.get_status()
        self.animate(dt)

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

class Goal(pygame.sprite.Sprite):
    def __init__(self, groups, pos):
        super().__init__(groups)
        try:
            self.unlocked_image = pygame.image.load("../assets/Items/Checkpoints/End/End (Idle).png").convert_alpha()
            self.unlocked_image = pygame.transform.scale(self.unlocked_image, (TILE_SIZE, TILE_SIZE))
        except:
            self.unlocked_image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.unlocked_image.fill('gold')
        
        # Locked state visual (Semi-transparent)
        self.locked_image = self.unlocked_image.copy()
        self.locked_image.set_alpha(100)
        
        self.image = self.locked_image
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-10, -10)
        self.locked = True

    def unlock(self):
        if self.locked:
            self.image = self.unlocked_image
            self.locked = False

class Box(pygame.sprite.Sprite):
    def __init__(self, groups, pos):
        super().__init__(groups)
        self.import_assets()
        self.status = 'idle'
        self.frame_index = 0
        self.animation_speed = 10
        
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, 0)
        
        self.health = 3
        self.is_broken = False

    def import_assets(self):
        self.animations = {'idle': [], 'hit': [], 'break': []}
        path = "../assets/Items/Boxes/Box1/"
        
        # Idle (single frame or simple sheet)
        try:
            idle_sheet = pygame.image.load(path + "Idle.png").convert_alpha()
            self.animations['idle'] = [pygame.transform.scale(idle_sheet, (TILE_SIZE, TILE_SIZE))]
        except: pass
        
        # Hit (28x24)
        try:
            self.animations['hit'] = import_sprite_sheet(path + "Hit (28x24).png", 28, 24, TILE_SIZE/28)
        except: pass
        
        # Break (standard size sheet)
        try:
            self.animations['break'] = import_sprite_sheet(path + "Break.png", 28, 24, TILE_SIZE/28)
        except: pass

    def hit(self):
        if not self.is_broken:
            self.health -= 1
            if self.health <= 0:
                self.is_broken = True
                self.status = 'break'
                self.frame_index = 0
            else:
                self.status = 'hit'
                self.frame_index = 0

    def animate(self, dt):
        animation = self.animations[self.status]
        if not animation: return
        
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(animation):
            if self.status == 'break':
                self.kill()
            else:
                self.status = 'idle'
                self.frame_index = 0
        
        self.image = animation[int(self.frame_index) % len(animation)]

    def update(self, dt):
        self.animate(dt)

class Barrier(pygame.sprite.Sprite):
    def __init__(self, groups, pos):
        super().__init__(groups)
        self.import_assets()
        self.status = 'idle'
        self.frame_index = 0
        self.animation_speed = 10
        
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, 0)
        
        self.health = 1
        self.is_broken = False

    def import_assets(self):
        self.animations = {'idle': [], 'hit': [], 'break': []}
        path = "../assets/Items/Boxes/Box3/"
        
        # Idle
        try:
            idle_sheet = pygame.image.load(path + "Idle.png").convert_alpha()
            self.animations['idle'] = [pygame.transform.scale(idle_sheet, (TILE_SIZE, TILE_SIZE))]
        except: pass
        
        # Hit (28x24)
        try:
            self.animations['hit'] = import_sprite_sheet(path + "Hit (28x24).png", 28, 24, TILE_SIZE/28)
        except: pass
        
        # Break (28x24)
        try:
            self.animations['break'] = import_sprite_sheet(path + "Break.png", 28, 24, TILE_SIZE/28)
        except: pass

    def hit(self, is_special=False):
        if is_special and not self.is_broken:
            self.health -= 1
            if self.health <= 0:
                self.is_broken = True
                self.status = 'break'
                self.frame_index = 0
        elif not is_special:
            # Maybe a small "shiver" or "hit" animation even if it doesn't break?
            # User didn't ask for it, but it adds polish.
            self.status = 'hit'
            self.frame_index = 0

    def animate(self, dt):
        animation = self.animations[self.status]
        if not animation: return
        
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(animation):
            if self.status == 'break':
                self.kill()
            else:
                self.status = 'idle'
                self.frame_index = 0
        
        self.image = animation[int(self.frame_index) % len(animation)]

    def update(self, dt):
        self.animate(dt)

class Spell(pygame.sprite.Sprite):
    def __init__(self, groups, pos, direction, collision_sprites, is_special=False, target=None):
        super().__init__(groups)
        self.direction_val = direction # 1 or -1
        self.direction = pygame.math.Vector2(direction, 0)
        self.is_special = is_special
        self.target = target
        self.speed = 500
        self.collision_sprites = collision_sprites
        self.spawn_time = pygame.time.get_ticks()
        self.grace_period = 200 # ms
        self.distance_traveled = 0
        self.spawn_pos = pygame.math.Vector2(pos)
        
        # Animations
        self.frames_appear = import_sprite_sheet("../assets/Main Characters/Appearing (96x96).png", 96, 96, 0.75 if is_special else 0.5)
        self.frames_disappear = import_sprite_sheet("../assets/Main Characters/Desappearing (96x96).png", 96, 96, 0.75 if is_special else 0.5)
        
        self.status = 'appear'
        self.active = True
        self.frames = self.frames_appear
        self.frame_index = 0
        self.animation_speed = 20
        
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        # Use a very small hitbox for the "magic core" to avoid hitting floors accidentally
        self.hitbox = self.rect.inflate(-60, -60) if is_special else self.rect.inflate(-20, -20)
        self.pos = pygame.math.Vector2(self.rect.center)

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(self.frames):
            if self.status == 'appear':
                self.status = 'moving'
                self.frame_index = len(self.frames) - 1 
            elif self.status == 'disappear':
                self.kill()
            else:
                self.frame_index = 0
        
        idx = int(self.frame_index)
        if idx >= len(self.frames): idx = len(self.frames) - 1
        
        current_frame = self.frames[idx]
        if self.is_special:
            # Apply Purple Tint for special spell
            temp_surface = current_frame.copy()
            temp_surface.fill((100, 0, 150), special_flags=pygame.BLEND_RGB_ADD)
            self.image = temp_surface
        else:
            self.image = current_frame

        if self.direction.x < 0:
            self.image = pygame.transform.flip(self.image, True, False)

    def move(self, dt):
        if self.status == 'moving' or self.status == 'appear':
            if self.is_special and self.target and self.target.alive():
                # Homing logic: update direction towards target
                target_vec = (pygame.math.Vector2(self.target.rect.center) - self.pos)
                if target_vec.length() > 0:
                    self.direction = target_vec.normalize()
            
            self.pos += self.direction * self.speed * dt
            self.rect.center = (round(self.pos.x), round(self.pos.y))
            self.hitbox.center = self.rect.center
            
            # Track distance and kill if range exceeded (special only?)
            # Actually, let's limit ALL spells to a reasonable range if we want,
            # but user specifically asked for special spell range.
            self.distance_traveled = self.spawn_pos.distance_to(self.pos)
            if self.is_special and self.distance_traveled > SPECIAL_SPELL_RANGE:
                self.status = 'disappear'
                self.frames = self.frames_disappear
                self.frame_index = 0
            
            # Simple collision with walls (destruction)
            # Only check after grace period to prevent instant explosion on spawn/floor
            if pygame.time.get_ticks() - self.spawn_time > self.grace_period:
                for sprite in self.collision_sprites:
                    if self.hitbox.colliderect(sprite.rect):
                        # Special spells only explode on non-Floor objects? No, normally any obstacle.
                        # But we specifically want to hitting Barriers.
                        self.status = 'disappear'
                        self.frames = self.frames_disappear
                        self.frame_index = 0
                        break

    def update(self, dt):
        self.move(dt)
        self.animate(dt)