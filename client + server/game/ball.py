import pygame
import random


class Ball:
    """Represents the ball in the Pong game."""

    def __init__(self, x, y, size, color, speed):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.speed = speed

        self.velocity_x = 0
        self.velocity_y = 0

        self.attached_to_paddle = None

        self.rect = pygame.Rect(
            self.x,
            self.y,
            self.size,
            self.size
        )

    def attach_to_paddle(self, paddle):
        self.attached_to_paddle = paddle
        self.velocity_x = 0
        self.velocity_y = 0
        self.update_position_on_paddle()

    def update_position_on_paddle(self):
        if self.attached_to_paddle is None:
            return

        paddle = self.attached_to_paddle

        if paddle.rect.centerx < 500:
            self.x = paddle.rect.right
        else:
            self.x = paddle.rect.left - self.size

        self.y = paddle.rect.centery - self.size / 2

        self.update_rect()

    def launch(self):
        if self.attached_to_paddle is None:
            return

        paddle = self.attached_to_paddle

        if paddle.rect.centerx < self.rect.centerx:
            direction = 1
        else:
            direction = -1

        self.velocity_x = direction * self.speed
        self.velocity_y = random.choice([-1, 1]) * self.speed * 0.7

        self.attached_to_paddle = None

    def reset(self, screen_width, screen_height):
        self.x = screen_width / 2 - self.size / 2
        self.y = screen_height / 2 - self.size / 2

        self.velocity_x = random.choice([-1, 1]) * self.speed
        self.velocity_y = random.choice([-1, 1]) * self.speed * 0.7

        self.attached_to_paddle = None

        self.update_rect()

    def update(self, dt, screen_width, screen_height):
        if self.attached_to_paddle is not None:
            self.update_position_on_paddle()
            return

        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt

        if self.y <= 0:
            self.y = 0
            self.velocity_y *= -1

        if self.y + self.size >= screen_height:
            self.y = screen_height - self.size
            self.velocity_y *= -1

        self.update_rect()

    def update_rect(self):
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def draw(self, screen):
        pygame.draw.rect(
            screen,
            self.color,
            self.rect
        )