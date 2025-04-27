import random

class SnakeAndLadderGame:
    def __init__(self):
        self.snakes = {16: 6, 48: 30, 62: 19, 64: 60, 93: 68, 95: 24, 98: 78}
        self.ladders = {1: 38, 4: 14, 9: 31, 21: 42, 28: 84, 51: 67, 72: 91, 80: 99}
        self.players = {}
        self.player_names = []

    def roll_dice(self):
        return random.randint(1, 6)

    def move_player(self, player_name, steps):
        pos = self.players[player_name]
        pos += steps
        if pos > 100:
            pos -= steps  # Cannot move
        if pos in self.snakes:
            pos = self.snakes[pos]
        elif pos in self.ladders:
            pos = self.ladders[pos]
        self.players[player_name] = pos
        return pos

