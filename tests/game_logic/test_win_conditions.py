import unittest
import sys
from pathlib import Path

src_dir = Path(__file__).parent.parent.parent / 'src'
sys.path.insert(0, str(src_dir))

from domain.bingo_card import BingoCard  # noqa: E402
from game_logic.win_con import (  # noqa: E402
    check_single_line, check_two_lines, check_full_house,
    check_four_corners, check_x_pattern, check_t_pattern,
    check_l_pattern, check_win_condition
)


class TestWinConditions(unittest.TestCase):
    """Test all win condition validators."""
    
    def setUp(self):
        """Create a fresh card for each test."""
        self.card = BingoCard()
    
    def test_single_line_row(self):
        """Test single line detection - horizontal row."""
        # Mark entire first row
        for col in range(5):
            val = self.card.bingo_card[0][col]
            if val != 'FREE':
                self.card.mark_number(val)
        
        self.assertTrue(check_single_line(self.card))
    
    def test_single_line_column(self):
        """Test single line detection - vertical column."""
        # Mark entire first column
        for row in range(5):
            val = self.card.bingo_card[row][0]
            if val != 'FREE':
                self.card.mark_number(val)
        
        self.assertTrue(check_single_line(self.card))
    
    def test_single_line_diagonal(self):
        """Test single line detection - diagonal."""
        # Mark main diagonal
        for i in range(5):
            val = self.card.bingo_card[i][i]
            if val != 'FREE':
                self.card.mark_number(val)
        
        self.assertTrue(check_single_line(self.card))
    
    def test_single_line_no_complete(self):
        """Test single line detection with incomplete lines."""
        # Mark only 3 numbers in first row
        for col in range(3):
            val = self.card.bingo_card[0][col]
            if val != 'FREE':
                self.card.mark_number(val)
        
        self.assertFalse(check_single_line(self.card))
    
    def test_two_lines(self):
        """Test two lines detection."""
        # Mark first row
        for col in range(5):
            val = self.card.bingo_card[0][col]
            if val != 'FREE':
                self.card.mark_number(val)
        
        # Mark second row
        for col in range(5):
            val = self.card.bingo_card[1][col]
            if val != 'FREE':
                self.card.mark_number(val)
        
        self.assertTrue(check_two_lines(self.card))
    
    def test_two_lines_false_with_one_line(self):
        """Test two lines fails with only one line."""
        # Mark only first row
        for col in range(5):
            val = self.card.bingo_card[0][col]
            if val != 'FREE':
                self.card.mark_number(val)
        
        self.assertFalse(check_two_lines(self.card))
    
    def test_full_house(self):
        """Test full house (all marked)."""
        # Mark all numbers
        for row in range(5):
            for col in range(5):
                val = self.card.bingo_card[row][col]
                if val != 'FREE':
                    self.card.mark_number(val)
        
        self.assertTrue(check_full_house(self.card))
    
    def test_full_house_incomplete(self):
        """Test full house fails when incomplete."""
        # Mark all except one
        count = 0
        for row in range(5):
            for col in range(5):
                val = self.card.bingo_card[row][col]
                if val != 'FREE' and count < 23:  # Leave one unmarked
                    self.card.mark_number(val)
                    count += 1
        
        self.assertFalse(check_full_house(self.card))
    
    def test_four_corners(self):
        """Test four corners pattern."""
        corners = [(0, 0), (0, 4), (4, 0), (4, 4)]
        
        for row, col in corners:
            val = self.card.bingo_card[row][col]
            if val != 'FREE':
                self.card.mark_number(val)
        
        self.assertTrue(check_four_corners(self.card))
    
    def test_four_corners_incomplete(self):
        """Test four corners fails when incomplete."""
        # Mark only 3 corners
        corners = [(0, 0), (0, 4), (4, 0)]
        
        for row, col in corners:
            val = self.card.bingo_card[row][col]
            if val != 'FREE':
                self.card.mark_number(val)
        
        self.assertFalse(check_four_corners(self.card))
    
    def test_x_pattern(self):
        """Test X pattern (both diagonals)."""
        # Mark both diagonals
        for i in range(5):
            val = self.card.bingo_card[i][i]
            if val != 'FREE':
                self.card.mark_number(val)
            
            val = self.card.bingo_card[i][4-i]
            if val != 'FREE':
                self.card.mark_number(val)
        
        self.assertTrue(check_x_pattern(self.card))
    
    def test_x_pattern_incomplete(self):
        """Test X pattern fails with only one diagonal."""
        # Mark only main diagonal
        for i in range(5):
            val = self.card.bingo_card[i][i]
            if val != 'FREE':
                self.card.mark_number(val)
        
        self.assertFalse(check_x_pattern(self.card))
    
    def test_t_pattern(self):
        """Test T pattern (top row + middle column)."""
        # Mark top row
        for col in range(5):
            val = self.card.bingo_card[0][col]
            if val != 'FREE':
                self.card.mark_number(val)
        
        # Mark middle column
        for row in range(5):
            val = self.card.bingo_card[row][2]
            if val != 'FREE':
                self.card.mark_number(val)
        
        self.assertTrue(check_t_pattern(self.card))
    
    def test_l_pattern(self):
        """Test L pattern (top row + left column)."""
        # Mark top row
        for col in range(5):
            val = self.card.bingo_card[0][col]
            if val != 'FREE':
                self.card.mark_number(val)
        
        # Mark left column
        for row in range(5):
            val = self.card.bingo_card[row][0]
            if val != 'FREE':
                self.card.mark_number(val)
        
        self.assertTrue(check_l_pattern(self.card))
    
    def test_check_win_condition_dispatcher(self):
        """Test the main check_win_condition dispatcher function."""
        # Mark a complete row
        for col in range(5):
            val = self.card.bingo_card[0][col]
            if val != 'FREE':
                self.card.mark_number(val)
        
        # Should pass single_line
        self.assertTrue(check_win_condition(self.card, 'single_line'))
        
        # Should fail two_lines
        self.assertFalse(check_win_condition(self.card, 'two_lines'))
    
    def test_invalid_win_condition_raises(self):
        """Test that invalid win condition raises ValueError."""
        with self.assertRaises(ValueError):
            check_win_condition(self.card, 'invalid_mode')


if __name__ == '__main__':
    unittest.main()