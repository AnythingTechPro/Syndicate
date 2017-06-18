import os
import time
import pygame
import random
import pyscroll
import client
from pygame.locals import *
from PIL import Image
from pytmx.util_pygame import load_pygame

class GameUtil(object):

    @staticmethod
    def load_image(filepath):
        if not os.path.exists(filepath):
            raise IOError('Failed to load image file %s!' % filepath)

        image = Image.open(filepath)
        return pygame.image.fromstring(image.tobytes(), image.size, image.mode).convert_alpha()

    @staticmethod
    def load_map(filepath):
        if not os.path.exists(filepath):
            raise IOError('Failed to load map file %s!' % filepath)

        return load_pygame(filepath)

class GameLevel(object):

    def __init__(self, map_filepath):
        self.tmx_data = GameUtil.load_map(map_filepath)
        self.map_data = pyscroll.TiledMapData(self.tmx_data)
        self.surfacedata = {}

    def setup(self):
        for x in range(0, self.tmx_data.width):
            for y in range(0, self.tmx_data.height):
                for layer in range(0, len(self.tmx_data.layers)):
                    surface = self.tmx_data.get_tile_image(x, y, layer)

                    if not surface:
                        continue

                    rect = surface.get_rect()
                    width = rect.width
                    height = rect.height

                    self.surfacedata[len(self.surfacedata) + 1] = [surface, x * width, y * height]

    def update(self):
        pass

    def draw(self, draw_surface):
        for surface, x, y in self.surfacedata.values():
            draw_surface.blit(surface, [x, y])

class Delayer(object):

    def __init__(self, function, delay):
        self.function = function
        self.delay = delay
        self.timestamp = time.time()

    @property
    def duration(self):
        return time.time() - self.timestamp

    def update(self):
        if self.duration < self.delay:
            return None
        else:
            self.timestamp = time.time()

        return self.function()

class PlayerAnimator(object):
    IDLE = 'idle'
    WALK_FORWARD = 'walk_forward'
    WALK_BACKWARD = 'walk_backward'
    WALK_LEFT = 'walk_left'
    WALK_RIGHT = 'walk_right'

    def __init__(self):
        self.state_dict = {
            self.IDLE: {
                1: GameUtil.load_image('assets/Characters/Agent/Walk/walk-0-0.png'),
                2: GameUtil.load_image('assets/Characters/Agent/Walk/walk-0-1.png'),
            },
            self.WALK_FORWARD: {
                1: GameUtil.load_image('assets/Characters/Agent/Walk/walk-0-2.png'),
                2: GameUtil.load_image('assets/Characters/Agent/Walk/walk-0-3.png'),
                3: GameUtil.load_image('assets/Characters/Agent/Walk/walk-0-4.png'),
                4: GameUtil.load_image('assets/Characters/Agent/Walk/walk-0-5.png'),
                5: GameUtil.load_image('assets/Characters/Agent/Walk/walk-0-6.png'),
                6: GameUtil.load_image('assets/Characters/Agent/Walk/walk-0-7.png'),
                7: GameUtil.load_image('assets/Characters/Agent/Walk/walk-0-8.png'),
            },
            self.WALK_BACKWARD: {
                1: GameUtil.load_image('assets/Characters/Agent/Walk/walk-2-0.png'),
                2: GameUtil.load_image('assets/Characters/Agent/Walk/walk-2-1.png'),
                3: GameUtil.load_image('assets/Characters/Agent/Walk/walk-2-2.png'),
                4: GameUtil.load_image('assets/Characters/Agent/Walk/walk-2-3.png'),
                5: GameUtil.load_image('assets/Characters/Agent/Walk/walk-2-4.png'),
                6: GameUtil.load_image('assets/Characters/Agent/Walk/walk-2-5.png'),
                7: GameUtil.load_image('assets/Characters/Agent/Walk/walk-2-6.png'),
                8: GameUtil.load_image('assets/Characters/Agent/Walk/walk-2-7.png'),
                9: GameUtil.load_image('assets/Characters/Agent/Walk/walk-2-8.png'),
            },
            self.WALK_LEFT: {
                1: GameUtil.load_image('assets/Characters/Agent/Walk/walk-1-0.png'),
                2: GameUtil.load_image('assets/Characters/Agent/Walk/walk-1-1.png'),
                3: GameUtil.load_image('assets/Characters/Agent/Walk/walk-1-2.png'),
                4: GameUtil.load_image('assets/Characters/Agent/Walk/walk-1-3.png'),
                5: GameUtil.load_image('assets/Characters/Agent/Walk/walk-1-4.png'),
                6: GameUtil.load_image('assets/Characters/Agent/Walk/walk-1-5.png'),
                7: GameUtil.load_image('assets/Characters/Agent/Walk/walk-1-6.png'),
                8: GameUtil.load_image('assets/Characters/Agent/Walk/walk-1-7.png'),
                9: GameUtil.load_image('assets/Characters/Agent/Walk/walk-1-8.png'),
            },
            self.WALK_RIGHT: {
                1: GameUtil.load_image('assets/Characters/Agent/Walk/walk-3-0.png'),
                2: GameUtil.load_image('assets/Characters/Agent/Walk/walk-3-1.png'),
                3: GameUtil.load_image('assets/Characters/Agent/Walk/walk-3-2.png'),
                4: GameUtil.load_image('assets/Characters/Agent/Walk/walk-3-3.png'),
                5: GameUtil.load_image('assets/Characters/Agent/Walk/walk-3-4.png'),
                6: GameUtil.load_image('assets/Characters/Agent/Walk/walk-3-5.png'),
                7: GameUtil.load_image('assets/Characters/Agent/Walk/walk-3-6.png'),
                8: GameUtil.load_image('assets/Characters/Agent/Walk/walk-3-7.png'),
                9: GameUtil.load_image('assets/Characters/Agent/Walk/walk-3-8.png'),
            }
        }

        self.state = self.IDLE
        self.state_index = 1

        self.state_delay = Delayer(self.play, 0.1)
        self.state_surface = self.get_surface()

    def get_surface(self):
        return self.state_dict[self.state][self.state_index]

    def play(self):
        self.state_index += 1

        if self.state_index > max(self.state_dict[self.state]):

            # reset the state index to the minimum/lowest range value in the dictionary
            self.state_index = min(self.state_dict[self.state])

        self.state_surface = self.get_surface()

    def update(self):
        self.state_delay.update()

class Player(pygame.sprite.DirtySprite, PlayerAnimator):

    def __init__(self, id, owner=False):
        pygame.sprite.DirtySprite.__init__(self)
        PlayerAnimator.__init__(self)

        self.id = id
        self.owner = owner

        self._x = 0
        self._y = 0

        self.last_x = 0
        self.last_y = 0

    @property
    def image(self):
        return self.state_surface

    @property
    def rect(self):
        rect = self.state_surface.get_rect()
        rect.x = self.x
        rect.y = self.y

        return rect

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x):
        self._x = x
        self.rect.x = x

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        self._y = y
        self.rect.y = y

    def get_key_control(self):
        key = pygame.key.get_pressed()

        return [key[pygame.K_DOWN], key[pygame.K_UP], key[pygame.K_RIGHT], key[pygame.K_LEFT]]

    def update(self):
        if self.owner:
            self.update_input()

        if self.x < self.last_x:
            self.state = self.WALK_LEFT
        elif self.x > self.last_x:
            self.state = self.WALK_RIGHT
        elif self.y < self.last_y:
            self.state = self.WALK_FORWARD
        elif self.y > self.last_y:
            self.state = self.WALK_BACKWARD
        else:
            self.state = self.IDLE

        self.last_x = self.x
        self.last_y = self.y

        PlayerAnimator.update(self)

    def update_input(self):
        key = pygame.key.get_pressed()
        speed = 1.0

        (down, up, right, left) = self.get_key_control()

        if down:
            self.y += speed

        if up:
            self.y -= speed

        if right:
            self.x += speed

        if left:
            self.x -= speed

        # now broadcast a position update for this player
        client.handle_send_position_update(self)

    def draw(self, surface):
        surface.blit(self.state_surface, (self.x, self.y))

class MousePicker(object):

    def __init__(self):
        self.moving = False

    @property
    def xy(self):
        if not pygame.mouse.get_focused():
            return [0, 0]

        x, y = pygame.mouse.get_pos()

        return [x / level.tmx_data.width, y / level.tmx_data.height]

    @property
    def pressed(self):
        return pygame.mouse.get_pressed()

    def update(self):
        m_x, m_y = self.xy

        m_x *= level.tmx_data.width
        m_y *= level.tmx_data.height

        (btn1, btn2, btn3) = self.pressed

        if not btn1 and self.moving:
            self.moving = False

        if round(m_x) - round(client.owned_player.x) <= 5 and round(m_y) - round(client.owned_player.y) <= 5 and btn1 or self.moving:
            client.owned_player.x = m_x
            client.owned_player.y = m_y
            self.moving = True

def main():
    pygame.init()

    screen_height, screen_width = 800, 600

    global clock
    clock = pygame.time.Clock()

    global screen
    screen = pygame.display.set_mode([screen_height, screen_width])

    global level
    level = GameLevel('assets/Maps/test.tmx')
    level.setup()

    #global level_layer
    #level_layer = pyscroll.BufferedRenderer(level.map_data, [screen_height, screen_width])

    # adjust the zoom (out)
    #level_layer.zoom = .5

    # adjust the zoom (in)
    #level_layer.zoom = 2.0

    #global player_group
    #player_group = pyscroll.PyscrollGroup(map_layer=level_layer)

    #__builtin__.player_group = player_group

    global players
    players = {}
    client.players = players

    global mouse_picker
    mouse_picker = MousePicker()

    # setup the client networking loop
    client.run_mainloop()

    # finally request a new player object over the network
    client.handle_send_request_spawn()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                break

        screen.fill(pygame.Color(1, 1, 1, 1))

        level.update()
        level.draw(screen)

        for player in list(players.values()):
            player.update()
            player.draw(screen)

        # only update mouse picker if we have a player
        #if client.owned_player:
        #    mouse_picker.update()

        #player_group.draw(screen)

        pygame.display.flip()
        # clocks pygame to render at 60fps
        #clock.tick(60)
        #print (clock.get_fps())

if __name__ == '__main__':
    main()
