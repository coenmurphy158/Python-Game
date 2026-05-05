import pygame
import sys
import pygame_menu
import random
pygame.init()

WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
spawn_enemy = pygame.USEREVENT + 1
pygame.time.set_timer(spawn_enemy,3000)

menu = pygame_menu.Menu('Main Menu', 600, 400)
menu.add.button('Play', lambda: menu.disable())
menu.add.button('Quit', pygame_menu.events.EXIT)
menu.mainloop(win)

player = pygame.image.load('aircraft.png').convert_alpha()
laser_image = pygame.image.load('laser.gif').convert_alpha()
enemy_img = pygame.image.load('enemypixel.gif').convert_alpha()
background = pygame.image.load("sky.png").convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

laser_speed = 5
laser_list = []
laser_counter = 0
enemies = []
bg_y1 = 0
bg_y2 = -HEIGHT
bg_speed = 1

class Enemy:
    walkRight = [pygame.image.load('enemypixel.gif')]
    walkLeft = [pygame.image.load('enemypixel.gif')]

    def __init__(self, x, y, width, height, end):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.path = [x, end]
        self.vel = 4
        self.image = pygame.image.load('enemypixel.gif').convert_alpha()

    def draw(self):
        win.blit(self.image, (self.x, self.y))
        self.move()

    def move(self):
        if self.vel > 0:
            if self.x + self.vel < self.path[1]:
                self.x += self.vel
            else:
                self.vel = -self.vel
        else:
            if self.x + self.vel > self.path[0]:
                self.x += self.vel
            else:
                self.vel = -self.vel

def get_sprite(sheet, col, row):
    SPRITE_W = 16
    SPRITE_H = 16
    rect = pygame.Rect(col * SPRITE_W, row * SPRITE_H, SPRITE_W, SPRITE_H)
    return sheet.subsurface(rect)

char_x = WIDTH // 2
char_y = HEIGHT // 2
char_speed = 2

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == spawn_enemy:
            x = random.randint(0, WIDTH - 20)
            enemies.append(Enemy(x, 0, 30, 30, x + 200))

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        char_x -= char_speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        char_x += char_speed
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        char_y -= char_speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        char_y += char_speed

    char_x = max(0, min(WIDTH - 16, char_x))
    char_y = max(0, min(HEIGHT - 16, char_y))

    bg_y1 += bg_speed
    bg_y2 += bg_speed
    if bg_y1 >= HEIGHT:
        bg_y1 = -HEIGHT
    if bg_y2 >= HEIGHT:
        bg_y2 = -HEIGHT

    win.blit(background, (0, bg_y1))
    win.blit(background, (0, bg_y2))

    player_image = get_sprite(player, 3, 3)
    win.blit(player_image, (char_x, char_y))

    laser_counter += 1
    if laser_counter >= 15:
        laser_counter = 0

    if keys[pygame.K_SPACE] and laser_counter == 0:
        laser_list.append({"laser_rect": pygame.Rect(char_x + 7, char_y, 2, 8)})
        laser_counter = 1

    for laser in laser_list:
        pygame.draw.rect(win, (255, 255, 255), laser["laser_rect"])
        laser["laser_rect"].y -= laser_speed

    laser_list = [laser for laser in laser_list if laser["laser_rect"].y > -10]

    for laser in laser_list[:]:
        for enemy in enemies[:]:
            enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
            if laser["laser_rect"].colliderect(enemy_rect):
                enemies.remove(enemy)
                laser_list.remove(laser)
                break

    for enemy in enemies:
        enemy.draw()

#double shot powerup
    class Powerup:
        def __init__(self):
            self.image = pygame.image.load('powerup2.png').convert_alpha()
            self.rect = self.image()
            self.rect.x = random.randint(300, 400)

    pygame.display.update()
    clock.tick(60)
