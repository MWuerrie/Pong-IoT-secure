from game.ball import Ball
from game.paddle import Paddle
from game.player import Player


class Game:
    """Controls the authoritative game state."""

    def __init__(self, screen_width=1000, screen_height=600):

        self.screen_width = screen_width
        self.screen_height = screen_height

        paddle_width = 20
        paddle_height = 100
        paddle_speed = 300

        ball_size = 20
        ball_speed = 400

        # Player 1 - red
        paddle1 = Paddle(
            50,
            screen_height / 2 - paddle_height / 2,
            "red",
            paddle_width,
            paddle_height,
            paddle_speed
        )

        # Player 2 - green
        paddle2 = Paddle(
            screen_width - 50 - paddle_width,
            screen_height / 2 - paddle_height / 2,
            "green",
            paddle_width,
            paddle_height,
            paddle_speed
        )

        self.player1 = Player("Player 1", paddle1)
        self.player2 = Player("Player 2", paddle2)

        self.ball = Ball(
            screen_width / 2 - ball_size / 2,
            screen_height / 2 - ball_size / 2,
            ball_size,
            "white",
            ball_speed
        )

        self.last_point = None

        self.ball.reset(
            self.screen_width,
            self.screen_height
        )

    def update(self, dt):

        self.ball.update(
            dt,
            self.screen_width,
            self.screen_height
        )

        # Collision with Player 1
        if self.ball.rect.colliderect(
            self.player1.paddle.rect
        ):

            if self.ball.velocity_x < 0:

                self.ball.x = self.player1.paddle.rect.right

                self.ball.velocity_x *= -1

                self.ball.update_rect()

        # Collision with Player 2
        if self.ball.rect.colliderect(
            self.player2.paddle.rect
        ):

            if self.ball.velocity_x > 0:

                self.ball.x = (
                    self.player2.paddle.rect.left
                    - self.ball.size
                )

                self.ball.velocity_x *= -1

                self.ball.update_rect()

        # Player 2 scores
        if self.ball.x + self.ball.size < 0:

            self.player2.add_point()

            self.last_point = 2


        # Player 1 scores
        if self.ball.x > self.screen_width:

            self.player1.add_point()

            self.last_point = 1
