import pygame
from settings import *
from sprites import Spell

class Player(pygame.sprite.Sprite):
    def __init__(self, groups, pos, collision_sprites, spell_sprites):
        super().__init__(groups)
        self.spell_sprites = spell_sprites
        
        # --- ANIMATION SETUP ---
        self.import_character_assets()
        self.frame_index = 0
        self.animation_speed = 15
        self.status = 'idle'      # The current state of the player
        self.facing_right = True  # Track which way to flip the image

        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-10, -30)
        
        # --- PHYSICS & MOVEMENT ---
        self.pos = pygame.math.Vector2(self.hitbox.topleft)
        self.direction = pygame.math.Vector2(0, 0)
        self.lives = 10
        self.hit_cooldown = 1000
        self.last_hit_time = 0
        
        # Knockback
        self.knockback_direction = pygame.math.Vector2(0, 0)
        self.knockback_timer = 0
        self.knockback_duration = 0.2
        
        self.speed = 300         
        self.gravity = 1200      
        self.jump_power = -500   
        self.on_ground = False
        
        # Spell Attack
        self.can_cast = True
        self.cast_cooldown = 1000 # 1 second
        self.last_cast_time = 0
        self.cv_attack = False
        
        # Collision
        self.collision_sprites = collision_sprites

        # Loading sound
        try:
            self.spell_cast_sound = pygame.mixer.Sound("../assets/soundtracks/freesound_community-magic-strike-5856.mp3")
            self.spell_cast_sound.set_volume(0.6)
        except Exception:
            self.spell_cast_sound = None

    def import_character_assets(self):
        """Loads all the different sprite sheets into a dictionary."""
        # Make sure these paths match exactly where your images are saved!
        character_path = "../assets/Main Characters/Ninja Frog/"
        
        self.animations = {
            'idle': [], 'run': [], 'jump': [], 'fall': [], 
            'double_jump': [], 'wall_jump': [], 'hit': []
        }

        for animation in self.animations.keys():
            # Build the path based on the dictionary keys
            # Example: '../assets/Main Characters/Ninja Frog/Idle (32x32).png'
            # Note: We capitalize the first letter to match your file names (Idle, Run, etc.)
            full_path = f"{character_path}{animation.replace('_', ' ').title()} (32x32).png"
            
            try:
                sheet = pygame.image.load(full_path).convert_alpha()
                num_frames = sheet.get_width() // 32
                
                for i in range(num_frames):
                    frame = pygame.Surface((32, 32), pygame.SRCALPHA)
                    frame.blit(sheet, (0, 0), (i * 32, 0, 32, 32))
                    frame = pygame.transform.scale(frame, (48, 48)) # Scale to match tiles
                    self.animations[animation].append(frame)
            except FileNotFoundError:
                print(f"Warning: Could not load {full_path}. Check your file names and paths.")

    def get_input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = 0
        
        dir_x = self.cv_direction_x
        if dir_x == 0:
            if keys[pygame.K_LEFT]:
                dir_x = -1
            if keys[pygame.K_RIGHT]:
                dir_x = 1
                
        self.direction.x = dir_x
        if dir_x < 0:
            self.facing_right = False
        elif dir_x > 0:
            self.facing_right = True
            
        if (keys[pygame.K_SPACE] or self.cv_jump) and self.on_ground:
            self.direction.y = self.jump_power
            self.on_ground = False

    def get_status(self):
        """Determines what state the frog is in based on its movement."""
        if self.knockback_timer > 0:
            self.status = 'hit'
            return

        if self.direction.y < 0:
            self.status = 'jump'
        elif self.direction.y > 1: # > 1 means falling (accounting for tiny gravity shifts)
            self.status = 'fall'
        else:
            if self.direction.x != 0:
                self.status = 'run'
            else:
                self.status = 'idle'

    def animate(self, dt):
        """Plays the correct animation frames based on the current status."""
        animation = self.animations[self.status]
        
        # Loop over the frame index
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(animation):
            self.frame_index = 0
            
        current_frame = animation[int(self.frame_index)]
        
        # Flicker logic for invincibility
        if pygame.time.get_ticks() - self.last_hit_time < self.hit_cooldown and self.status == 'hit':
            # Toggle alpha/visibility every 100ms
            if (pygame.time.get_ticks() // 100) % 2:
                self.image.set_alpha(0)
            else:
                self.image.set_alpha(255)
        else:
            self.image.set_alpha(255)

        # Flip the image if facing left
        if self.facing_right:
            self.image = current_frame
        else:
            self.image = pygame.transform.flip(current_frame, True, False)

    def horizontal_collisions(self):
        for sprite in self.collision_sprites:
            # Check hitbox instead of rect
            if self.hitbox.colliderect(sprite.rect):
                if self.direction.x > 0: 
                    self.hitbox.right = sprite.rect.left
                    self.pos.x = self.hitbox.x
                elif self.direction.x < 0:
                    self.hitbox.left = sprite.rect.right
                    self.pos.x = self.hitbox.x

    def vertical_collisions(self):
        self.on_ground = False
        for sprite in self.collision_sprites:
            # Check hitbox instead of rect
            if self.hitbox.colliderect(sprite.rect):
                if self.direction.y > 0: 
                    self.hitbox.bottom = sprite.rect.top
                    self.pos.y = self.hitbox.y
                    self.direction.y = 0
                    self.on_ground = True
                elif self.direction.y < 0: 
                    self.hitbox.top = sprite.rect.bottom
                    self.pos.y = self.hitbox.y
                    self.direction.y = 0

    def apply_knockback(self, direction_x):
        self.knockback_direction = pygame.math.Vector2(direction_x, -0.5).normalize()
        self.knockback_timer = self.knockback_duration

    def cast_spell(self):
        if self.can_cast:
            direction = 1 if self.facing_right else -1
            # Spawn spell at player center
            Spell((self.groups()[0], self.spell_sprites), self.rect.center, direction, self.collision_sprites)
            self.can_cast = False
            self.last_cast_time = pygame.time.get_ticks()
            if self.spell_cast_sound:
                self.spell_cast_sound.play()

    def update(self, dt):
        # Handle attack input
        if self.cv_attack and self.can_cast:
            self.cast_spell()
            
        # Cooldown logic
        if not self.can_cast:
            if pygame.time.get_ticks() - self.last_cast_time >= self.cast_cooldown:
                self.can_cast = True

        if self.knockback_timer > 0:
            self.pos += self.knockback_direction * self.speed * 1.5 * dt
            self.knockback_timer -= dt
            
            # Apply collision while being knocked back
            self.hitbox.x = round(self.pos.x)
            self.horizontal_collisions()
            self.hitbox.y = round(self.pos.y)
            self.vertical_collisions()
        else:
            self.get_input()
            
        self.direction.y += self.gravity * dt

        # X Movement
        if self.knockback_timer <= 0:
            self.pos.x += self.direction.x * self.speed * dt
            self.hitbox.x = round(self.pos.x) # Move hitbox
            self.horizontal_collisions()

        # Y Movement
        self.pos.y += self.direction.y * dt
        self.hitbox.y = round(self.pos.y) # Move hitbox
        self.vertical_collisions()

        # IMPORTANT: Make the visual rect follow the physical hitbox
        # We align the bottoms so the frog's feet stay on the ground
        self.rect.midbottom = self.hitbox.midbottom 

        self.get_status()
        self.animate(dt)