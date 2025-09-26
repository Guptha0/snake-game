import pygame
import random
import sys
import time
from enum import Enum

# Initialize pygame
pygame.init()

# Game constants
class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 200, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)

class SnakeGame:
    def __init__(self):
        # Game settings
        self.cell_size = 20
        self.grid_width = 30
        self.grid_height = 20
        self.screen_width = self.cell_size * self.grid_width
        self.screen_height = self.cell_size * self.grid_height + 50  # Extra space for score
        
        # Game state
        self.difficulty = Difficulty.MEDIUM
        self.speed = self.get_speed()
        self.score = 0
        self.high_score = 0
        self.game_over = False
        self.paused = False
        
        # Initialize screen
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Snake Game - GitHub Edition")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 20)
        self.big_font = pygame.font.SysFont('Arial', 40)
        
        # Initialize game objects
        self.reset_game()
    
    def get_speed(self):
        """Get game speed based on difficulty"""
        speeds = {
            Difficulty.EASY: 8,
            Difficulty.MEDIUM: 12,
            Difficulty.HARD: 18
        }
        return speeds[self.difficulty]
    
    def reset_game(self):
        """Reset the game to initial state"""
        # Snake starts in the middle, moving right
        self.snake = [
            (self.grid_width // 2, self.grid_height // 2),
            (self.grid_width // 2 - 1, self.grid_height // 2),
            (self.grid_width // 2 - 2, self.grid_height // 2)
        ]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        
        # Generate first food
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        self.speed = self.get_speed()
    
    def generate_food(self):
        """Generate food at random position not occupied by snake"""
        while True:
            food = (random.randint(0, self.grid_width - 1), 
                   random.randint(0, self.grid_height - 1))
            if food not in self.snake:
                return food
    
    def handle_input(self):
        """Handle keyboard input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                elif event.key == pygame.K_1:
                    self.difficulty = Difficulty.EASY
                    self.speed = self.get_speed()
                elif event.key == pygame.K_2:
                    self.difficulty = Difficulty.MEDIUM
                    self.speed = self.get_speed()
                elif event.key == pygame.K_3:
                    self.difficulty = Difficulty.HARD
                    self.speed = self.get_speed()
                elif not self.paused:
                    # Direction changes (can't reverse)
                    if event.key == pygame.K_UP and self.direction != Direction.DOWN:
                        self.next_direction = Direction.UP
                    elif event.key == pygame.K_DOWN and self.direction != Direction.UP:
                        self.next_direction = Direction.DOWN
                    elif event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
                        self.next_direction = Direction.LEFT
                    elif event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
                        self.next_direction = Direction.RIGHT
    
    def update(self):
        """Update game state"""
        if self.game_over or self.paused:
            return
        
        # Update direction
        self.direction = self.next_direction
        
        # Calculate new head position
        head_x, head_y = self.snake[0]
        if self.direction == Direction.UP:
            new_head = (head_x, head_y - 1)
        elif self.direction == Direction.DOWN:
            new_head = (head_x, head_y + 1)
        elif self.direction == Direction.LEFT:
            new_head = (head_x - 1, head_y)
        elif self.direction == Direction.RIGHT:
            new_head = (head_x + 1, head_y)
        
        # Check for collisions with walls
        if (new_head[0] < 0 or new_head[0] >= self.grid_width or 
            new_head[1] < 0 or new_head[1] >= self.grid_height):
            self.game_over = True
            self.high_score = max(self.high_score, self.score)
            return
        
        # Check for collisions with self
        if new_head in self.snake:
            self.game_over = True
            self.high_score = max(self.high_score, self.score)
            return
        
        # Move snake
        self.snake.insert(0, new_head)
        
        # Check for food collision
        if new_head == self.food:
            self.score += 10 * self.difficulty.value
            self.food = self.generate_food()
            # Increase speed slightly with score (optional)
            if self.score % 100 == 0 and self.speed < 25:
                self.speed += 1
        else:
            # Remove tail if no food eaten
            self.snake.pop()
    
    def draw(self):
        """Draw everything on the screen"""
        self.screen.fill(BLACK)
        
        # Draw grid (optional, for better visualization)
        for x in range(0, self.screen_width, self.cell_size):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, self.screen_height - 50))
        for y in range(0, self.screen_height - 50, self.cell_size):
            pygame.draw.line(self.screen, GRAY, (0, y), (self.screen_width, y))
        
        # Draw snake
        for i, (x, y) in enumerate(self.snake):
            color = DARK_GREEN if i > 0 else GREEN  # Head is brighter
            rect = pygame.Rect(x * self.cell_size, y * self.cell_size, 
                             self.cell_size, self.cell_size)
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 1)  # Border
            
            # Draw eyes on head
            if i == 0:
                eye_size = self.cell_size // 5
                # Determine eye positions based on direction
                if self.direction == Direction.RIGHT:
                    left_eye = (rect.right - eye_size * 2, rect.top + eye_size * 2)
                    right_eye = (rect.right - eye_size * 2, rect.bottom - eye_size * 2)
                elif self.direction == Direction.LEFT:
                    left_eye = (rect.left + eye_size, rect.top + eye_size * 2)
                    right_eye = (rect.left + eye_size, rect.bottom - eye_size * 2)
                elif self.direction == Direction.UP:
                    left_eye = (rect.left + eye_size * 2, rect.top + eye_size)
                    right_eye = (rect.right - eye_size * 2, rect.top + eye_size)
                else:  # DOWN
                    left_eye = (rect.left + eye_size * 2, rect.bottom - eye_size)
                    right_eye = (rect.right - eye_size * 2, rect.bottom - eye_size)
                
                pygame.draw.circle(self.screen, WHITE, left_eye, eye_size)
                pygame.draw.circle(self.screen, WHITE, right_eye, eye_size)
        
        # Draw food
        food_rect = pygame.Rect(self.food[0] * self.cell_size, 
                              self.food[1] * self.cell_size,
                              self.cell_size, self.cell_size)
        pygame.draw.rect(self.screen, RED, food_rect)
        pygame.draw.rect(self.screen, BLACK, food_rect, 1)
        
        # Draw score panel
        score_panel = pygame.Rect(0, self.screen_height - 50, self.screen_width, 50)
        pygame.draw.rect(self.screen, LIGHT_GRAY, score_panel)
        pygame.draw.line(self.screen, BLACK, (0, self.screen_height - 50), 
                        (self.screen_width, self.screen_height - 50), 2)
        
        # Draw score text
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        high_score_text = self.font.render(f"High Score: {self.high_score}", True, BLACK)
        difficulty_text = self.font.render(f"Difficulty: {self.difficulty.name}", True, BLACK)
        
        self.screen.blit(score_text, (10, self.screen_height - 40))
        self.screen.blit(high_score_text, (150, self.screen_height - 40))
        self.screen.blit(difficulty_text, (350, self.screen_height - 40))
        
        # Draw controls info
        controls_text = self.font.render("P: Pause | R: Restart | Q: Quit | 1-3: Difficulty", True, BLACK)
        self.screen.blit(controls_text, (10, self.screen_height - 20))
        
        # Draw game over screen
        if self.game_over:
            overlay = pygame.Surface((self.screen_width, self.screen_height))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.big_font.render("GAME OVER", True, RED)
            score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = self.font.render("Press R to Restart or Q to Quit", True, WHITE)
            
            self.screen.blit(game_over_text, 
                           (self.screen_width // 2 - game_over_text.get_width() // 2, 
                            self.screen_height // 2 - 60))
            self.screen.blit(score_text, 
                           (self.screen_width // 2 - score_text.get_width() // 2, 
                            self.screen_height // 2))
            self.screen.blit(restart_text, 
                           (self.screen_width // 2 - restart_text.get_width() // 2, 
                            self.screen_height // 2 + 40))
        
        # Draw pause screen
        elif self.paused:
            overlay = pygame.Surface((self.screen_width, self.screen_height))
            overlay.set_alpha(120)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            pause_text = self.big_font.render("PAUSED", True, WHITE)
            continue_text = self.font.render("Press P to Continue", True, WHITE)
            
            self.screen.blit(pause_text, 
                           (self.screen_width // 2 - pause_text.get_width() // 2, 
                            self.screen_height // 2 - 30))
            self.screen.blit(continue_text, 
                           (self.screen_width // 2 - continue_text.get_width() // 2, 
                            self.screen_height // 2 + 20))
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while True:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(self.speed)

# Run the game
if __name__ == "__main__":
    game = SnakeGame()
    game.run()