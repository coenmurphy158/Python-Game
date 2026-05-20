import pygame
import sys
import random

WIDTH, HEIGHT = 800, 600
GAME_W, GAME_H = 400, 300

char_x = GAME_W // 2
char_y = GAME_H // 2
char_speed = 2
laser_cooldown = 15
triple_shot_timer = 0
laser_speed = 5
laser_counter = 0
bg_y1 = 0
bg_y2 = -GAME_H
bg_speed = 1
score_size = 36
enemy_laser_speed = 3
powerups = []
laser_list = []
explosions = []
enemies = []
enemy_lasers = []
score = 0
score_animation = 0
game_over = False
run_won = False
player_health = 100
player_max_health = 100
display_health = player_health
health_flash = 0
screen_shake = 0
enemy_spawn_delay = 3000
boss_active = False
boss = None
boss_health = 0
boss_max_health = 1500
boss_bullets = []
game_state = "title"
rapid_fire_timer = 0
upgrade_health = 0
upgrade_shield = 0
upgrade_lightning = 0
upgrade_speed = 0
upgrade_fire_rate = 0
upgrade_triple = 0
upgrade_nuke = 0
upgrade_magnet = 0
selected_upgrade = "health"


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

    def draw(self, surf):
        surf.blit(self.image, (self.x, self.y))
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
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 2
        self.target_x = char_x
        self.target_y = char_y
        self.image = pygame.image.load('enemy_pixel.bmp').convert_alpha()
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        if random.randint(1, 90) == 1:
            self.target_x = char_x
            self.target_y = char_y

        self.target_x = char_x
        self.target_y = char_y

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = max(1, (dx * dx + dy * dy) ** 0.5)

        self.x += (dx / dist) * self.speed
        self.y += (dy / dist) * self.speed
        self.speed += 0.05

        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self, surf):
        surf.blit(self.image, (self.x, self.y))
        self.update()

class DroneEnemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 1.5
        self.image = pygame.image.load('drone_enemy.bmp').convert_alpha()
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.zone_active = False
        self.zone_timer = 0
        self.zone_rect = pygame.Rect(0, 0, 100, 100)

    def update(self):
        if not self.zone_active:
            self.y += self.speed
            if self.y > 150:
                self.zone_active = True
                self.zone_timer = 120
                self.zone_rect.x = int(self.x + self.width / 2 - self.zone_rect.width / 2)
                self.zone_rect.y = int(self.y + self.height)
        else:
            self.zone_timer -= 1

    def draw(self, surf):
        surf.blit(self.image, (self.x, self.y))
        self.update()

class Boss:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.width = 64
        self.height = 64
        self.image = pygame.transform.scale(image, (self.width, self.height))
        self.speed = 2.5
        self.dir = 1
        self.bullet_timer = 0
        self.laser_timer = 0
        self.laser_state = "idle"
        self.laser_x = self.x + self.width // 2

    def update(self):
        if self.laser_state not in ("telegraph", "firing"):
            self.x += self.speed * self.dir
            if self.x <= 0:
                self.x = 0
                self.dir = 1
            if self.x + self.width >= GAME_W:
                self.x = GAME_W - self.width
                self.dir = -1

        self.laser_x = self.x + self.width // 2

        if self.bullet_timer > 0:
            self.bullet_timer -= 1
        if self.laser_timer > 0:
            self.laser_timer -= 1

        if self.laser_state == "idle":
            if self.bullet_timer == 0:
                self.fire_spread()
                self.bullet_timer = int(1.2 * 60)
            if self.laser_timer == 0:
                self.laser_state = "telegraph"
                self.laser_timer = int(0.8 * 60)

        elif self.laser_state == "telegraph":
            if self.laser_timer == 0:
                self.laser_state = "firing"
                self.laser_timer = int(1.0 * 60)

        elif self.laser_state == "firing":
            if self.laser_timer == 0:
                self.laser_state = "cooldown"
                self.laser_timer = int(1.0 * 60)

        elif self.laser_state == "cooldown":
            if self.laser_timer == 0:
                self.laser_state = "idle"
                self.laser_timer = int(2.0 * 60)

    def fire_spread(self):
        angles = [-0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6]
        for a in angles:
            boss_bullets.append({
                "x": self.x + self.width // 2,
                "y": self.y + self.height,
                "dx": a * 3,
                "dy": 4
            })

    def draw(self, surf):
        surf.blit(self.image, (self.x, self.y))
        if self.laser_state == "telegraph":
            pygame.draw.line(
                surf, (255, 0, 0),
                (self.laser_x, self.y + self.height),
                (self.laser_x, GAME_H),
                1
            )
        if self.laser_state == "firing":
            pygame.draw.line(
                surf, (255, 50, 50),
                (self.laser_x, self.y + self.height),
                (self.laser_x, GAME_H),
                6
            )

class PowerUp:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.speed = 1
        file_map = {
            "rapid": "fire_speed_powerup.png",
            "health": "health_powerup.png",
            "triple": "tripleshot_powerup.png"
        }

        raw = pygame.image.load(file_map[kind]).convert_alpha()

        scale_factor = 1.5
        new_w = int(raw.get_width() * scale_factor)
        new_h = int(raw.get_height() * scale_factor)

        self.image = pygame.transform.scale(raw, (new_w, new_h))
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        self.y += self.speed + bg_speed
        self.rect.y = self.y

    def draw(self, surf):
        surf.blit(self.image, (self.x, self.y))

    def update(self):
        self.y += self.speed + bg_speed
        self.rect.y = self.y

    def draw(self, surf):
        surf.blit(self.image, (self.x, self.y))

def restart_game():
    global char_x, char_y, enemies, laser_list, enemy_lasers, explosions
    global score, score_animation, game_over, bg_y1, bg_y2
    global player_health, display_health, health_flash, screen_shake
    global boss_active, boss, boss_health, boss_bullets
    global run_won, game_state
    global player_max_health, char_speed, laser_cooldown

    player_max_health = 100 + upgrade_health
    player_health = player_max_health
    char_speed = 2 + upgrade_speed
    laser_cooldown = max(3, 15 - upgrade_fire_rate)

    run_won = False

    char_x = GAME_W // 2
    char_y = GAME_H // 2
    enemies = []
    laser_list = []
    enemy_lasers = []
    explosions = []
    boss_bullets = []
    score = 0
    score_animation = 0
    bg_y1 = 0
    bg_y2 = -GAME_H
    game_over = False
    display_health = player_health
    health_flash = 0
    screen_shake = 0

    boss_active = False
    boss = None
    boss_health = boss_max_health

    game_state = "title"


def get_sprite(sheet, col, row):
    SPRITE_W = 16
    SPRITE_H = 16
    rect = pygame.Rect(col * SPRITE_W, row * SPRITE_H, SPRITE_W, SPRITE_H)
    return sheet.subsurface(rect)

pygame.init()
pygame.mixer.music.load("background_music.ogg")
pygame.mixer.music.set_volume(0.85)
pygame.mixer.music.play(-1)

win = pygame.display.set_mode((WIDTH, HEIGHT))
game_surface = pygame.Surface((GAME_W, GAME_H))
clock = pygame.time.Clock()
spawn_enemy = pygame.USEREVENT + 1
pygame.time.set_timer(spawn_enemy, enemy_spawn_delay)

player = pygame.image.load('aircraft.bmp').convert_alpha()
laser_image = pygame.image.load('laser.bmp').convert_alpha()
enemy_img = pygame.image.load('enemy_pixel.bmp').convert_alpha()
background = pygame.image.load("sky.bmp").convert()
explosion_img = pygame.image.load("explosion.bmp").convert_alpha()
explosion_sheet = pygame.image.load("bk_explo_short.bmp")
boss_image_raw = pygame.image.load("enemy_boss1.png").convert_alpha()
laser_sound = pygame.mixer.Sound("laser_sound.mp3")
explosion_sound = pygame.mixer.Sound("explosion_sound.mp3")
hit_sound = pygame.mixer.Sound("hit_sound.wav")

title_card = pygame.image.load('intro_scene.png').convert_alpha()
comic_card = pygame.image.load('comic_card.png').convert_alpha()

explosion_frames = []
frame_width = explosion_sheet.get_width() // 8
frame_height = explosion_sheet.get_height()

comic_card = pygame.transform.scale(comic_card, (GAME_W, GAME_H))
title_card = pygame.transform.scale(title_card, (GAME_W, GAME_H))

for i in range(8):
    frame = explosion_sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
    explosion_frames.append(frame)

background = pygame.transform.scale(background, (GAME_W, GAME_H))
pixel_font = pygame.font.Font('pixel_text.ttf', 32)

boss_health = boss_max_health

def fade_in(surface, image, speed=5):
    fade = pygame.Surface(surface.get_size())
    fade.fill((0, 0, 0))
    for alpha in range(255, -1, -speed):
        surface.blit(image, (0, 0))
        fade.set_alpha(alpha)
        surface.blit(fade, (0, 0))
        pygame.display.update()
        clock.tick(60)

def apply_powerup(kind):
    global char_speed, laser_speed, player_health, laser_counter

    if kind == "health":
        player_health = min(player_max_health, player_health + 25)


    elif kind == "rapid":
        global rapid_fire_timer
        rapid_fire_timer = 300


    elif kind == "triple":
        global triple_shot_timer
        triple_shot_timer = 300

def play_intro():
    title_scaled = pygame.transform.scale(title_card, (WIDTH, HEIGHT))
    comic_scaled = pygame.transform.scale(comic_card, (WIDTH, HEIGHT))

    fade_in(win, title_scaled, speed=5)
    pygame.display.update()

    pygame.time.delay(2000)

    fade_in(win, comic_scaled, speed=5)
    pygame.display.update()

    waiting = True
    font = pygame.font.Font('pixel_text.ttf', 24)

    pulse = 0
    pulse_dir = 1

    while waiting:
        win.blit(comic_scaled, (0, 0))

        pulse += pulse_dir * 0.01
        if pulse > 2:
            pulse_dir = -1
        if pulse < -2:
            pulse_dir = 1

        base_text = "Press ENTER to continue"
        text_surface = font.render(base_text, True, (255, 255, 255))

        scale = 1 + pulse * 0.05
        new_w = int(text_surface.get_width() * scale)
        new_h = int(text_surface.get_height() * scale)
        scaled_text = pygame.transform.scale(text_surface, (new_w, new_h))

        win.blit(
            scaled_text,
            (WIDTH // 2 - new_w // 2, HEIGHT - 80)
        )

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                waiting = False

play_intro()

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if game_state == "title":
        win.fill((0, 0, 0))
        title_bg = pygame.transform.scale(comic_card, (WIDTH, HEIGHT))
        win.blit(title_bg, (0, 0))

        font = pygame.font.Font('pixel_text.ttf', 32)

        start_text = font.render("START GAME", True, (255, 255, 255))
        settings_text = font.render("SETTINGS", True, (255, 255, 255))
        quit_text = font.render("QUIT", True, (255, 255, 255))

        button_width = max(start_text.get_width(), settings_text.get_width(), quit_text.get_width()) + 40
        button_height = start_text.get_height() + 20

        start_rect = pygame.Rect(0, 0, button_width, button_height)
        settings_rect = pygame.Rect(0, 0, button_width, button_height)
        quit_rect = pygame.Rect(0, 0, button_width, button_height)

        start_rect.center = (WIDTH // 2, 300)
        settings_rect.center = (WIDTH // 2, 360)
        quit_rect.center = (WIDTH // 2, 420)

        mx, my = pygame.mouse.get_pos()

        if start_rect.collidepoint(mx, my):
            start_color = (255, 255, 0)
        else:
            start_color = (255, 255, 255)

        if settings_rect.collidepoint(mx, my):
            settings_color = (255, 255, 0)
        else:
            settings_color = (255, 255, 255)

        if quit_rect.collidepoint(mx, my):
            quit_color = (255, 255, 0)
        else:
            quit_color = (255, 255, 255)

        pygame.draw.rect(win, start_color, start_rect, 2)
        pygame.draw.rect(win, settings_color, settings_rect, 2)
        pygame.draw.rect(win, quit_color, quit_rect, 2)

        win.blit(start_text, (start_rect.centerx - start_text.get_width() // 2,
                              start_rect.centery - start_text.get_height() // 2))
        win.blit(settings_text, (settings_rect.centerx - settings_text.get_width() // 2,
                                 settings_rect.centery - settings_text.get_height() // 2))
        win.blit(quit_text, (quit_rect.centerx - quit_text.get_width() // 2,
                             quit_rect.centery - quit_text.get_height() // 2))

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_state = "game"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_rect.collidepoint(mx, my):
                    game_state = "game"
                if settings_rect.collidepoint(mx, my):
                    game_state = "settings"
                if quit_rect.collidepoint(mx, my):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()
        clock.tick(60)
        continue

    if game_state == "settings":
        bg_full = pygame.transform.scale(background, (WIDTH, HEIGHT))
        win.blit(bg_full, (0, 0))

        font = pygame.font.Font('pixel_text.ttf', 32)

        music_text = font.render("TOGGLE MUSIC", True, (255, 255, 255))
        volume_up_text = font.render("VOLUME +", True, (255, 255, 255))
        volume_down_text = font.render("VOLUME -", True, (255, 255, 255))
        back_text = font.render("BACK", True, (255, 255, 255))

        button_width = max(
            music_text.get_width(),
            volume_up_text.get_width(),
            volume_down_text.get_width(),
            back_text.get_width()
        ) + 40

        button_height = music_text.get_height() + 20

        music_rect = pygame.Rect(0, 0, button_width, button_height)
        volume_up_rect = pygame.Rect(0, 0, button_width, button_height)
        volume_down_rect = pygame.Rect(0, 0, button_width, button_height)
        back_rect = pygame.Rect(0, 0, button_width, button_height)

        music_rect.center = (WIDTH // 2, 220)
        volume_up_rect.center = (WIDTH // 2, 280)
        volume_down_rect.center = (WIDTH // 2, 340)
        back_rect.center = (WIDTH // 2, 420)

        mx, my = pygame.mouse.get_pos()


        def hover_color(rect):
            return (255, 255, 0) if rect.collidepoint(mx, my) else (255, 255, 255)


        pygame.draw.rect(win, hover_color(music_rect), music_rect, 2)
        pygame.draw.rect(win, hover_color(volume_up_rect), volume_up_rect, 2)
        pygame.draw.rect(win, hover_color(volume_down_rect), volume_down_rect, 2)
        pygame.draw.rect(win, hover_color(back_rect), back_rect, 2)

        win.blit(music_text, (music_rect.centerx - music_text.get_width() // 2,
                              music_rect.centery - music_text.get_height() // 2))

        win.blit(volume_up_text, (volume_up_rect.centerx - volume_up_text.get_width() // 2,
                                  volume_up_rect.centery - volume_up_text.get_height() // 2))

        win.blit(volume_down_text, (volume_down_rect.centerx - volume_down_text.get_width() // 2,
                                    volume_down_rect.centery - volume_down_text.get_height() // 2))

        win.blit(back_text, (back_rect.centerx - back_text.get_width() // 2,
                             back_rect.centery - back_text.get_height() // 2))

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if music_rect.collidepoint(mx, my):
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()

                if volume_up_rect.collidepoint(mx, my):
                    vol = pygame.mixer.music.get_volume()
                    pygame.mixer.music.set_volume(min(1.0, vol + 0.1))

                if volume_down_rect.collidepoint(mx, my):
                    vol = pygame.mixer.music.get_volume()
                    pygame.mixer.music.set_volume(max(0.0, vol - 0.1))

                if back_rect.collidepoint(mx, my):
                    game_state = "title"

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game_state = "title"

        pygame.display.update()
        clock.tick(60)
        continue

    if game_state == "game":
        for event in events:
            if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                restart_game()

            if run_won and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                restart_game()

            if event.type == spawn_enemy and not game_over and not boss_active:
                r = random.randint(1, 4)
                if r == 1:
                    enemies.append(KamikazeEnemy(random.randint(0, GAME_W - 20), 0))
                elif r == 2:
                    enemies.append(DroneEnemy(random.randint(0, GAME_W - 20), 0))
                else:
                    x = random.randint(0, GAME_W - 20)
                    enemies.append(Enemy(x, 0, 30, 30, x + 200))

                enemy_spawn_delay = max(200, enemy_spawn_delay - 100)
                pygame.time.set_timer(spawn_enemy, enemy_spawn_delay)

        if run_won:
            game_surface.blit(background, (0, 0))

            won_font = pygame.font.Font('pixel_text.ttf', 48)
            won_text = won_font.render("RUN WON", True, (255, 165, 0))
            game_surface.blit(
                won_text,
                (GAME_W // 2 - won_text.get_width() // 2, GAME_H // 2 - 50)
            )

            score_font = pygame.font.Font('pixel_text.ttf', 24)
            score_text = score_font.render(f"FINAL SCORE: {score}", True, (255, 255, 255))
            game_surface.blit(
                score_text,
                (GAME_W // 2 - score_text.get_width() // 2, GAME_H // 2 + 10)
            )

            scaled = pygame.transform.scale(game_surface, (WIDTH, HEIGHT))
            win.blit(scaled, (0, 0))

            hint_font = pygame.font.Font('pixel_text.ttf', 20)
            hint_text = hint_font.render("Press ENTER to restart", True, (255, 255, 255))
            win.blit(
                hint_text,
                (WIDTH // 2 - hint_text.get_width() // 2, HEIGHT // 2 + 80)
            )

            pygame.display.update()
            clock.tick(60)
            continue
    if game_state == "shop":
        bg_full = pygame.transform.scale(background, (WIDTH, HEIGHT))
        win.blit(bg_full, (0, 0))

        font = pygame.font.Font('pixel_text.ttf', 32)

        title = font.render("UPGRADE SHOP", True, (255, 255, 255))
        win.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        cost = 1000

        u1 = font.render(f"+10 HEALTH ({cost})", True, (255, 255, 255))
        u2 = font.render(f"SHIELD ({cost})", True, (255, 255, 255))
        u3 = font.render(f"LIGHTNING STRIKE ({cost})", True, (255, 255, 255))
        u4 = font.render(f"+1 SPEED ({cost})", True, (255, 255, 255))
        u5 = font.render(f"+1 FIRE RATE ({cost})", True, (255, 255, 255))
        u6 = font.render(f"LONGER TRIPLE SHOT ({cost})", True, (255, 255, 255))
        u7 = font.render(f"NUKE POWERUP ({cost})", True, (255, 255, 255))
        u8 = font.render(f"MAGNET POWERUP ({cost})", True, (255, 255, 255))

        start_text = font.render("START RUN", True, (255, 255, 255))

        button_w = max(u1.get_width(), u2.get_width(), u3.get_width(), u4.get_width(),
                       u5.get_width(), u6.get_width(), u7.get_width(), u8.get_width(),
                       start_text.get_width()) + 40

        button_h = u1.get_height() + 20

        r1 = pygame.Rect(0, 0, button_w, button_h)
        r2 = pygame.Rect(0, 0, button_w, button_h)
        r3 = pygame.Rect(0, 0, button_w, button_h)
        r4 = pygame.Rect(0, 0, button_w, button_h)
        r5 = pygame.Rect(0, 0, button_w, button_h)
        r6 = pygame.Rect(0, 0, button_w, button_h)
        r7 = pygame.Rect(0, 0, button_w, button_h)
        r8 = pygame.Rect(0, 0, button_w, button_h)
        rstart = pygame.Rect(0, 0, button_w, button_h)

        r1.center = (WIDTH // 2, 200)
        r2.center = (WIDTH // 2, 250)
        r3.center = (WIDTH // 2, 300)
        r4.center = (WIDTH // 2, 350)
        r5.center = (WIDTH // 2, 400)
        r6.center = (WIDTH // 2, 450)
        r7.center = (WIDTH // 2, 500)
        r8.center = (WIDTH // 2, 550)
        rstart.center = (WIDTH // 2, 620)

        mx, my = pygame.mouse.get_pos()


        def hover(rect):
            return (255, 255, 0) if rect.collidepoint(mx, my) else (255, 255, 255)


        pygame.draw.rect(win, hover(r1), r1, 2)
        pygame.draw.rect(win, hover(r2), r2, 2)
        pygame.draw.rect(win, hover(r3), r3, 2)
        pygame.draw.rect(win, hover(r4), r4, 2)
        pygame.draw.rect(win, hover(r5), r5, 2)
        pygame.draw.rect(win, hover(r6), r6, 2)
        pygame.draw.rect(win, hover(r7), r7, 2)
        pygame.draw.rect(win, hover(r8), r8, 2)
        pygame.draw.rect(win, hover(rstart), rstart, 2)

        win.blit(u1, (r1.centerx - u1.get_width() // 2, r1.centery - u1.get_height() // 2))
        win.blit(u2, (r2.centerx - u2.get_width() // 2, r2.centery - u2.get_height() // 2))
        win.blit(u3, (r3.centerx - u3.get_width() // 2, r3.centery - u3.get_height() // 2))
        win.blit(u4, (r4.centerx - u4.get_width() // 2, r4.centery - u4.get_height() // 2))
        win.blit(u5, (r5.centerx - u5.get_width() // 2, r5.centery - u5.get_height() // 2))
        win.blit(u6, (r6.centerx - u6.get_width() // 2, r6.centery - u6.get_height() // 2))
        win.blit(u7, (r7.centerx - u7.get_width() // 2, r7.centery - u7.get_height() // 2))
        win.blit(u8, (r8.centerx - u8.get_width() // 2, r8.centery - u8.get_height() // 2))
        win.blit(start_text,
                 (rstart.centerx - start_text.get_width() // 2, rstart.centery - start_text.get_height() // 2))

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if r1.collidepoint(mx, my) and score >= cost:
                    score -= cost
                    upgrade_health += 10
                if r2.collidepoint(mx, my) and score >= cost:
                    score -= cost
                    upgrade_shield += 1
                if r3.collidepoint(mx, my) and score >= cost:
                    score -= cost
                    upgrade_lightning += 1
                if r4.collidepoint(mx, my) and score >= cost:
                    score -= cost
                    upgrade_speed += 1
                if r5.collidepoint(mx, my) and score >= cost:
                    score -= cost
                    upgrade_fire_rate += 1
                if r6.collidepoint(mx, my) and score >= cost:
                    score -= cost
                    upgrade_triple += 1
                if r7.collidepoint(mx, my) and score >= cost:
                    score -= cost
                    upgrade_nuke += 1
                if r8.collidepoint(mx, my) and score >= cost:
                    score -= cost
                    upgrade_magnet += 1
                if rstart.collidepoint(mx, my):
                    restart_game()
                    game_state = "game"

        pygame.display.update()
        clock.tick(60)
        continue

    if game_over or run_won:
        bg_full = pygame.transform.scale(background, (WIDTH, HEIGHT))
        win.blit(bg_full, (0, 0))

        font = pygame.font.Font('pixel_text.ttf', 48)
        small_font = pygame.font.Font('pixel_text.ttf', 32)

        if game_over:
            title_text = font.render("GAME OVER", True, (255, 0, 0))
        else:
            title_text = font.render("RUN WON", True, (255, 165, 0))

        win.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 120))

        score_text = small_font.render(f"SCORE: {score}", True, (255, 255, 255))
        win.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 180))

        restart_text = small_font.render("RESTART", True, (255, 255, 255))
        menu_text = small_font.render("MENU", True, (255, 255, 255))
        shop_text = small_font.render("SHOP", True, (255, 255, 255))
        quit_text = small_font.render("QUIT", True, (255, 255, 255))

        button_w = max(restart_text.get_width(), menu_text.get_width(), shop_text.get_width(),
                       quit_text.get_width()) + 40
        button_h = restart_text.get_height() + 20

        restart_rect = pygame.Rect(0, 0, button_w, button_h)
        menu_rect = pygame.Rect(0, 0, button_w, button_h)
        shop_rect = pygame.Rect(0, 0, button_w, button_h)
        quit_rect = pygame.Rect(0, 0, button_w, button_h)

        restart_rect.center = (WIDTH // 2, 300)
        menu_rect.center = (WIDTH // 2, 360)
        shop_rect.center = (WIDTH // 2, 420)
        quit_rect.center = (WIDTH // 2, 480)

        mx, my = pygame.mouse.get_pos()


        def hover(rect):
            return (255, 255, 0) if rect.collidepoint(mx, my) else (255, 255, 255)

        pygame.draw.rect(win, hover(restart_rect), restart_rect, 2)
        pygame.draw.rect(win, hover(menu_rect), menu_rect, 2)
        pygame.draw.rect(win, hover(shop_rect), shop_rect, 2)
        pygame.draw.rect(win, hover(quit_rect), quit_rect, 2)
        win.blit(restart_text, (restart_rect.centerx - restart_text.get_width() // 2,
                                restart_rect.centery - restart_text.get_height() // 2))
        win.blit(menu_text, (menu_rect.centerx - menu_text.get_width() // 2,
                             menu_rect.centery - menu_text.get_height() // 2))
        win.blit(shop_text, (shop_rect.centerx - shop_text.get_width() // 2,
                             shop_rect.centery - shop_text.get_height() // 2))
        win.blit(quit_text, (quit_rect.centerx - quit_text.get_width() // 2,
                             quit_rect.centery - quit_text.get_height() // 2))

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if restart_rect.collidepoint(mx, my):
                    restart_game()
                    game_state = "game"

                if menu_rect.collidepoint(mx, my):
                    restart_game()
                    game_state = "title"

                if shop_rect.collidepoint(mx, my):
                    game_state = "shop"

                if quit_rect.collidepoint(mx, my):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()
        clock.tick(60)
        continue

    if not boss_active and score >= 10000 and not game_over and not run_won:
        boss_active = True
        enemies = []
        enemy_lasers = []
        boss_bullets = []
        boss_health = boss_max_health
        boss = Boss(GAME_W // 2 - 32, 20, boss_image_raw)

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        char_x -= char_speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        char_x += char_speed
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        char_y -= char_speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        char_y += char_speed

    char_x = max(0, min(GAME_W - 16, char_x))
    char_y = max(0, min(GAME_H - 16, char_y))

    shake_x = 0
    shake_y = 0
    if screen_shake > 0:
        shake_x = random.randint(-5, 5)
        shake_y = random.randint(-5, 5)
        screen_shake -= 1

    bg_y1 += bg_speed
    bg_y2 += bg_speed
    if bg_y1 >= GAME_H:
        bg_y1 = -GAME_H
    if bg_y2 >= GAME_H:
        bg_y2 = -GAME_H

    game_surface.blit(background, (shake_x, bg_y1 + shake_y))
    game_surface.blit(background, (shake_x, bg_y2 + shake_y))

    player_image = get_sprite(player, 3, 3)
    game_surface.blit(player_image, (char_x, char_y))

    laser_counter += 1

    current_cooldown = laser_cooldown
    if rapid_fire_timer > 0:
        current_cooldown = max(10, laser_cooldown // 5)

    if laser_counter >= current_cooldown:
        laser_counter = 0
    if rapid_fire_timer > 0:
        rapid_fire_timer -= 1
    if keys[pygame.K_SPACE] and laser_counter == 0:
        if triple_shot_timer > 0:

            laser_list.append({"laser_rect": pygame.Rect(char_x + 7, char_y, 2, 8)})
            laser_list.append({"laser_rect": pygame.Rect(char_x + 2, char_y, 2, 8)})
            laser_list.append({"laser_rect": pygame.Rect(char_x + 12, char_y, 2, 8)})
        else:
            laser_list.append({"laser_rect": pygame.Rect(char_x + 7, char_y, 2, 8)})

        laser_counter = 1
        laser_sound.play()

    for laser in laser_list:
        pygame.draw.rect(game_surface, (255, 255, 255), laser["laser_rect"])
        laser["laser_rect"].y -= laser_speed

    laser_list = [laser for laser in laser_list if laser["laser_rect"].y > -10]

    for laser in laser_list[:]:
        if boss_active and boss is not None:
            boss_rect = pygame.Rect(boss.x, boss.y, boss.width, boss.height)
            if laser["laser_rect"].colliderect(boss_rect):
                explosions.append([boss.x + boss.width // 2, boss.y + boss.height // 2, 0])
                laser_list.remove(laser)
                boss_health -= 25
                score += 50
                score_animation = 6
                if boss_health <= 0:
                    boss_active = False
                    boss = None
                    boss_bullets = []
                    run_won = True
                continue

        for enemy in enemies[:]:
            enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
            if laser["laser_rect"].colliderect(enemy_rect):
                explosions.append([enemy.x, enemy.y, 0])
                if random.randint(1, 9) == 1:
                    kind = random.choice(["rapid", "triple", "health"])
                    powerups.append(PowerUp(enemy.x, enemy.y, kind))
                enemies.remove(enemy)
                explosion_sound.play()
                explosion_sound.set_volume(0.2)
                laser_list.remove(laser)
                score += 100
                score_animation = 6
                break

    for enemy in enemies[:]:
        if isinstance(enemy, KamikazeEnemy):
            if enemy.x < -50 or enemy.x > GAME_W + 50 or enemy.y < -50 or enemy.y > GAME_H + 50:
                enemies.remove(enemy)
                continue

        if isinstance(enemy, Enemy):
            if random.randint(1, 80) == 1:
                enemy_lasers.append(
                    pygame.Rect(enemy.x + enemy.width // 2, enemy.y + enemy.height, 3, 10)
                )

        if isinstance(enemy, DroneEnemy) and enemy.zone_active:
            pygame.draw.rect(game_surface, (255, 0, 0), enemy.zone_rect, 2)
            inner = pygame.Surface((enemy.zone_rect.width, enemy.zone_rect.height), pygame.SRCALPHA)
            inner.fill((255, 0, 0, 80))
            game_surface.blit(inner, (enemy.zone_rect.x, enemy.zone_rect.y))

            player_rect = pygame.Rect(char_x, char_y, 16, 16)

            if player_rect.colliderect(enemy.zone_rect):
                player_health -= 5
                health_flash = 2
                screen_shake = 2
                if player_health <= 0:
                    game_over = True

            if enemy.zone_timer <= 0:
                enemies.remove(enemy)

        enemy.draw(game_surface)

    if boss_active and boss is not None:
        boss.update()
        boss.draw(game_surface)

    for ex in explosions[:]:
        frame = explosion_frames[ex[2]]
        game_surface.blit(frame, (ex[0], ex[1]))
        ex[2] += 1
        if ex[2] >= len(explosion_frames):
            explosions.remove(ex)

    if score_animation > 0:
        size = score_size + score_animation
        score_animation -= 1
    else:
        size = score_size

    for el in enemy_lasers[:]:
        el.y += enemy_laser_speed
        pygame.draw.rect(game_surface, (255, 0, 0), el)

    player_rect = pygame.Rect(char_x, char_y, 16, 16)
    for p in powerups[:]:
        p.update()
        p.draw(game_surface)

        if p.rect.colliderect(player_rect):
            apply_powerup(p.kind)
            powerups.remove(p)

    if triple_shot_timer > 0:
        triple_shot_timer -= 1

    for el in enemy_lasers[:]:
        if player_rect.colliderect(el):
            player_health -= 25
            enemy_lasers.remove(el)
            health_flash = 8
            screen_shake = 8
            hit_sound.play()
            hit_sound.set_volume(0.2)
            if player_health <= 0:
                game_over = True

    enemy_lasers = [el for el in enemy_lasers if el.y < GAME_H]

    if boss_active and boss is not None:
        for b in boss_bullets[:]:
            b["x"] += b["dx"]
            b["y"] += b["dy"]
            pygame.draw.rect(game_surface, (255, 200, 50), (b["x"], b["y"], 4, 4))
            if b["y"] > GAME_H or b["x"] < -10 or b["x"] > GAME_W + 10:
                boss_bullets.remove(b)
                continue
            if player_rect.colliderect(pygame.Rect(b["x"], b["y"], 4, 4)):
                player_health -= 20
                boss_bullets.remove(b)
                health_flash = 5
                screen_shake = 6
                if player_health <= 0:
                    game_over = True

        if boss is not None and boss.laser_state == "firing":
            laser_rect = pygame.Rect(
                boss.laser_x - 3,
                boss.y + boss.height,
                6,
                GAME_H - (boss.y + boss.height)
            )
            if player_rect.colliderect(laser_rect):
                player_health -= 5
                health_flash = 3
                screen_shake = 3
                if player_health <= 0:
                    game_over = True

    enemy_lasers = [el for el in enemy_lasers if el.y < GAME_H]

    player_rect = pygame.Rect(char_x, char_y, 16, 16)
    for enemy in enemies[:]:
        if isinstance(enemy, KamikazeEnemy):
            enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
            if player_rect.colliderect(enemy_rect):
                player_health -= 40
                enemies.remove(enemy)
                health_flash = 12
                screen_shake = 12
                if player_health <= 0:
                    game_over = True

    if display_health > player_health:
        display_health -= 1
    elif display_health < player_health:
        display_health += 1

    scaled = pygame.transform.scale(game_surface, (WIDTH, HEIGHT))
    win.blit(scaled, (0, 0))

    ui_font = pygame.font.Font('pixel_text.ttf', 24)
    score_text = ui_font.render(f"Score: {score}", True, (255, 255, 255))
    win.blit(score_text, (10, 10))

    pygame.draw.rect(win, (100, 0, 0), (10, 50, 165, 15))

    health_ratio = display_health / player_max_health
    segments = 33
    segment_width = 165 // segments
    filled_segments = int(segments * health_ratio)

    for i in range(filled_segments):
        x = 10 + i * segment_width
        pygame.draw.rect(win, (0, 255, 0), (x, 50, segment_width - 1, 15))

    if boss_active and boss is not None:
        bar_w = 260
        bar_h = 18
        bx = WIDTH // 2 - bar_w // 2
        by = 10
        pygame.draw.rect(win, (60, 0, 0), (bx, by, bar_w, bar_h))
        if boss_health < 0:
            boss_health = 0
        bratio = boss_health / boss_max_health
        pygame.draw.rect(win, (255, 60, 60), (bx, by, int(bar_w * bratio), bar_h))

    pygame.display.update()
    clock.tick(60)
