import pygame

from .paddle import Paddle
from .player import Player
from .ball import Ball


class Game:
    """Manages the main game loop, state, entities, and rendering for the Pong game."""

    # Game screen configuration
    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 600
    FPS = 60

    # Color definitions (RGB)
    BACKGROUND_COLOR = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)

    # Paddle settings
    PADDLE_WIDTH = 20
    PADDLE_HEIGHT = 50
    PADDLE_SPEED = 500

    # Ball settings
    BALL_SIZE = 20
    BALL_SPEED = 900

    def __init__(self):
        """Initializes Pygame, creates the window, and sets up all game objects."""
        pygame.init()

        # Setup the display screen and window title
        self.screen = pygame.display.set_mode(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        )
        pygame.display.set_caption("Pong")

        # Game loop timing and state control
        self.clock = pygame.time.Clock()
        self.running = True

        # Font configuration for the score display
        self.font = pygame.font.Font(None, 80)

        # -----------------------------
        # Paddles Setup
        # -----------------------------
        # Position left paddle at the vertical center of the screen
        left_paddle = Paddle(
            50,
            self.SCREEN_HEIGHT / 2 - self.PADDLE_HEIGHT / 2,
            self.RED,
            self.PADDLE_WIDTH,
            self.PADDLE_HEIGHT,
            self.PADDLE_SPEED
        )

        # Position right paddle opposite to the left one
        right_paddle = Paddle(
            self.SCREEN_WIDTH - 50 - self.PADDLE_WIDTH,
            self.SCREEN_HEIGHT / 2 - self.PADDLE_HEIGHT / 2,
            self.GREEN,
            self.PADDLE_WIDTH,
            self.PADDLE_HEIGHT,
            self.PADDLE_SPEED
        )

        # -----------------------------
        # Players Setup
        # -----------------------------
        # Player 1 controls the left paddle using W/S keys
        self.player1 = Player(
            "Player 1",
            left_paddle,
            pygame.K_w,
            pygame.K_s
        )

        # Player 2 controls the right paddle using Arrow Up/Down keys
        self.player2 = Player(
            "Player 2",
            right_paddle,
            pygame.K_UP,
            pygame.K_DOWN
        )

        # -----------------------------
        # Ball Setup
        # -----------------------------
        # Create and reset the ball position to start the game
        self.ball = Ball(
            self.SCREEN_WIDTH / 2,
            self.SCREEN_HEIGHT / 2,
            self.BALL_SIZE,
            self.WHITE,
            self.BALL_SPEED
        )

        self.ball.reset(
            self.SCREEN_WIDTH,
            self.SCREEN_HEIGHT
        )

    def handle_events(self):
        """Processes Pygame events like closing the window or pressing action keys."""
        for event in pygame.event.get():
            # Stop the game if window close button is clicked
            if event.type == pygame.QUIT:
                self.running = False

            # Check for key down events
            if event.type == pygame.KEYDOWN:
                # Quit the game instantly on ESCAPE
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                # Launch the ball on SPACEBAR (e.g., after serving or resetting)
                if event.key == pygame.K_SPACE:
                    self.ball.launch()

    def update(self, dt):
        """Updates the logic, positions, and collisions of all game elements."""
        # Process player movement inputs
        self.player1.handle_input(dt, self.SCREEN_HEIGHT)
        self.player2.handle_input(dt, self.SCREEN_HEIGHT)

        # Update ball position and check for wall bounces
        self.ball.update(dt, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

        # Run collision checks and score updates
        self.check_paddle_collision()
        self.check_score()

    def check_paddle_collision(self):
        """Handles collision detection and resolution between the ball and paddles."""
        # Ignore collisions if the ball is still waiting to be launched
        if self.ball.attached_to_paddle is not None:
            return

        # Check collision with Player 1's paddle (Left side)
        if self.ball.rect.colliderect(self.player1.paddle.rect):
            # Align ball edge to paddle edge and reverse X velocity to go right
            self.ball.x = self.player1.paddle.rect.right
            self.ball.velocity_x = abs(self.ball.velocity_x)

        # Check collision with Player 2's paddle (Right side)
        if self.ball.rect.colliderect(self.player2.paddle.rect):
            # Align ball edge to paddle edge and reverse X velocity to go left
            self.ball.x = self.player2.paddle.rect.left - self.ball.size
            self.ball.velocity_x = -abs(self.ball.velocity_x)

    def check_score(self):
        """Monsters out-of-bounds balls, awards points, and resets the round."""
        # Player 2 scores (Ball flew past Player 1 on the left side)
        if self.ball.x < -self.ball.size:
            self.player2.add_point()
            # Attach the ball to Player 1's paddle for the next serve
            self.ball.attach_to_paddle(self.player1.paddle)

        # Player 1 scores (Ball flew past Player 2 on the right side)
        elif self.ball.x > self.SCREEN_WIDTH:
            self.player1.add_point()
            # Attach the ball to Player 2's paddle for the next serve
            self.ball.attach_to_paddle(self.player2.paddle)

    def draw(self):
        """Clears the screen and draws all visual components of the game."""
        # Clear screen with black background
        self.screen.fill(self.BACKGROUND_COLOR)

        # Draw a vertical dashed line dividing the field in half
        pygame.draw.line(
            self.screen,
            self.WHITE,
            (self.SCREEN_WIDTH // 2, 0),
            (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT),
            2
        )

        # Render paddles and ball onto the screen
        self.player1.paddle.draw(self.screen)
        self.player2.paddle.draw(self.screen)
        self.ball.draw(self.screen)

        # Render score text
        score_text = self.font.render(
            f"{self.player1.score}     {self.player2.score}",
            True,
            self.WHITE
        )

        # Center the score display at the top of the window
        score_rect = score_text.get_rect(
            center=(self.SCREEN_WIDTH // 2, 50)
        )
        self.screen.blit(score_text, score_rect)

        # Refresh the display to show the newly drawn frame
        pygame.display.flip()

    def run(self):
        """Starts and runs the continuous main game loop."""
        while self.running:
            # Measure time elapsed since last frame (in seconds)
            dt = self.clock.tick(self.FPS) / 1000

            # Execute the core loop steps
            self.handle_events()
            self.update(dt)
            self.draw()

        # Clean exit when loop terminates
        pygame.quit()