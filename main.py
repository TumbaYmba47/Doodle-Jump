import pygame
import random
from os import path
img_dir = path.join(path.dirname("__file__"), 'img')
snd_dir = path.join(path.dirname("__file__"), 'snd')
pygame.init()
pygame.mixer.init()
WIDTH = 1080
HEIGHT = 720
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Убей зомби!")
clock = pygame.time.Clock()
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
score = 0
skeleton_move = []
skeleton_escape = []
skeleton_list = ['skeleton-move_1.png', 'skeleton-move_2.png', 'skeleton-move_3.png',
                 'skeleton-move_4.png', 'skeleton-move_5.png', 'skeleton-move_6.png', 'skeleton-move_7.png',
                 'skeleton-move_8.png']
for img in skeleton_list:
    skeleton_move.append(pygame.transform.scale(pygame.image.load(path.join(img_dir, img)), (100, 50)))
skeleton_list = ['skeleton-escape_1.png', 'skeleton-escape_2.png', 'skeleton-escape_3.png',
                 'skeleton-escape_4.png', 'skeleton-escape_5.png', 'skeleton-escape_6.png', 'skeleton-escape_7.png',
                 'skeleton-escape_8.png']
for img in skeleton_list:
    skeleton_escape.append(pygame.transform.scale(pygame.image.load(path.join(img_dir, img)), (100, 50)))
city = pygame.transform.scale(pygame.image.load(path.join(img_dir, "city.png")), (WIDTH, 100))
background = pygame.transform.scale(pygame.image.load(path.join(img_dir, "background-1.png")), (WIDTH, HEIGHT))
background_rect = background.get_rect()
hammer = pygame.transform.scale(pygame.image.load(path.join(img_dir, "hammer.png")), (100, 100))
tank = pygame.transform.scale(pygame.image.load(path.join(img_dir, "tank.png")), (150, 150))
music = pygame.mixer.Sound(path.join(snd_dir, 'music.wav'))
fix = pygame.mixer.Sound(path.join(snd_dir, 'fix.wav'))
kill = pygame.mixer.Sound(path.join(snd_dir, 'kill.wav'))
preview = pygame.mixer.Sound(path.join(snd_dir, 'preview.wav'))
shot = pygame.mixer.Sound(path.join(snd_dir, 'shot.wav'))
victory = pygame.mixer.Sound(path.join(snd_dir, 'victory.wav'))
loss = pygame.mixer.Sound(path.join(snd_dir, 'loss.wav'))
shot.set_volume(0.4)
escape = False
all_escape = 0


def draw_text(text, size, y, x=WIDTH / 2):
    font_name = pygame.font.match_font('arial')
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    screen.blit(text_surface, text_rect)


def draw_shield_bar(x, y, pct):
    if pct < 0:
        pct = 0
    bar_length = 300
    bar_height = 30
    fill = (pct / 100) * bar_length
    outline_rect = pygame.Rect(x, y, bar_length, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    pygame.draw.rect(screen, GREEN, fill_rect)
    pygame.draw.rect(screen, WHITE, outline_rect, 2)


def end_game(text, size, y, sound):
    afk_time = pygame.time.get_ticks()
    music.stop()
    sound.play()
    screen.blit(background, background_rect)
    draw_text(text, size, y)
    pygame.display.flip()
    while pygame.time.get_ticks() - afk_time <= sound.get_length() * 1000:
        pass
    sound.stop()


def menu():
    music.stop()
    preview.play(-1)
    screen.blit(background, background_rect)
    draw_text("НА ГОРОД НАПАЛО 500 АБОЛТУСОВ ", 40, 200)
    draw_text("УБЕЙТЕ ИХ", 40, 300)
    draw_text("НАЖМИТЕ ЛЮБУЮ КНОПКУ ЧТОБЫ НАЧАТЬ", 40, 490)
    pygame.display.flip()
    wait = True
    while wait:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            if ev.type == pygame.KEYUP:
                preview.stop()
                wait = False
                return True


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = tank
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.speedy = 0

    def update(self):
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_a]:
            self.speedx = -12
        if keystate[pygame.K_d]:
            self.speedx = 12
        self.speedy = 0
        if keystate[pygame.K_w]:
            self.speedy = -12
        if keystate[pygame.K_s]:
            self.speedy = 12
        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        self.rect.y += self.speedy
        if self.rect.y < 0:
            self.rect.y = 0
        if self.rect.y > HEIGHT - 40:
            self.rect.y = HEIGHT - 40

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)


class Hp (pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = hammer
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.bottom = 0
        self.speedy = 0
        self.hp_take = 0

    def update(self):
        if score % 10 == 0 and score != 0 and score > self.hp_take:
            self.rect.bottom = random.randint(500, 600)
            self.rect.centerx = random.randint(WIDTH // 2 - 350, WIDTH // 2 + 350)
            self.hp_take = score


class Tower (pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = city
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = HEIGHT - 70
        self.shield = 100


class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = random.choice(skeleton_move)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(100, WIDTH - 100)
        self.rect.y = 0
        self.speedy = random.randrange(3, 8)

    def update(self):
        if not escape:
            self.image = random.choice(skeleton_move)
            if self.rect.top > HEIGHT:
                tower.shield -= 2
                self.rect.centerx = h
                self.rect.bottom = 0
                self.speedy = random.randrange(5, 10)
            self.rect.y += self.speedy
        else:
            self.image = random.choice(skeleton_escape)
            self.rect.y -= 4


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((10, 20))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()


all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
health = pygame.sprite.Group()
hp = Hp()
tower = Tower()
player = Player()
all_sprites.add(player, tower, hp)
health.add(hp)
mob = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
for i in range(10):
    mob[i] = Mob()
    all_sprites.add(mob[i])
    mobs.add(mob[i])
game_over = True
running = True
while running:
    if game_over:
        escape = False
        for i in range(10):
            mob[i].image = random.choice(skeleton_move)
            mob[i].rect.centerx = random.randint(100, WIDTH - 100)
            mob[i].rect.bottom = 0
            mob[i].speedy = random.randrange(5, 10)
        score = 0
        hp.hp_take = 0
        tower.shield = 100
        all_escape = 0
        if not menu():
            running = False
        music.play(-1)
        game_over = False
    clock.tick(FPS)
    h = random.randint(100, WIDTH - 100)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            player.shoot()
            shot.play()
    for k in range(10):
        if escape:
            if mob[k].rect.bottom < 0:
                all_escape += 1
        hit = pygame.sprite.spritecollide(mob[k], bullets, True)
        if hit:
            kill.play()
            mob[k].rect.centerx = h
            mob[k].rect.bottom = 0
            score += 1
    if all_escape < 10:
        all_escape = 0
    else:
        end_game("ПОБЕДА", 100, HEIGHT / 2 - 50, victory)
        game_over = True
    hit = pygame.sprite.spritecollide(player, health, False)
    if hit:
        fix.play()
        hp.rect.bottom = 0
        hp.speedy = 0
        if tower.shield + 10 >= 100:
            tower.shield = 100
        else:
            tower.shield += 10
    if tower.shield <= 0:
        end_game("ГОРОД УНИЧТОЖИЛИ", 100, HEIGHT / 2 - 50, loss)
        game_over = True
    if score >= 500:
        escape = True
    all_sprites.update()
    screen.blit(background, background_rect)
    draw_text(str(score), 40, 10)
    all_sprites.draw(screen)
    draw_shield_bar(5, 5, tower.shield)
    pygame.display.flip()
pygame.quit()
