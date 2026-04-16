# from shop_menu import ShopMenu
# from settings import *
# import pygame as pg
# from game import *
# from main_menu import *
# from pause_menu import *
# from gameover_menu import *
# from win_menu import *
# import os
# os.chdir(os.path.dirname(__file__))
# main_menu_sound = pg.mixer.Sound("../sounds/main_menu.mp3")
# ingame_sound = pg.mixer.Sound("../sounds/ingame.mp3")
# ingame_sound.set_volume(0.2)

# # palmer , bellinghamء , saka , toney , trent ---> pressure!!! _______  what pressure?
# class Game_Mannager:
#     def __init__(self):
#         self.running = True
#         self.paused = False
#         self.gameOver = False
#         self.winGame = False
#         pg.init()
#         self.display = pg.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
#         pg.display.set_caption('Castle Defense')
#         self.main_menu = Main_Menu(self.display,self)
#         self.game =  Game(self.display , self)
#         self.shop_menu = ShopMenu(self.display,self)
#         self.clock = pg.time.Clock()
#         self.state = 'menu'
#         self.load()
#         self.allowIngamesound = True
#         self.state_switched = False
#         main_menu_sound.play(loops=-1).set_volume(0.5)

        
#     def load(self):
#         for direction in enemy_paths.keys():
#             for action in ['walk', 'atk']:
#                 for full_path in enemy_paths[direction][action]:
#                         surf = pg.image.load(full_path).convert_alpha()
#                         enemy_frames[direction][action].append(surf)

#         for direction in strong_enemy_paths.keys():
#             for action in ['walk', 'atk']:
#                 for full_path in strong_enemy_paths[direction][action]:
#                         surf = pg.image.load(full_path).convert_alpha()
#                         strong_enemy_frames[direction][action].append(surf)

#         explosion_path = '../sprites/effects/bom'
#         for i in range(8):
#             surf = pg.image.load(join(explosion_path,f'{i}.png'))
#             explosion.append(surf)


#     def new_game(self):
#         pg.mixer.stop()
#         self.game.reset()
#         game_manager = Game_Mannager()
#         game_manager.run()
#         self.running = False
#         ingame_sound.stop()

#     def run(self):
#         while self.running:
#             dt = self.clock.tick_busy_loop(60)/1000
#             for event in pg.event.get():
#                 if event.type == pg.QUIT:
#                     self.running = False
#                 if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
#                     self.running = False

#             if self.paused and self.state =='pause':
#                 self.pause_menu.update()
#             if self.gameOver and self.state == 'gameover':
#                 self.gameover_menu.update()
#             if self.winGame and self.state == 'wingame':
#                 self.wingame_menu.update()
#             elif self.state == 'menu':
#                 self.main_menu.draw()

#             elif self.state == 'game':
#                 self.game.update(dt)
#                 self.pause_menu = Pause_menu(self.display, self)
#                 self.gameover_menu = GameOver_menu(self.display, self)
#                 self.wingame_menu = WinGame_menu(self.display, self)
#                 self.shop_menu= ShopMenu(self.display,self)

#                 if not  self.state_switched  and self.allowIngamesound :
#                     main_menu_sound.stop()
#                     ingame_sound.play(loops=-1).set_volume(0.2)
#                     self.state_switched = True
#             elif self.state == 'pause':
#                 self.paused = not self.paused
                
                
#             elif self.state == 'gameover':
#                 self.gameOver = not self.gameOver
#             elif self.state == 'wingame':
#                 self.winGame = not self.winGame
#             elif self.state == 'shop':
#                 self.shop_menu.update()
#             pg.display.update()
#     pg.quit()


import pygame
import sys
from player import Player  # Import your new class!

# --- 1. Setup and Initialization ---
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tilemap Platformer with Animations")
clock = pygame.time.Clock()

# --- 2. Load Environment Assets ---
bg_tile = pygame.image.load("../assets/Background/Brown.png").convert()
sprite_sheet = pygame.image.load("../assets/Terrain/Terrain (16x16).png").convert_alpha()
bg_w, bg_h = bg_tile.get_size()

# --- 3. Tile Helper Functions ---
def get_tile(sheet, x, y, width, height, scale):
    image = pygame.Surface((width, height), pygame.SRCALPHA)
    image.blit(sheet, (0, 0), (x, y, width, height))
    return pygame.transform.scale(image, (width * scale, height * scale))

TILE_SIZE = 48 
SCALE = 3

grass_tile = get_tile(sprite_sheet, 96, 0, 16, 16, SCALE) 
dirt_tile = get_tile(sprite_sheet, 96, 16, 16, 16, SCALE)
pyramid_tile = get_tile(sprite_sheet, 192, 0, 16, 16, SCALE)
slime_tile = get_tile(sprite_sheet, 96, 96, 16, 16, SCALE) 

level_map = [
    "................P",
    "................P",
    ".......P.........",
    ".......P.........",
    ".......P.........",
    ".................",
    ".................",
    ".......GGGG......",
    "....GGGDDDD......",
    "....DDDDDDD......",
    "OOOODDDDDDD...GGG",
    "OOOODDDDDDD...DDD",
    "OOOODDDDDDD...DDD"
]

# --- 4. Build the Level Data ---
platforms = []
tiles_to_draw = []

for row_index, row in enumerate(level_map):
    for col_index, char in enumerate(row):
        x = col_index * TILE_SIZE
        y = row_index * TILE_SIZE
        if char != '.':
            rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            platforms.append(rect)
            if char == 'G': tiles_to_draw.append((grass_tile, rect))
            elif char == 'D': tiles_to_draw.append((dirt_tile, rect))
            elif char == 'P': tiles_to_draw.append((pyramid_tile, rect))
            elif char == 'O': tiles_to_draw.append((slime_tile, rect))

# --- 5. Create Player Instance ---
# Using the class imported from player.py
player = Player(100, 100)

# --- 6. Main Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Updates ---
    player.update(platforms)

    # --- Drawing ---
    for x in range(0, SCREEN_WIDTH, bg_w):
        for y in range(0, SCREEN_HEIGHT, bg_h):
            screen.blit(bg_tile, (x, y))

    for tile_image, tile_rect in tiles_to_draw:
        screen.blit(tile_image, tile_rect.topleft)

    player.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()