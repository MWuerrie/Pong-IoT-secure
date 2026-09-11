import pygame
import random


class Ball:
    """
    Represents the ball in a Pong-like game.
    Handles movement, collisions with screen boundaries, and attachment to paddles.
    """

    def __init__(self, x, y, size, color, speed):
        """
        Initializes the ball with position, size, appearance, and speed attributes.
        """
        # Initial floating-point coordinates for smooth movement calculation
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.speed = speed

        # Current directional velocities (pixels per second/frame depending on dt)
        self.velocity_x = 0
        self.velocity_y = 0

        # Tracks which paddle the ball is currently stuck to.
        # None = ball is moving freely
        # Paddle object reference = ball sticks to that specific paddle
        self.attached_to_paddle = None

        # Pygame Rect object used for collision detection and drawing
        self.rect = pygame.Rect(
            self.x,
            self.y,
            self.size,
            self.size
        )

    def attach_to_paddle(self, paddle):
        """
        Binds the ball to a specific paddle and stops its movement.
        """
        self.attached_to_paddle = paddle
        self.velocity_x = 0
        self.velocity_y = 0

        # Immediately position the ball correctly relative to the paddle
        self.update_position_on_paddle()

    def update_position_on_paddle(self):
        """
        Calculates and updates the ball's position so it moves along with the attached paddle.
        """
        # If the ball is free, do nothing
        if self.attached_to_paddle is None:
            return

        paddle = self.attached_to_paddle

        # Default horizontal alignment to the center of the paddle (fallback)
        self.x = paddle.rect.centerx - self.size / 2

        # Determine which side of the screen the paddle is on based on an arbitrary center line (500)
        if paddle.rect.centerx > 500:
            # Right paddle: Place the ball just to the left side of the paddle
            self.x = paddle.rect.left - self.size
        else:
            # Left paddle: Place the ball just to the right side of the paddle
            self.x = paddle.rect.right

        # Vertically center the ball relative to the paddle's height
        self.y = paddle.rect.centery - self.size / 2

        # Sync the changes to the Pygame Rect
        self.update_rect()

    def launch(self):
        """
        Launches the ball away from the attached paddle into active gameplay.
        """
        # Only launch if the ball is actually attached to a paddle
        if self.attached_to_paddle is None:
            return

        paddle = self.attached_to_paddle

        # Determine direction based on the spatial relationship between paddle and ball
        if paddle.rect.centerx < self.rect.centerx:
            direction = 1  # Launch right if ball is to the right of the paddle center
        else:
            direction = -1 # Launch left if ball is to the left of the paddle center

        # Set velocities: X moves away from the paddle, Y gets a random diagonal angle
        self.velocity_x = -direction * self.speed
        self.velocity_y = random.choice([-1, 1]) * self.speed * 0.7

        # Detach the ball from the paddle
        self.attached_to_paddle = None

    def reset(self, screen_width, screen_height):
        """
        Resets the ball to the center of the screen with a random initial launch direction.
        """
        # Center the ball horizontally and vertically on the screen
        self.x = screen_width / 2 - self.size / 2
        self.y = screen_height / 2 - self.size / 2

        # Choose a random horizontal and vertical direction for the new serve
        self.velocity_x = random.choice([-1, 1]) * self.speed
        self.velocity_y = random.choice([-1, 1]) * self.speed * 0.7

        # Ensure the ball is not attached to any paddle upon reset
        self.attached_to_paddle = None

        # Sync coordinate changes to the Rect object
        self.update_rect()

    def update(self, dt, screen_width, screen_height):
        """
        Updates the ball's position based on elapsed time (dt) and handles wall bounces.
        """
        # If attached, just follow the paddle's movement and skip independent movement logic
        if self.attached_to_paddle is not None:
            self.update_position_on_paddle()
            return

        # Move the ball using delta time (dt) for framerate-independent speed
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt

        # Boundary collision: Top wall bounce
        if self.y <= 0:
            self.y = 0
            self.velocity_y *= -1  # Reverse vertical direction

        # Boundary collision: Bottom wall bounce
        if self.y + self.size >= screen_height:
            self.y = screen_height - self.size
            self.velocity_y *= -1  # Reverse vertical direction

        # Always update the Rect layout after changing positions
        self.update_rect()

    def update_rect(self):
        """
        Synchronizes the continuous float coordinates (x, y) with the discrete integer Pygame Rect (x, y).
        """
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def draw(self, screen):
        """
        Renders the ball as a solid rectangle on the provided surface/screen.
        """
        pygame.draw.rect(
            screen,
            self.color,
            self.rect
        )