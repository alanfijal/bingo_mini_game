import random
class BingoCard:
    def __init__(self):
        self.bingo_card = [[None for _ in range(5)] for _ in range(5)]
        self.generate_card()

    def bingo_card(self):
        # backward compatibility for tests/other code expecting .card
        return self.bingo_card

    def generate_card(self):
        ranges = [(1,15), (16,30), (31,45), (46,60), (61,75)]
            
        for col in range(5):
            start, end = ranges[col]
            numbers = random.sample(range(start, end + 1), 5)
            for row in range(5):
                self.bingo_card[row][col] = numbers[row]
        
        # if rules.get('free_space', True):
        self.bingo_card[2][2] = 'FREE'

    

    