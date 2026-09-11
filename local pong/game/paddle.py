import pygame


class Paddle:
  
    """Represents a paddle. Set the size and color, handles the mnovement"""

    def __init__(self, x, y, color, width, height, speed):
        self.x = x
        self.y = y
        self.color = color
        self.width = width
        self.height = height
        self.speed = speed

        # giving the paddle a rectangel structure
        self.rect = pygame.Rect(   
            self.x,
            self.y,
            self.width,  
            self.height
        )

    # move up

    """
    dt is the time since the last movement 
    (look up in game.py :   dt = self.clock.tick(self.FPS) / 1000)
    example: 60 FPS. How did the position of the paddle changed after 16 milliseconds?  
    dt= 0.016
    y_old = 250.0 (last position before movement)
     speed = 300  (PADDLE_SPEED in game.py)
    y_new= 250.0 + 300*0.016 = 254.8 
    
    """
    
    def move_up(self, dt):
        self.y -= self.speed * dt

        if self.y < 0:
            self.y = 0

        self.update_rect()

    # move down
    def move_down(self, screen_height, dt):
        self.y += self.speed * dt

        if self.y + self.height > screen_height:
            self.y = screen_height - self.height

        self.update_rect()


    # update to new position
    def update_rect(self):
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    # drawing the paddle
    def draw(self, screen):
        pygame.draw.rect(
            screen,
            self.color,
            self.rect
        )