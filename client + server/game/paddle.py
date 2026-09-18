import pygame


class Paddle:
    """Represents a Pong paddle."""

    def __init__(self, x, y, color, width, height, speed):
        self.x = x
        self.y = y
        self.color = color
        self.width = width
        self.height = height
        self.speed = speed

        self.rect = pygame.Rect(
            self.x,
            self.y,
            self.width,
            self.height
        )

    def move_up(self, dt):
        self.y -= self.speed * dt

        if self.y < 0:
            self.y = 0

        self.update_rect()

    def move_down(self, screen_height, dt):
        self.y += self.speed * dt

        if self.y + self.height > screen_height:
            self.y = screen_height - self.height

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