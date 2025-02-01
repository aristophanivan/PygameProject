import pygame
import random
from database_setup import database

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class Player:
    def __init__(self):
        self.hp = 100
        self.max_hp = 100
        self.speed = 5
        self.damage = 10
        self.fire_rate = 1.0  # Fire rate multiplier
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 50
        self.shoot_cooldown = 0  # Cooldown timer for shooting
        self.sprite = pygame.image.load("data/player.png")  # Load player sprite
        self.sprite = pygame.transform.scale(self.sprite, (40, 40))

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - 40:
            self.x += self.speed

    def shoot(self, bullets):
        if self.shoot_cooldown == 0:  # Only shoot if cooldown is 0
            bullets.append(Bullet(self.x + 18, self.y, -10))
            self.shoot_cooldown = int(15 / self.fire_rate)  # Adjust cooldown by fire rate

    def cooldown(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def draw(self, screen):
        screen.blit(self.sprite, (self.x, self.y))

class Enemy:
    def __init__(self, wave):
        self.hp = 10 + wave * 3 // 2
        self.speed = 1 + wave // 10
        self.damage = 5 + wave // 2
        self.x = random.randint(0, SCREEN_WIDTH - 40)
        self.y = random.randint(-200, -50)
        self.direction = random.choice([-1, 1])
        self.shoot_cooldown = random.randint(60, 120)

    def move(self):
        if self.y < SCREEN_HEIGHT // 2:
            self.y += self.speed
        else:
            self.x += self.direction * self.speed
            if self.x <= 0 or self.x >= SCREEN_WIDTH - 40:
                self.direction *= -1

    def shoot(self, bullets):
        if self.shoot_cooldown <= 0:
            bullets.append(Bullet(self.x + 18, self.y + 40, 10))
            self.shoot_cooldown = random.randint(90, 150)
        else:
            self.shoot_cooldown -= 1

    def draw(self, screen):
        pygame.draw.rect(screen, RED, (self.x, self.y, 40, 40))

class Bullet:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed

    def move(self):
        self.y += self.speed

    def draw(self, screen):
        color = BLUE if self.speed < 0 else RED
        pygame.draw.rect(screen, color, (self.x, self.y, 5, 10))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Shooter")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.running = True
        self.wave = 1
        self.total_enemies = 20
        self.enemies_killed = 0
        self.enemies = []
        self.player = Player()
        self.player_bullets = []
        self.enemy_bullets = []
        self.state = "menu"  # menu, game, pause, game_over, upgrade, enter_name
        self.player_name = "enter your name"  # New attribute for player name
        self.leaderboard = []  # New attribute for leaderboard
        self.game_over_timer = 0
        self.database = database()
        
    def draw_text(self, text, x, y, color=WHITE):
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))

    def spawn_enemies(self):
        remaining = self.total_enemies - self.enemies_killed
        count = min(3, remaining)
        self.enemies.extend([Enemy(self.wave) for _ in range(count)])

    def handle_collisions(self):
        # Player bullets vs enemies
        for bullet in self.player_bullets[:]:
            for enemy in self.enemies[:]:
                if (enemy.x < bullet.x < enemy.x + 40 and
                        enemy.y < bullet.y < enemy.y + 40):
                    enemy.hp -= self.player.damage
                    self.player_bullets.remove(bullet)
                    if enemy.hp <= 0:
                        self.enemies.remove(enemy)
                        self.enemies_killed += 1
                    break

        # Enemy bullets vs player
        for bullet in self.enemy_bullets[:]:
            if (self.player.x < bullet.x < self.player.x + 40 and
                    self.player.y < bullet.y < self.player.y + 40):
                self.player.hp -= 10
                self.enemy_bullets.remove(bullet)

        # Player bullets vs enemy bullets (reflection)
        for player_bullet in self.player_bullets[:]:
            for enemy_bullet in self.enemy_bullets[:]:
                if (enemy_bullet.x < player_bullet.x < enemy_bullet.x + 5 and
                        enemy_bullet.y < player_bullet.y < enemy_bullet.y + 10):
                    self.player_bullets.remove(player_bullet)
                    self.enemy_bullets.remove(enemy_bullet)
                    break

    def draw_text(self, text, x, y, color=WHITE):
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))

    def reset_game(self):
        self.wave = 1
        self.total_enemies = 20
        self.enemies_killed = 0
        self.player = Player()
        self.player_bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.player_name = "enter your name"

    def upgrade_menu(self):
        self.screen.fill(BLACK)
        self.draw_text("Choose an Upgrade:", SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 100)
        self.draw_text("1: +20 HP", SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 - 50)
        self.draw_text("2: +5 Damage", SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2)
        self.draw_text("3: +0.5 Speed", SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 + 50)
        self.draw_text("4: +10% Fire Rate", SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 + 100)
        pygame.display.flip()

    def apply_upgrade(self, choice):
        if choice == pygame.K_1:
            self.player.max_hp += 20
            self.player.hp += 20
        elif choice == pygame.K_2:
            self.player.damage += 5
        elif choice == pygame.K_3:
            self.player.speed += 0.5
        elif choice == pygame.K_4:
            self.player.fire_rate += 0.1

    def run(self):
        while self.running:
            self.screen.fill(BLACK)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if self.state == "menu" and event.key == pygame.K_RETURN:
                        self.state = "enter_name"  # Transition to enter_name state
                    elif self.state == "pause" and event.key == pygame.K_RETURN:
                        self.state = "game"
                    elif self.state == "game" and event.key == pygame.K_ESCAPE:
                        self.state = "pause"
                    elif self.state == "upgrade":
                        self.apply_upgrade(event.key)
                        self.state = "game"
                    if self.state == "enter_name":
                        if event.key == pygame.K_RETURN and self.player_name != "enter your name":
                            self.state = "game"  # Transition back to menu after entering name
                        elif event.key == pygame.K_BACKSPACE:
                            self.player_name = self.player_name[:-1]
                        else:
                            self.player_name += event.unicode

            if self.state == "menu":
                data = self.database.get_player_progress()
                self.draw_text("Space Shooter", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50)
                self.draw_text("Press Enter to Start", SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2)
                self.draw_text("Leaderboard", SCREEN_WIDTH // 10 - 25, SCREEN_HEIGHT // 8 - 50)
                items = list(data.items())  # Преобразуем пары (ключ, значение) в список
                for i in range(len(items)):
                    key, value = items[i]
                    self.draw_text(str(key), 10, SCREEN_HEIGHT // 8 + i * 100)
                    self.draw_text(str(value), 210, SCREEN_HEIGHT // 8 + i * 100)

            elif self.state == "game":
                keys = pygame.key.get_pressed()
                self.player.move(keys)
                if keys[pygame.K_SPACE]:
                    self.player.shoot(self.player_bullets)

                self.player.cooldown()

                if not self.enemies and self.enemies_killed < self.total_enemies:
                    self.spawn_enemies()

                if self.enemies_killed >= self.total_enemies:
                    self.wave += 1
                    self.total_enemies = 20
                    self.enemies_killed = 0
                    self.player.hp = self.player.max_hp
                    self.player.max_hp += 2
                    self.state = "upgrade"

                self.handle_collisions()

                self.player_bullets = [b for b in self.player_bullets if b.y > 0]
                self.enemy_bullets = [b for b in self.enemy_bullets if b.y < SCREEN_HEIGHT]

                for bullet in self.player_bullets:
                    bullet.move()
                    bullet.draw(self.screen)

                for bullet in self.enemy_bullets:
                    bullet.move()
                    bullet.draw(self.screen)

                for enemy in self.enemies:
                    enemy.move()
                    enemy.shoot(self.enemy_bullets)
                    enemy.draw(self.screen)

                self.player.draw(self.screen)
                self.draw_text(f"HP: {self.player.hp}/{self.player.max_hp}", 10, 10)
                self.draw_text(f"Wave: {self.wave}", 10, 40)

                if self.player.hp <= 0:
                    self.database.save_player_progress(self.player_name, self.wave - 1)
                    self.state = "game_over"
                    self.game_over_timer = pygame.time.get_ticks()

            elif self.state == "pause":
                self.draw_text("Paused", SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 50)
                self.draw_text("Press Enter to Resume", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2)

            elif self.state == "upgrade":
                self.upgrade_menu()

            elif self.state == "game_over":
                elapsed_time = (pygame.time.get_ticks() - self.game_over_timer) / 1000
                if elapsed_time >= 10: 
                    self.reset_game()
                    self.state = "menu"
                else:
                    self.draw_text("Game Over", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50)
                    self.draw_text(f"Returning to menu in {10 - int(elapsed_time)} seconds", SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2)
            elif self.state == "enter_name":
                self.draw_text("Enter your name:", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50)
                self.draw_text(self.player_name, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
