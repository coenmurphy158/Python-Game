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

player_health = 100
player_max_health = 100
display_health = player_health
health_flash = 0
screen_shake = 0

def restart_game():
    global char_x, char_y, enemies, laser_list, enemy_lasers, explosions
    global score, score_animation, game_over, bg_y1, bg_y2
    global player_health, display_health, health_flash, screen_shake

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

    player_health = player_max_health
    display_health = player_health
    health_flash = 0
    screen_shake = 0

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
class KamikazeEnemy:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.speed = 2
        self.target_x = char_x
        self.target_y = char_y
        self.image = pygame.image.load('enemy_pixel.bmp').convert_alpha()
        self.width = self.image.get_width()
        self.height = self.image.get_height()
    def update(self):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = max(1,(dx*dx + dy*dy)**0.5)
        self.x += (dx / dist) * self.speed
        self.y += (dy / dist) * self.speed
        self.speed +=0.05
    def draw(self):
        win.blit(self.image,(self.x,self.y))
        self.update()



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
                if random.randint(1,3) == 1:
                    enemies.append(KamikazeEnemy(random.randint(0,WIDTH - 20),0))
                else:
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

        shake_x = 0
        shake_y = 0
        if screen_shake > 0:
            shake_x = random.randint(-5, 5)
            shake_y = random.randint(-5, 5)
            screen_shake -= 1

        bg_y1 += bg_speed
        bg_y2 += bg_speed
        if bg_y1 >= HEIGHT:
            bg_y1 = -HEIGHT
        if bg_y2 >= HEIGHT:
            bg_y2 = -HEIGHT

        win.blit(background, (shake_x, bg_y1 + shake_y))
        win.blit(background, (shake_x, bg_y2 + shake_y))

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
            if isinstance(enemy, Enemy):
                if random.randint(1, 80) == 1:
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

        bar_width = 165
        bar_height = 15

        if display_health > player_health:
            display_health -= 1
        elif display_health < player_health:
            display_health += 1

        health_ratio = display_health / player_max_health

        if health_flash > 0:
            bar_color = (255, 80, 80)
            health_flash -= 1
        else:
            bar_color = (0, 255, 0)

        pygame.draw.rect(win, (100, 0, 0), (10, 60, bar_width, bar_height))

        segments = 33
        segment_width = bar_width // segments
        filled_segments = int(segments*health_ratio)

        for i in range(filled_segments):
            x = 10 + i * segment_width
            pygame.draw.rect(win,bar_color,(x,60,segment_width-1,bar_height))

        for el in enemy_lasers:
            el.y += enemy_laser_speed
            pygame.draw.rect(win, (255, 0, 0), el)

        enemy_lasers = [el for el in enemy_lasers if el.y < HEIGHT]

        player_rect = pygame.Rect(char_x, char_y, 16, 16)
        for enemy in enemies[:]:
            if isinstance(enemy, KamikazeEnemy):
                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                player_rect = pygame.Rect(char_x, char_y, 16, 16)
                if player_rect.colliderect(enemy_rect):
                    player_health -= 40
                    enemies.remove(enemy)
                    health_flash = 10
                    screen_shake = 12
                    if player_health <= 0:
                        game_over = True

        pygame.display.update()
        clock.tick(60)
