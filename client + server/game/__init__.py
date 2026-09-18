def update(self, dt):
    """Updates the authoritative game state."""

    # Update ball movement and wall collisions
    self.ball.update(
        dt,
        self.screen_width,
        self.screen_height
    )