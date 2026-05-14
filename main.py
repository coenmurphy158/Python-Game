import pygame
import sys
import random

WIDTH, HEIGHT = 800, 600
char_x = WIDTH // 2
char_y = HEIGHT // 2
char_speed = 2

laser_speed = 5
laser_counter = 0
bg_y1 = 0
bg_y2 = -HEIGHT
bg_speed = 1
score_size = 36
enemy_laser_speed = 3

laser_list = []
explosions = []
enemies = []
enemy_lasers = []
score = 0
score_animation = 0
game_over = False

def restart_game():
    global char_x, char_y, enemies, laser_list, enemy_lasers, explosions
    global score, score_animation, game_over, bg_y1, bg_y2

    char_x = WIDTH // 2
    char_y = HEIGHT // 2
    enemies = []
    laser_list = []
    enemy_lasers = []
    explosions = []
    score = 0
    score_animation = 0
    bg_y1 = 0
    bg_y2 = -HEIGHT
    game_over = False


class Powerup:
    def __init__(self):
        self.sprite = pygame.image.load('powerup2.bmp').convert_alpha()
        self.rect = pygame.rect.Rect(self.sprite.get_rect().center)
    def draw(self):
        win.blit(self.sprite, (self.rect.x, self.rect.y))


class Enemy:
    walkRight = [pygame.image.load('enemy_pixel.bmp')]
    walkLeft = [pygame.image.load('enemy_pixel.bmp')]

    def __init__(self, x, y, width, height, end):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.path = [x, end]
        self.vel = 4
        self.image = pygame.image.load('enemy_pixel.bmp').convert_alpha()

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

if __name__ == '__main__':
    pygame.init()

    win = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    spawn_enemy = pygame.USEREVENT + 1
    pygame.time.set_timer(spawn_enemy, 3000)

    player = pygame.image.load('aircraft.bmp').convert_alpha()
    laser_image = pygame.image.load('laser.bmp').convert_alpha()
    enemy_img = pygame.image.load('enemy_pixel.bmp').convert_alpha()
    background = pygame.image.load("sky.bmp").convert()
    explosion_img = pygame.image.load("explosion.bmp").convert_alpha()
    explosion_sheet = pygame.image.load("bk_explo_short.bmp")

    explosion_frames = []
    frame_width = explosion_sheet.get_width() // 8
    frame_height = explosion_sheet.get_height()
    for i in range(8):
        frame = explosion_sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
        explosion_frames.append(frame)

    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    pixel_font = pygame.font.Font('pixel_text.ttf', 32)

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == spawn_enemy and not game_over:
                x = random.randint(0, WIDTH - 20)
                enemies.append(Enemy(x, 0, 30, 30, x + 200))

            if game_over:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    restart_game()


        if game_over:
            go_font = pygame.font.Font('pixel_text.ttf', 48)
            go_text = go_font.render("GAME OVER", True, (255, 0, 0))
            win.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, HEIGHT // 2 - 50))

            score_font = pygame.font.Font('pixel_text.ttf', 24)
            score_text = score_font.render(f"Final Score: {score}", True, (255, 255, 255))
            win.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + 10))

            pygame.display.update()
            clock.tick(60)
            continue


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
                    explosions.append([enemy.x, enemy.y, 0])
                    enemies.remove(enemy)
                    laser_list.remove(laser)
                    score += 100
                    score_animation = 6
                    break

        for enemy in enemies:
            enemy.draw()
            if random.randint(1, 120) == 1:
                enemy_lasers.append(pygame.Rect(enemy.x + enemy.width // 2, enemy.y + enemy.height, 3, 10))

        for ex in explosions[:]:
            frame = explosion_frames[ex[2]]
            win.blit(frame, (ex[0], ex[1]))
            ex[2] += 1
            if ex[2] >= len(explosion_frames):
                explosions.remove(ex)

        if score_animation > 0:
            size = score_size + score_animation
            score_animation -= 1
        else:
            size = score_size

        font = pygame.font.Font('pixel_text.ttf', size)
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        win.blit(score_text, (10, 10))

        for el in enemy_lasers:
            el.y += enemy_laser_speed
            pygame.draw.rect(win, (255, 0, 0), el)

        enemy_lasers = [el for el in enemy_lasers if el.y < HEIGHT]

        player_rect = pygame.Rect(char_x, char_y, 16, 16)
        for el in enemy_lasers[:]:
            if player_rect.colliderect(el):
                game_over = True
                enemy_lasers.remove(el)

        pygame.display.update()
        clock.tick(60)
