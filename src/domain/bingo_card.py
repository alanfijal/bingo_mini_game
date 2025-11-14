import random
from domain.rules import get_rules

class BingoCard:
    def __init__(self, rules=None):
        self.rules = get_rules(rules)
        card_size = self.rules.get('card_size', 5)
        self.bingo_card = [[None for _ in range(card_size)] for _ in range(card_size)]
        self.marked = set()  # Track marked numbers
        self.generate_card()

    def bingo_card(self):
        # backward compatibility for tests/other code expecting .card
        return self.bingo_card

    def generate_card(self):
        ranges = self.rules.get('number_ranges', [(1,15), (16,30), (31,45), (46,60), (61,75)])
        card_size = self.rules.get('card_size', 5)
            
        for col in range(card_size):
            start, end = ranges[col]
            numbers = random.sample(range(start, end + 1), card_size)
            for row in range(card_size):
                self.bingo_card[row][col] = numbers[row]
        
        if self.rules.get('free_space', True):
            center = card_size // 2
            self.bingo_card[center][center] = 'FREE'
            # Free space is always considered marked
            self.marked.add('FREE')

    def mark_number(self, number):
        """
        Mark a number on the card if it exists.
        
        Args:
            number: The number to mark
            
        Returns:
            bool: True if the number was found and marked, False otherwise
        """
        for row in range(len(self.bingo_card)):
            for col in range(len(self.bingo_card[row])):
                if self.bingo_card[row][col] == number:
                    self.marked.add(number)
                    return True
        return False
    
    def is_marked(self, number):
        """
        Check if a number is marked.
        
        Args:
            number: The number to check
            
        Returns:
            bool: True if the number is marked, False otherwise
        """
        return number in self.marked
