from domain.bingo_card import BingoCard
import random

class Draw_Mark(BingoCard):
    def __init__(self, card:BingoCard | None = None):
        if card is not None:
            self.bingo_card = [row[:] for row in card.bingo_card]
        else:
            raise ValueError("A BingoCard instance must be provided.")
        
        self.drawn = set()
        
    def draw_number(self):
        all = set(range(1,76))
        remaining = list(all - self.drawn)
        if not remaining:
            raise ValueError("All numbers have been drawn.")
        n = random.choice(remaining)
        self.drawn.add(n)
        return n
    
    def find_cell(self, number):
        for r in range(5):
            for c in range(5):
                if self.bingo_card[r][c] == number:
                    self.bingo_card[r][c] = 'X'
                    return (r, c)
        return None
    
    def is_marked(self, row: int, col: int) -> bool:
        if not (0 <= row < 5 and 0 <= col < 5):
            raise IndexError("row and col must be in range 0..4")
        return self.bingo_card[row][col] == 'X'
    
    def mark_cell(self, number):
        cell = self.find_cell(number)
        if cell is None:
            return False
        
        r, c = cell
        if self.is_marked(r, c):
            return False
        if number not in self.drawn:
            raise ValueError(f"Number {number} has not been drawn yet.")
        self.bingo_card[r][c] = 'X'
        return True