import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Detect the current screen size
infoObject = pygame.display.Info()
WINDOW_WIDTH = infoObject.current_w
WINDOW_HEIGHT = infoObject.current_h

# Optionally set the display mode to fullscreen
screen = pygame.display.set_mode(
    (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN
)
pygame.display.set_caption("Growth Game")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Scale sizes relative to screen dimensions
PLAYER_START_SIZE = int(WINDOW_HEIGHT * 0.05)  # 5% of screen height
FOOD_SIZE = int(WINDOW_HEIGHT * 0.06)          # Changed from 0.04 to 0.06 (6% of screen height)
GROWTH_AMOUNT = int(PLAYER_START_SIZE * 0.2)
SHRINK_AMOUNT = int(PLAYER_START_SIZE * 0.3)
FOOD_LIFETIME = 4  # Changed from 2 to 4 seconds
GAME_DURATION = 390  # Game length in seconds
FPS = 60

# Load and scale images
chompy_open = pygame.image.load('Assets/sprites/Chompy_mouth_open.png')
chompy_closed = pygame.image.load('Assets/sprites/Chompy_mouth_closed.png')
background_beach = pygame.image.load('Assets/backgrounds/beach_bg.png')
background_playground = pygame.image.load('Assets/backgrounds/playground_bg.png')

# Load food sprites
GOOD_FOODS = {
    'banana': pygame.image.load('Assets/sprites/Banana.png'),
    'grape': pygame.image.load('Assets/sprites/Grape.png'),
    'kiwi': pygame.image.load('Assets/sprites/Kiwi fruit.png'),
    'pineapple': pygame.image.load('Assets/sprites/pineapple.png'),
    'strawberry': pygame.image.load('Assets/sprites/Strawberry.png'),
    'watermelon': pygame.image.load('Assets/sprites/watermelon.png')
}

BAD_FOODS = {
    'poop': pygame.image.load('Assets/sprites/poop.png')
}

# Scale all food sprites
for sprite_dict in [GOOD_FOODS, BAD_FOODS]:
    for name, sprite in sprite_dict.items():
        sprite_dict[name] = pygame.transform.scale(sprite, (FOOD_SIZE, FOOD_SIZE))

# Scale background images to fit the screen
background_beach = pygame.transform.scale(
    background_beach, (WINDOW_WIDTH, WINDOW_HEIGHT)
)
background_playground = pygame.transform.scale(
    background_playground, (WINDOW_WIDTH, WINDOW_HEIGHT)
)

class Player:
    def __init__(self):
        self.size = PLAYER_START_SIZE
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT // 2
        self.dragging = False
        self.chomping = False
        self.image = chompy_closed
        self.last_chomp_time = time.time()
        self.width = self.size * 2
        self.height = self.size * 2

    def draw(self):
        # Swap images to simulate chomping
        current_time = time.time()
        if current_time - self.last_chomp_time > 0.5:
            self.chomping = not self.chomping
            self.image = chompy_open if self.chomping else chompy_closed
            self.last_chomp_time = current_time

        # Scale the image according to self.size
        scaled_image = pygame.transform.scale(
            self.image, (self.size * 2, self.size * 2)
        )
        self.width = self.size * 2
        self.height = self.size * 2

        # Draw the scaled image centered on (self.x, self.y)
        screen.blit(
            scaled_image,
            (int(self.x) - self.width // 2, int(self.y) - self.height // 2)
        )

    def move_to(self, pos):
        self.x = max(self.width // 2, min(pos[0], WINDOW_WIDTH - self.width // 2))
        self.y = max(self.height // 2, min(pos[1], WINDOW_HEIGHT - self.height // 2))

    def grow(self):
        self.size += GROWTH_AMOUNT

    def shrink(self):
        self.size = max(PLAYER_START_SIZE, self.size - SHRINK_AMOUNT)

    def collides_with(self, food):
        distance = ((self.x - food.x) ** 2 + (self.y - food.y) ** 2) ** 0.5
        return distance < (self.size + FOOD_SIZE // 2)

class Food:
    def __init__(self, is_good=True):
        self.spawn_time = time.time()
        self.active = True
        self.reset(is_good)

    def reset(self, is_good=True):
        self.x = random.randint(FOOD_SIZE, WINDOW_WIDTH - FOOD_SIZE)
        self.y = random.randint(FOOD_SIZE, WINDOW_HEIGHT - FOOD_SIZE)
        self.is_good = is_good
        if is_good:
            self.food_type = random.choice(list(GOOD_FOODS.keys()))
            self.sprite = GOOD_FOODS[self.food_type]
        else:
            self.food_type = random.choice(list(BAD_FOODS.keys()))
            self.sprite = BAD_FOODS[self.food_type]
        self.spawn_time = time.time()
        self.active = True

    def draw(self):
        if not self.active:
            return

        # Calculate fade based on lifetime
        time_alive = time.time() - self.spawn_time
        fade = max(0, 1 - (time_alive / FOOD_LIFETIME))

        # Create a copy of the sprite for transparency
        sprite_copy = self.sprite.copy()
        sprite_copy.set_alpha(int(255 * fade))
        
        # Draw the sprite centered at (x, y)
        screen.blit(
            sprite_copy,
            (int(self.x - FOOD_SIZE // 2), int(self.y - FOOD_SIZE // 2))
        )

    def update(self):
        if self.active and time.time() - self.spawn_time > FOOD_LIFETIME:
            self.active = False
            return True
        return False

def spawn_new_food(foods):
    # Only spawn if we have less than 3 active foods
    active_foods = sum(1 for food in foods if food.active)
    if active_foods < 3 and random.random() < 0.02:
        is_good = random.random() < 0.9  # Changed from 0.7 to 0.9 (90% chance of good food)
        for food in foods:
            if not food.active:
                food.reset(is_good)
                break

def main():
    player = Player()
    foods = [Food() for _ in range(3)]  # Create food pool
    score = 0
    game_start_time = time.time()
    font_size = int(WINDOW_HEIGHT * 0.05)
    font = pygame.font.Font(None, font_size)

    # Choose a background
    background = background_beach if random.random() < 0.5 else background_playground

    running = True
    while running:
        current_time = time.time()
        time_remaining = max(0, GAME_DURATION - (current_time - game_start_time))

        # End game if timer runs out
        if time_remaining <= 0:
            running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Mouse Events
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                # Create a rect for the player
                player_rect = pygame.Rect(
                    int(player.x - player.width // 2),
                    int(player.y - player.height // 2),
                    player.width,
                    player.height
                )
                if player_rect.collidepoint(mouse_pos):
                    player.dragging = True
            elif event.type == pygame.MOUSEBUTTONUP:
                player.dragging = False
            elif event.type == pygame.MOUSEMOTION and player.dragging:
                player.move_to(event.pos)
            # Touch Events
            elif event.type == pygame.FINGERDOWN:
                touch_x = event.x * WINDOW_WIDTH
                touch_y = event.y * WINDOW_HEIGHT
                player_rect = pygame.Rect(
                    int(player.x - player.width // 2),
                    int(player.y - player.height // 2),
                    player.width,
                    player.height
                )
                if player_rect.collidepoint((touch_x, touch_y)):
                    player.dragging = True
            elif event.type == pygame.FINGERUP:
                player.dragging = False
            elif event.type == pygame.FINGERMOTION and player.dragging:
                touch_x = event.x * WINDOW_WIDTH
                touch_y = event.y * WINDOW_HEIGHT
                player.move_to((touch_x, touch_y))

        # Update player position if dragging
        if player.dragging:
            mouse_pos = pygame.mouse.get_pos()
            player.move_to(mouse_pos)

        # Update and check collisions with food
        for food in foods:
            if food.active and player.collides_with(food):
                if food.is_good:
                    player.grow()
                    score += 10
                else:
                    player.shrink()
                    score -= 5
                food.active = False
            food.update()

        # Maybe spawn new food
        spawn_new_food(foods)

        # Draw everything
        screen.blit(background, (0, 0))  # Draw the background

        # Draw foods
        for food in foods:
            food.draw()

        # Draw player
        player.draw()

        # Draw score and timer
        score_text = font.render(f"Score: {score}", True, BLACK)
        time_text = font.render(f"Time: {int(time_remaining)}s", True, BLACK)
        screen.blit(score_text, (10, 10))
        screen.blit(time_text, (10, 10 + font_size))

        pygame.display.flip()
        clock.tick(FPS)

    # Game over screen
    screen.fill(WHITE)
    game_over_text = font.render(f"Game Over! Final Score: {score}", True, BLACK)
    screen.blit(
        game_over_text,
        (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2,
         WINDOW_HEIGHT // 2 - game_over_text.get_height() // 2)
    )
    pygame.display.flip()

    # Wait a few seconds before closing
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    main()
