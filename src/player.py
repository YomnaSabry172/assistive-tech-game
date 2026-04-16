import pygame

class Player:
    def __init__(self, x, y):
        # Animation variables
        self.animations = {'idle': [], 'run': [], 'jump': [], 'fall': []}
        self.state = 'idle'
        self.frame_index = 0
        self.animation_speed = 0.2 # How fast the frames change
        self.facing_right = True

        # Load all animations
        self.load_animations()
        
        # Set initial image and rect (Hitbox)
        self.image = self.animations[self.state][self.frame_index]
        self.rect = self.image.get_rect(topleft=(x, y))
        
        # Physics variables
        self.vel_x = 0
        self.vel_y = 0       
        self.speed = 5       
        self.gravity = 0.5   
        self.jump_power = -10 
        self.on_ground = False

    def import_sprite_sheet(self, path):
        """Loads a sprite sheet and slices it into individual 32x32 frames."""
        sheet = pygame.image.load(path).convert_alpha()
        frames = []
        # The frog sprites are 32x32. We figure out how many frames are in the sheet
        # by dividing the total width by 32.
        num_frames = sheet.get_width() // 32
        
        for i in range(num_frames):
            # Create a blank 32x32 surface
            surface = pygame.Surface((32, 32), pygame.SRCALPHA)
            # Cut the specific frame out of the sheet
            surface.blit(sheet, (0, 0), (i * 32, 0, 32, 32))
            # Scale it up (Optional: scale by 2 to make it 64x64 on screen)
            surface = pygame.transform.scale(surface, (64, 64)) 
            frames.append(surface)
            
        return frames

    def load_animations(self):
        """Loads all the different sprite sheets for the player."""
        base_path = "../assets/Main Characters/Ninja Frog/"
        self.animations['idle'] = self.import_sprite_sheet(base_path + "Idle (32x32).png")
        self.animations['run'] = self.import_sprite_sheet(base_path + "Run (32x32).png")
        self.animations['jump'] = self.import_sprite_sheet(base_path + "Jump (32x32).png")
        self.animations['fall'] = self.import_sprite_sheet(base_path + "Fall (32x32).png")

    def get_input(self):
        """Handles keyboard input for movement."""
        keys = pygame.key.get_pressed()
        self.vel_x = 0

        if keys[pygame.K_LEFT]:
            self.vel_x = -self.speed
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            self.vel_x = self.speed
            self.facing_right = True

        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = self.jump_power

    def update_state(self):
        """Determines which animation to play based on what the player is doing."""
        if self.vel_y < 0:
            self.state = 'jump'
        elif self.vel_y > 1: # We use > 1 to allow a tiny bit of gravity tolerance
            self.state = 'fall'
        elif self.vel_x != 0:
            self.state = 'run'
        else:
            self.state = 'idle'

    def animate(self):
        """Cycles through the frames of the current animation."""
        animation_list = self.animations[self.state]
        
        # Increase frame index by animation speed
        self.frame_index += self.animation_speed
        
        # Loop back to the first frame if we reach the end of the list
        if self.frame_index >= len(animation_list):
            self.frame_index = 0
            
        # Get the current image frame
        current_image = animation_list[int(self.frame_index)]
        
        # Flip the image if facing left
        if self.facing_right:
            self.image = current_image
        else:
            self.image = pygame.transform.flip(current_image, True, False)

    def update(self, platforms_list):
        # 1. Get user input
        self.get_input()

        # 2. Horizontal Movement & Collisions (Need to separate X and Y collisions)
        self.rect.x += self.vel_x
        for platform in platforms_list:
            if self.rect.colliderect(platform):
                if self.vel_x > 0: # Moving right
                    self.rect.right = platform.left
                elif self.vel_x < 0: # Moving left
                    self.rect.left = platform.right

        # 3. Vertical Movement (Gravity) & Collisions
        self.vel_y += self.gravity
        self.rect.y += self.vel_y
        self.on_ground = False

        for platform in platforms_list:
            if self.rect.colliderect(platform):
                if self.vel_y > 0: # Falling down
                    self.rect.bottom = platform.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0: # Jumping up and hitting a ceiling
                    self.rect.top = platform.bottom
                    self.vel_y = 0

        # 4. Handle Animations
        self.update_state()
        self.animate()

    def draw(self, surface):
        surface.blit(self.image, self.rect)