import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.speed = 5
        self.hp = 100
        self.damage = 10

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - self.rect.width))

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)

    def upgrade_hp(self):
        self.hp += 20

    def upgrade_damage(self):
        self.damage += 5

    def upgrade_speed(self):
        self.speed += 1

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = -10

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, wave):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = 1 + wave // 10
        self.hp = 10 + wave * 2
        self.damage = 5 + wave

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
            global game_over
            game_over = True

# Game setup
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

# Wave management
current_wave = 0
max_waves = 30
enemies_per_wave = 5
game_over = False



def spawn_enemies(wave):
    for _ in range(enemies_per_wave + wave // 2):
        enemy = Enemy(wave)
        all_sprites.add(enemy)
        enemies.add(enemy)

def show_upgrade_screen(screen):
    font = pygame.font.Font(None, 36)
    text1 = font.render("Выберите улучшение:", True, WHITE)
    text2 = font.render("1 - Увеличить HP на 20", True, WHITE)
    text3 = font.render("2 - Увеличить урон на 5", True, WHITE)
    text4 = font.render("3 - Увеличить скорость на 1", True, WHITE)
    screen.blit(text1, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
    screen.blit(text2, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
    screen.blit(text3, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50))
    screen.blit(text4, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    player.upgrade_hp()
                    waiting = False
                elif event.key == pygame.K_2:
                    player.upgrade_damage()
                    waiting = False
                elif event.key == pygame.K_3:
                    player.upgrade_speed()
                    waiting = False

def show_start_screen(screen):
    font = pygame.font.Font(None, 74)
    title = font.render("Космическая Осада", True, WHITE)
    instructions = font.render("Нажмите любую клавишу для начала", True, WHITE)
    screen.blit(title, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 50))
    screen.blit(instructions, (SCREEN_WIDTH // 2 - 350, SCREEN_HEIGHT // 2 + 50))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False
    screen.fill(BLACK)

# Main game loop
def main():
    global current_wave, game_over
    pygame.display.set_caption("Космическая Осада")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    show_start_screen(screen)

    running = True
    while running:
        if game_over:
            font = pygame.font.Font(None, 74)
            text = font.render("Игра окончена", True, WHITE)
            screen.blit(text, (SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2))
            pygame.display.flip()
            pygame.time.wait(3000)
            running = False
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot()

        all_sprites.update()

        # Check for collisions
        hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
        for enemy in hits:
            enemy.hp -= player.damage
            if enemy.hp <= 0:
                enemy.kill()

        # Spawn new wave if all enemies are defeated
        if len(enemies) == 0:
            if current_wave <= max_waves:
                spawn_enemies(current_wave)
                show_upgrade_screen(screen)
                current_wave += 1
            else:
                font = pygame.font.Font(None, 74)
                text = font.render("Победа!", True, WHITE)
                screen.blit(text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
                pygame.display.flip()
                pygame.time.wait(3000)
                running = False

        # Draw everything
        screen.fill(BLACK)
        all_sprites.draw(screen)

        # Draw wave info
        font = pygame.font.Font(None, 36)
        wave_text = font.render(f"Волна: {current_wave}", True, WHITE)
        screen.blit(wave_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
