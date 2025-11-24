import random
import logging
from typing import Any
from domain.bingo_card import BingoCard
from domain.number_pool import NumberPool
from game_logic.win_con import check_win_condition
from interfaces.cli_presenter import CLIPresenter

logger = logging.getLogger(__name__)


class GameSession:
    """Manages a single bingo game session"""
    
    def __init__(self, rules: dict[str, Any] | None = None):
        """
        Initialise a game session
        Args:
            rules: Optional custom rules configuration
        """
        self.rules = rules
        self.card: BingoCard | None = None
        self.number_pool: NumberPool = NumberPool(min_number=1, max_number=75)
        self.game_started = False
        self.game_over = False
        self.presenter = CLIPresenter()
        
        logger.info("Game session initialized")
    
    def start_new_game(self) -> None:
        """Start a new game by generating a card and resetting the number pool"""
        self.card = BingoCard(rules=self.rules)
        self.number_pool.reset()
        self.game_started = True
        self.game_over = False
        
        logger.info("New game started")
        self.presenter.display_message("New game started!", style="success")
        self.presenter.display_card(self.card)
    
    def reset_game(self) -> None:
        """Reset the current game with a new card"""
        if self.card:
            logger.info("Game reset requested")
        self.start_new_game()
    
    def draw_number(self) -> int | None:
        """
        Draw a random number from the pool
        Returns:
            The drawn number, or None if pool is empty
        """
        if not self.game_started:
            self.presenter.display_message("Game not started. Use 'start' command first.", style="error")
            return None
        
        if self.game_over:
            self.presenter.display_message("Game is over. Start a new game to continue.", style="info")
            return None
        
        if self.number_pool.is_empty:
            self.presenter.display_message("All numbers have been drawn!", style="info")
            return None
        
        available = list(self.number_pool.available_numbers)
        number = random.choice(available)
        self.number_pool.mark_as_called(number)
        
        logger.info(f"Number drawn: {number}")
        self.presenter.display_called_number(number)
        
        if self.card and self.card.mark_number(number):
            self.presenter.display_message(f"Number {number} marked on your card!", style="success")
            self.presenter.display_card(self.card)
        else:
            self.presenter.display_message(f"Number {number} is not on your card.", style="info")
        
        return number
    
    def mark_number(self, number: int) -> bool:
        """
        Manually mark a number on the card
        Args:
            number: The number to mark
        Returns:
            True if successfully marked, False otherwise
        """
        if not self.game_started or not self.card:
            self.presenter.display_message("Game not started.", style="error")
            return False
        
        if number not in self.number_pool.called_numbers:
            self.presenter.display_message(
                f"Number {number} has not been called yet!",
                style="error"
            )
            logger.warning(f"Attempted to mark uncalled number: {number}")
            return False
        
        success = self.card.mark_number(number)
        if success:
            self.presenter.display_message(f"Number {number} marked!", style="success")
            logger.info(f"Number marked: {number}")
        else:
            self.presenter.display_message(
                f"Number {number} is not on your card.",
                style="error"
            )
        
        return success
    
    def claim_bingo(self) -> bool:
        """
        Process a bingo claim from the player
        Returns:
            True if claim is valid, False otherwise
        """
        if not self.game_started or not self.card:
            self.presenter.display_message("Game not started.", style="error")
            return False
        
        if self.game_over:
            self.presenter.display_message("Game is already over.", style="info")
            return False
        
        logger.info("Bingo claim received")
        
        win_condition = self.rules.get('win_condition', 'single_line') if self.rules else 'single_line'
        is_valid = check_win_condition(self.card, win_condition)
        
        if is_valid:
            self.game_over = True
            self.presenter.display_message(
                f"\nBINGO! You win with '{win_condition}' pattern!\n",
                style="success"
            )
            logger.info(f"Valid bingo claim - win condition: {win_condition}")
            self.presenter.display_card(self.card, title="WINNING CARD")
            return True
        else:
            self.presenter.display_message(
                f"Invalid bingo claim. You don't have '{win_condition}' yet.",
                style="error"
            )
            logger.warning(f"Invalid bingo claim rejected - win condition not met: {win_condition}")
            return False
    
    def show_card(self) -> None:
        """Display the current card"""
        if not self.card:
            self.presenter.display_message("No active card. Start a game first.", style="error")
            return
        
        self.presenter.display_card(self.card)
    
    def show_called_numbers(self) -> None:
        """Display all called numbers"""
        called = self.number_pool.called_numbers
        
        if not called:
            self.presenter.display_message("No numbers have been called yet.", style="info")
            return
        
        self.presenter.display_message(f"\nCalled Numbers ({len(called)}):", style="info")
        
        for i in range(0, len(called), 10):
            row = called[i:i+10]
            print("  " + "  ".join(f"{n:>2}" for n in row))
        
        print()
    
    def get_game_stats(self) -> dict[str, Any]:
        """
        Get current game statistics
        Returns:
            Dictionary with game stats
        """
        return {
            'game_started': self.game_started,
            'game_over': self.game_over,
            'numbers_called': len(self.number_pool.called_numbers),
            'numbers_remaining': self.number_pool.remaining_count,
            'win_condition': self.rules.get('win_condition', 'single_line') if self.rules else 'single_line',
        }
    
    def show_stats(self) -> None:
        """Display game statistics"""
        stats = self.get_game_stats()
        
        self.presenter.display_message("\n=== Game Statistics ===", style="info")
        print(f"  Game Started: {stats['game_started']}")
        print(f"  Game Over: {stats['game_over']}")
        print(f"  Numbers Called: {stats['numbers_called']}")
        print(f"  Numbers Remaining: {stats['numbers_remaining']}")
        print(f"  Win Condition: {stats['win_condition']}")
        print()