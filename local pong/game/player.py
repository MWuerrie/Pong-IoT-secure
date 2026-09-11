import pygame


class Player:
    """Represents a player in the game, managing their paddle, controls, and score."""

    def __init__(self, name, paddle, up_key, down_key):
        """
        Initializes a new player instance.

        Args:
            name (str): The name of the player.
            paddle (Paddle): The paddle object controlled by this player.
            up_key (int): The Pygame key constant used to move up.
            down_key (int): The Pygame key constant used to move down.
        """
        self.name = name
        self.paddle = paddle
        self.up_key = up_key
        self.down_key = down_key
        self.score = 0  # Starts with a score of 0

    def handle_input(self, dt, screen_height):
        """
        Checks for player keyboard input and moves the paddle accordingly.

        Args:
            dt (float): Delta time since the last frame for smooth movement.
            screen_height (int): The height of the screen to prevent moving out of bounds.
        """
        # Get the state of all keyboard buttons
        keys = pygame.key.get_pressed()

        # Move the paddle up if the designated up key is pressed
        if keys[self.up_key]:
            self.paddle.move_up(dt)

        # Move the paddle down if the designated down key is pressed
        if keys[self.down_key]:
            self.paddle.move_down(screen_height, dt)

    def add_point(self):
        """Increments the player's score by 1 when they win a round."""
        self.score += 1