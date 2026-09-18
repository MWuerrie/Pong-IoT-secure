class Player:
    """Represents a player in the networked Pong game."""

    def __init__(self, name, paddle):
        self.name = name
        self.paddle = paddle
        self.score = 0

    def add_point(self):
        self.score += 1