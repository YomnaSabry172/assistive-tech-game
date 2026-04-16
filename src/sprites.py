from settings import *

class Collision_sprites(pg.sprite.Sprite):
    def __init__(self, groups,image, pos):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)

from settings import *

class AllSprites(pg.sprite.Group):
    offset = pg.Vector2()
    def __init__(self):
        super().__init__()
        self.display_surface = pg.display.get_surface()
    def draw(self , target_pos):
        AllSprites.offset.x = 1280 / 2 - target_pos[0] # Show tile area
        AllSprites.offset.y = 720 / 2 - target_pos[1]
        ground_sprites = [sprite for sprite in self if hasattr(sprite , 'ground' )]
        object_sprites = [sprite for sprite in self if not hasattr(sprite , 'ground' ) ]
        enemy_sprites  = [sprite for sprite in self if hasattr(sprite , 'enemy') and not hasattr(sprite, 'ground') ]
        archers_sprites = [sprite for sprite in self if not hasattr(sprite , 'ground' ) and hasattr(sprite , 'isArcher')]
        obstacles = [sprite for sprite in self if not hasattr(sprite , 'ground' ) and hasattr(sprite , 'isObstacle')]
        for layer in [ground_sprites,object_sprites,archers_sprites, obstacles,enemy_sprites]:#the order is important
            for sprite in sorted(layer,key  = lambda sprite: sprite.rect.centery):
                #print(sprite)
                if  hasattr(sprite , 'enemy') and not hasattr(sprite, 'ground') :
                    if sprite.ismoving:
                        sprite.draw(AllSprites.offset)
                    else :continue
                else :
                    self.display_surface.blit(sprite.image,sprite.rect.topleft + AllSprites.offset)
