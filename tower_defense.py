import pygame
import json
import random
import math

# Initialize Pygame
pygame.init()

# Set up the game window
WIDTH = 800
HEIGHT = 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defense Game")

# Define colors
WHITE = (255, 255, 255)
LIGHT_GREY = (200, 200, 200)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Define game variables
FPS = 60
SLOWMOTION = 30
clock = pygame.time.Clock()
is_running = True
game_over = False
is_playing = True
is_slowmotion = False

def load_config():
    with open('config.json') as file:
        data = json.load(file)
        return data
    
data = load_config()
enemy_data = data["enemies"]
tower_data = data["towers"]
level_data = data["levels"]
current_lvl = 1

level_start_time = pygame.time.get_ticks()
pause_time = 0

# Define classes for Tower, Enemy, and Projectile
class Tower(pygame.sprite.Sprite):
    def __init__(self, x, y, _type):
        pygame.sprite.Sprite.__init__(self)
        self.type = _type
        
        # Retrieve enemy attributes from config based on enemy_type
        self.data = tower_data[_type]
        self.dmg = self.data['dmg']
        self.p_speed = self.data['p_speed']
        self.attack_range = self.data['range']
        self.cost = self.data['cost']
        self.attack_cooldown = self.data['cooldown']  # milliseconds
        self.color = self.data['color']
        
        self.image = pygame.Surface((50, 50))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.last_attack_time = pygame.time.get_ticks()

    def attack(self, target):
        # Calculate the angle between the tower and the target
        dx = target.rect.centerx - self.rect.centerx
        dy = target.rect.centery - self.rect.centery
        angle = math.atan2(dy, dx)

        # Create a projectile and launch it towards the target
        projectile = Projectile(self.rect.centerx, self.rect.centery, angle, self.dmg, self.p_speed)
        all_sprites.add(projectile)
        projectiles.add(projectile)
        
    def handle_event(self, event):
        pass

    def draw_range(self):
            range_color = BLACK
            range_alpha = 50  # Transparency value (0 - 255)
            range_pos = self.rect.center

            pygame.draw.circle(window, (range_color[0], range_color[1], range_color[2], range_alpha),
                            range_pos, self.attack_range, 1)
    def update(self):
        # Find the closest enemy within attack range
        target = None
        min_dist = self.attack_range
        for enemy in enemies:
            dist = math.hypot(enemy.rect.centerx - self.rect.centerx, enemy.rect.centery - self.rect.centery)
            if dist < min_dist:
                target = enemy
                min_dist = dist

        # Attack the target if available and cooldown is over
        if target and pygame.time.get_ticks() - self.last_attack_time > self.attack_cooldown:
            self.attack(target)
            self.last_attack_time = pygame.time.get_ticks()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, waypoints, _type):
        pygame.sprite.Sprite.__init__(self)
        self.type = _type
        
        # Retrieve enemy attributes from config based on enemy_type
        self.data = enemy_data[_type]
        self.max_health = self.data['health']
        self.max_armor = self.data['armor']
        self.mp = self.data['mp']
        self.speed = self.data['speed']
        self.reward = self.data['reward']
        self.size = self.data['size']
        self.spawn_rate = self.data['spawn_rate']
        self.color = self.data['color']
        self.player_dmg = self.data['player_dmg']
        
        self.last_spawn_time = pygame.time.get_ticks()
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.waypoints = waypoints
        self.current_waypoint_index = 0
        self.target_waypoint = self.waypoints[self.current_waypoint_index]
        self.offset = 10
        self.rect.x = self.target_waypoint[0] - self.offset
        self.rect.y = self.target_waypoint[1] - self.offset
        self.health = self.max_health
        self.armor = self.max_armor

    def update(self):
        # Move towards the current waypoint
        dx = self.target_waypoint[0] - self.rect.x - self.offset
        dy = self.target_waypoint[1] - self.rect.y - self.offset
        distance = math.hypot(dx, dy)
        if distance > 0:
            dx /= distance
            dy /= distance
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        print(f'x: {self.rect.x}, y: {self.rect.y}')
        

        # Check if reached the current waypoint
        if distance <= self.speed:
            self.current_waypoint_index += 1
            if self.current_waypoint_index < len(self.waypoints):
                self.target_waypoint = self.waypoints[self.current_waypoint_index]
            else:
                player_overlay.decrease_life(self.player_dmg)
                self.kill()

        if self.health <= 0:
            self.kill()

    def draw_health_bar(self):
        bar_width = self.rect.width
        bar_height = 5
        health_ratio = self.health / self.max_health
        filled_width = int(bar_width * health_ratio)
        if self.data['armor'] :
            bar_rect = pygame.Rect(self.rect.x, self.rect.y - bar_height - 10, filled_width, bar_height)
            outline_rect = pygame.Rect(self.rect.x, self.rect.y - bar_height - 10, bar_width, bar_height)
        else:
            bar_rect = pygame.Rect(self.rect.x, self.rect.y - bar_height - 5, filled_width, bar_height)
            outline_rect = pygame.Rect(self.rect.x, self.rect.y - bar_height - 5, bar_width, bar_height)
        
        if health_ratio > 0.5:
            color = GREEN
        elif health_ratio > 0.33:
            color = ORANGE
        else:
            color = RED
        
        pygame.draw.rect(window, color, bar_rect)
        pygame.draw.rect(window, BLACK, outline_rect, 1)
        
    def draw_armor_bar(self):
        bar_width = self.rect.width
        bar_height = 5
        if self.data['armor']:
            armor_ratio = self.armor / self.max_armor
            filled_width = int(bar_width * armor_ratio)
            bar_rect = pygame.Rect(self.rect.x, self.rect.y - bar_height - 5, filled_width, bar_height)
            outline_rect = pygame.Rect(self.rect.x, self.rect.y - bar_height - 5, bar_width, bar_height)
            
            pygame.draw.rect(window, BLUE, bar_rect)
            pygame.draw.rect(window, BLACK, outline_rect, 1)

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, damage, speed):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((10, 10))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = speed
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed
        self.physic_dmg = damage['physic']
        self.magic_dmg = damage['magic']
        self.brut_dmg = damage['brut']

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if self.rect.left > WIDTH or self.rect.right < 0 or self.rect.top > HEIGHT or self.rect.bottom < 0:
            self.kill()

class PlayerOverlay:
    def __init__(self, current_lvl_coin):
        self.max_life = 200
        self.life = self.max_life
        self.max_coin = current_lvl_coin
        self.coin = self.max_coin
        self.font = pygame.font.Font(None, 36)

    def decrease_life(self, amount):
        self.life -= amount
        if self.life < 0:
            self.life = 0
            
    def decrease_coin(self, amount):
        self.coin -= amount
        if self.coin < 0:
            self.coin = 0
    
    def increase_coin(self, amount):
        self.coin += amount
        if self.coin > 99999:
            self.coin = 99999

    def draw(self):
        life_text = self.font.render(f"Life: {self.life}", True, BLACK)
        coin_text = self.font.render(f"Coin: {self.coin}", True, BLACK)
        
        # Get current time since the start of a level
        elapsed_time = (pygame.time.get_ticks() - level_start_time) - pause_time
        minutes = int(elapsed_time / 60000)
        seconds = int((elapsed_time % 60000) / 1000)
        milliseconds = int((elapsed_time % 1000))
        time_str_milli = f"Time: {minutes:02d}:{seconds:02d}:{milliseconds:03d}"
        time_str = f"Time: {minutes:02d}:{seconds:02d}"
        
        time_text = self.font.render(time_str, True, BLACK)
        window.blit(life_text, (10, 10))
        window.blit(coin_text, (10, 40))
        window.blit(time_text, (600, 10))

class ReplayButton:
    def __init__(self):
        self.onHoverColor = BLUE
        self.rect = pygame.Rect(350, 250, 100, 50)
        self.font = pygame.font.Font(None, 36)
        self.is_clicked = False

    def draw(self):
        if self.is_hovered():
            pygame.draw.rect(window, self.onHoverColor, self.rect)
        else:
            pygame.draw.rect(window, WHITE, self.rect)
        pygame.draw.rect(window, BLACK, self.rect, 2)
        text = self.font.render("Replay", True, BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        window.blit(text, text_rect)

    def is_hovered(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered() and game_over:  # Only handle event if game over
                self.is_clicked = True

class PlaceTowerMenu:
    def __init__(self):
        self.onHoverColor = BLUE
        self.rect = pygame.Rect(350, 250, 100, 50)
        self.font = pygame.font.Font(None, 36)
        self.is_clicked = False

    def draw(self):
        pygame.draw.rect(window, LIGHT_GREY, self.rect)
        pygame.draw.rect(window, BLACK, self.rect, 2)
        text = self.font.render("Replay", True, BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        window.blit(text, text_rect)

    def is_hovered(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered() and game_over:  # Only handle event if game over
                self.is_clicked = True

# Define the waypoints for enemy movement
waypoints = level_data[str(current_lvl)]['waypoints']

# Create sprite groups
all_sprites = pygame.sprite.Group()
towers = pygame.sprite.Group()
enemies = pygame.sprite.Group()
projectiles = pygame.sprite.Group()

# Create player life counter
player_overlay = PlayerOverlay(int(level_data[str(current_lvl)]['player_stat']['coin']))

# Create replay button
replay_button = ReplayButton()

not_enough_coin = False
error_time = 1000

def pause(event):
    global is_running
    global is_playing
    global pause_time
    time =  pygame.time.get_ticks()
    
    while not is_playing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_playing = not is_playing
                is_running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    is_playing = not is_playing

        pause_font = pygame.font.Font(None, 62)
        pause_text = pause_font.render("PAUSE", True, BLACK)
        pause_text_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        window.blit(pause_text, pause_text_rect)
        # Refresh the display
        pygame.display.flip()
        clock.tick(FPS)
    pause_time = pygame.time.get_ticks() - time
    
def update_damage(enemies, projectiles):
    # Check for collisions between projectiles and enemies
    hits = pygame.sprite.groupcollide(projectiles, enemies, True, False)
    for projectile, enemy_list in hits.items():
        for enemy in enemy_list:
            update_armor = enemy.armor - projectile.physic_dmg
            update_health = enemy.health - projectile.brut_dmg
            update_mp = enemy.mp - projectile.magic_dmg
            
            if update_armor < 0:
                update_health += int(update_armor)
            if update_mp < 0:
                update_health += int(update_mp)
                
            enemy.armor = update_armor
            enemy.mp = update_mp
            enemy.health = update_health
            if enemy.health <= 0:
                return enemy.reward
            else:
                return

# Game loop
while is_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                is_playing = not is_playing
                pause(event)
            if event.key == pygame.K_SPACE:
                enemy = Enemy(waypoints, "goblin")
                all_sprites.add(enemy)
                enemies.add(enemy)
            if event.key == pygame.K_a:
                enemy = Enemy(waypoints, "orc")
                all_sprites.add(enemy)
                enemies.add(enemy)

        replay_button.handle_event(event)

        if game_over and replay_button.is_clicked:
            # Reset game state
            all_sprites.empty()
            towers.empty()
            enemies.empty()
            projectiles.empty()
            player_overlay.life = player_overlay.max_life
            player_overlay.coin = player_overlay.max_coin
            level_start_time = pygame.time.get_ticks()
            game_over = False
            replay_button.is_clicked = False
            break

        if not game_over:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                tower = Tower(mouse_pos[0], mouse_pos[1], 'sniper')
                if player_overlay.coin >= tower.cost:
                    all_sprites.add(tower)
                    towers.add(tower)
                    player_overlay.coin -= tower.cost
                else:
                    error_tick = pygame.time.get_ticks()
                    is_slowmotion = True
                    not_enough_coin = True

    if not game_over:
        # # Create new enemy
        # current_time = pygame.time.get_ticks()
        # spawn_rate = enemy_data['goblin']['spawn_rate']
        
        # if (current_time - level_start_time) % spawn_rate == 0:
        #     enemy = Enemy(waypoints, "goblin")
        #     all_sprites.add(enemy)
        #     enemies.add(enemy)
        
        # # Create new enemy
        # if random.randint(0, 100) < 1 :
        #     enemy = Enemy(waypoints, "armor goblin")
        #     all_sprites.add(enemy)
        #     enemies.add(enemy)
        
        # # Create new enemy
        # if random.randint(0, 1000) < 10 :
        #     enemy = Enemy(waypoints, "orc")
        #     all_sprites.add(enemy)
        #     enemies.add(enemy)
        
        # # Create new enemy
        # if random.randint(0, 1000) < 10 :
        #     enemy = Enemy(waypoints, "armor orc")
        #     all_sprites.add(enemy)
        #     enemies.add(enemy)

        # Update game
        all_sprites.update()
        
        coin_earn = update_damage(enemies, projectiles)
        
        if coin_earn:
            player_overlay.increase_coin(coin_earn)

        # Re-update game entities to check dead ones
        all_sprites.update()

        # Update towers' attacks
        for tower in towers:
            tower.update()

        # Check for game over condition
        if player_overlay.life == 0:
            game_over = True

    # Draw on the window
    window.fill(LIGHT_GREY)
    pygame.draw.lines(window, (200, 10, 10), False, waypoints, 35)  # Draw enemy path
    player_overlay.draw()  # Draw player life counter

    if game_over:
        replay_button.draw()  # Draw replay button
    else:
        for enemy in enemies:
            enemy.draw_health_bar()
            enemy.draw_armor_bar()
        all_sprites.draw(window)
        
     # Draw tower ranges
        for tower in towers:
            tower.draw_range()

    if not_enough_coin:
            if pygame.time.get_ticks() - error_tick > error_time:
                is_slowmotion = False
                not_enough_coin = False
            error_font = pygame.font.Font(None, 62)
            error_text = error_font.render("Not enough coins", True, RED)
            error_text_rect = error_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            window.blit(error_text, error_text_rect)

    # Refresh the display
    pygame.display.flip()
    if is_slowmotion:
        clock.tick(SLOWMOTION)
    else:
        clock.tick(FPS)

# Quit the game
pygame.quit()
