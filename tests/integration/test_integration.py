import unittest
import sys
from pathlib import Path

src_dir = Path(__file__).parent.parent.parent / 'src'
sys.path.insert(0, str(src_dir))

from domain.bingo_card import BingoCard  # noqa: E402
from domain.number_pool import NumberPool  # noqa: E402
from game_logic.game_session import GameSession  # noqa: E402
from game_logic.win_con import check_win_condition  # noqa: E402


class TestEpic1Integration(unittest.TestCase):
    """Integration tests for Epic 1: Bingo Card Generation."""
    
    def test_card_generation_and_reset(self):
        """Test card generation with reset functionality (Epic 1.5)."""
        card = BingoCard()
        
        # Get first card data
        first_card = [row[:] for row in card.bingo_card]
        card.marked.copy()
        
        # Reset the card
        card.reset()
        second_card = [row[:] for row in card.bingo_card]
        
        # Cards should be different (extremely high probability)
        self.assertNotEqual(first_card, second_card)
        
        # Center should still be FREE
        center = len(card.bingo_card) // 2
        self.assertEqual(card.bingo_card[center][center], 'FREE')
        
        # FREE should be in marked set
        self.assertIn('FREE', card.marked)
    
    def test_card_validation_complete(self):
        """Test complete card validation (Epic 1.4, 1.6, 1.8)."""
        card = BingoCard()
        
        # Check dimensions
        self.assertEqual(len(card.bingo_card), 5)
        for row in card.bingo_card:
            self.assertEqual(len(row), 5)
        
        # Check no duplicates (excluding FREE)
        numbers = []
        for row in card.bingo_card:
            for val in row:
                if val != 'FREE':
                    numbers.append(val)
        
        self.assertEqual(len(numbers), len(set(numbers)))
        
        # Check column ranges
        for col in range(5):
            for row in range(5):
                val = card.bingo_card[row][col]
                if val != 'FREE':
                    expected_min = col * 15 + 1
                    expected_max = (col + 1) * 15
                    self.assertTrue(expected_min <= val <= expected_max,
                                  f"Value {val} in column {col} outside range {expected_min}-{expected_max}")
        
        # Check center is FREE and marked
        center = 2
        self.assertEqual(card.bingo_card[center][center], 'FREE')
        self.assertTrue(card.is_marked('FREE'))


class TestEpic2Integration(unittest.TestCase):
    """Integration tests for Epic 2: Number Calling and Validation."""
    
    def test_number_pool_and_card_marking(self):
        """Test number pool with card marking (Epic 2.1, 2.2, 2.5, 2.6)."""
        pool = NumberPool(1, 75)
        card = BingoCard()
        
        # Draw numbers and mark them on card
        drawn_numbers = []
        marked_count = 0
        
        for _ in range(20):
            # Draw a number
            available = list(pool.available_numbers)
            self.assertTrue(len(available) > 0)
            
            number = available[0]
            pool.mark_as_called(number)
            drawn_numbers.append(number)
            
            # Try to mark on card
            if card.mark_number(number):
                marked_count += 1
                self.assertTrue(card.is_marked(number))
        
        # Verify no duplicates in drawn numbers
        self.assertEqual(len(drawn_numbers), len(set(drawn_numbers)))
        
        # Verify called numbers tracked correctly
        self.assertEqual(pool.called_numbers, drawn_numbers)
        self.assertEqual(pool.remaining_count, 75 - 20)
    
    def test_auto_validation_against_drawn(self):
        """Test auto-validation of marked numbers (Epic 2.6, 2.8)."""
        session = GameSession()
        session.start_new_game()
        
        # Get a number from the card
        test_number = session.card.bingo_card[0][0]
        if test_number == 'FREE':
            test_number = session.card.bingo_card[0][1]
        
        # Try to mark without drawing - should fail
        result = session.mark_number(test_number)
        self.assertFalse(result)
        
        # Draw the number
        session.number_pool.mark_as_called(test_number)
        
        # Now marking should succeed
        result = session.mark_number(test_number)
        self.assertTrue(result)
        self.assertTrue(session.card.is_marked(test_number))
    
    def test_complete_game_flow(self):
        """Test complete game flow from start to marking (Epic 2.1-2.8)."""
        session = GameSession()
        
        # Start game
        session.start_new_game()
        self.assertTrue(session.game_started)
        self.assertIsNotNone(session.card)
        self.assertEqual(session.number_pool.remaining_count, 75)
        
        # Draw multiple numbers
        for _ in range(10):
            number = session.draw_number()
            self.assertIsNotNone(number)
            self.assertIn(number, session.number_pool.called_numbers)
        
        # Verify state
        self.assertEqual(len(session.number_pool.called_numbers), 10)
        self.assertEqual(session.number_pool.remaining_count, 65)


class TestEpic3Integration(unittest.TestCase):
    """Integration tests for Epic 3: Bingo Claim & Validation."""
    
    def test_claim_validation_single_line(self):
        """Test bingo claim with single line win condition (Epic 3.1, 3.2, 3.3, 3.4)."""
        session = GameSession(rules={'win_condition': 'single_line'})
        session.start_new_game()
        
        # Mark entire first row
        for col in range(5):
            number = session.card.bingo_card[0][col]
            if number != 'FREE':
                session.card.mark_number(number)
        
        # Claim bingo - should succeed
        result = session.claim_bingo()
        self.assertTrue(result)
        self.assertTrue(session.game_over)
    
    def test_invalid_claim_rejection(self):
        """Test rejection of invalid bingo claims (Epic 3.5, 3.6)."""
        session = GameSession(rules={'win_condition': 'single_line'})
        session.start_new_game()
        
        # Mark only 3 numbers in first row (not enough)
        for col in range(3):
            number = session.card.bingo_card[0][col]
            if number != 'FREE':
                session.card.mark_number(number)
        
        # Claim bingo - should fail
        result = session.claim_bingo()
        self.assertFalse(result)
        self.assertFalse(session.game_over)
    
    def test_multiple_win_conditions(self):
        """Test various win condition patterns (Epic 3.2, 3.8)."""
        # Test full house
        card = BingoCard()
        
        # Mark all numbers
        for row in card.bingo_card:
            for val in row:
                if val != 'FREE':
                    card.mark_number(val)
        
        self.assertTrue(check_win_condition(card, 'full_house'))
        self.assertTrue(check_win_condition(card, 'single_line'))
        self.assertTrue(check_win_condition(card, 'two_lines'))
    
    def test_four_corners_pattern(self):
        """Test four corners win pattern validation (Epic 3.2)."""
        card = BingoCard()
        
        # Mark only the four corners
        corners = [
            (0, 0), (0, 4),
            (4, 0), (4, 4)
        ]
        
        for row, col in corners:
            val = card.bingo_card[row][col]
            if val != 'FREE':
                card.mark_number(val)
        
        self.assertTrue(check_win_condition(card, 'four_corners'))
        self.assertFalse(check_win_condition(card, 'single_line'))
    
    def test_x_pattern(self):
        """Test X pattern (both diagonals) win condition (Epic 3.2)."""
        card = BingoCard()
        
        # Mark both diagonals
        for i in range(5):
            # Main diagonal
            val = card.bingo_card[i][i]
            if val != 'FREE':
                card.mark_number(val)
            
            # Anti-diagonal
            val = card.bingo_card[i][4-i]
            if val != 'FREE':
                card.mark_number(val)
        
        self.assertTrue(check_win_condition(card, 'x_pattern'))
    
    def test_complete_game_with_win(self):
        """Test complete game flow from start to win (Epic 3 complete)."""
        session = GameSession(rules={'win_condition': 'single_line'})
        session.start_new_game()
        
        # Simulate drawing all numbers in first row
        for col in range(5):
            number = session.card.bingo_card[0][col]
            if number != 'FREE':
                # Add to number pool as called
                session.number_pool.mark_as_called(number)
                # Mark on card
                session.card.mark_number(number)
        
        # Verify the row is complete
        self.assertTrue(check_win_condition(session.card, 'single_line'))
        
        # Claim bingo
        result = session.claim_bingo()
        self.assertTrue(result)
        self.assertTrue(session.game_over)
        
        # Try to draw after game over - should not work
        result = session.draw_number()
        self.assertIsNone(result)


class TestCrossEpicIntegration(unittest.TestCase):
    """Integration tests spanning multiple epics."""
    
    def test_full_game_simulation(self):
        """Simulate a complete game from start to finish."""
        session = GameSession(rules={'win_condition': 'single_line'})
        
        # Epic 1: Start with card generation
        session.start_new_game()
        self.assertIsNotNone(session.card)
        
        # Epic 2: Draw and mark numbers until we complete a line
        max_draws = 75
        draws = 0
        
        while not session.game_over and draws < max_draws:
            number = session.draw_number()
            if number is None:
                break
            draws += 1
            
            # Epic 3: Check if we can claim bingo
            if check_win_condition(session.card, 'single_line'):
                result = session.claim_bingo()
                self.assertTrue(result)
                break
        
        # Verify we either won or exhausted numbers
        self.assertTrue(session.game_over or draws == max_draws)


if __name__ == '__main__':
    unittest.main()