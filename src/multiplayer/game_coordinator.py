import random
import logging
from domain.bingo_card import BingoCard
from domain.number_pool import NumberPool
from game_logic.win_con import get_best_win
from multiplayer.lobby import Lobby
from multiplayer.player import Player

logger = logging.getLogger(__name__)


class GameCoordinator:
    """Coordinates a multiplayer bingo game."""
    
    def __init__(self, lobby: Lobby, rules: dict | None = None):
        """
        Initialise game coordinator.
        Args:
            lobby: The lobby to coordinate
            rules: Optional game rules
        """
        self.lobby = lobby
        self.rules = rules or {}
        self.number_pool = NumberPool(1, 75)
        self.game_active = False
        self.winner: Player = None
        self.win_type: str = None
    
    def start_game(self) -> bool:
        """
        Start the multiplayer game.
        Returns:
            True if game started successfully
        """
        if not self.lobby.start_game():
            return False
        
        for player in self.lobby.players.values():
            card = BingoCard(rules=self.rules)
            player.assign_card(card)
        
        self.number_pool.reset()
        self.game_active = True
        self.winner = None
        self.win_type = None
        
        logger.info(f"Multiplayer game started in lobby {self.lobby.lobby_id}")
        return True
    
    def draw_number(self) -> int | None:
        """
        Draw a number from the pool.
        Returns:
            The drawn number, or None if pool is empty
        """
        if not self.game_active:
            return None
        
        if self.number_pool.is_empty:
            logger.info("Number pool exhausted")
            return None
        
        available = list(self.number_pool.available_numbers)
        number = random.choice(available)
        self.number_pool.mark_as_called(number)
        
        for player in self.lobby.players.values():
            if player.card:
                player.mark_number(number)
        
        logger.info(f"Number drawn: {number}")
        return number
    
    def validate_bingo_claim(self, player_id: str) -> tuple[bool, str | None, int]:
        """
        Validate a bingo claim from a player.
        Args:
            player_id: ID of player making the claim
        Returns:
            Tuple of (is_valid, win_type, points_earned)
        """
        if not self.game_active:
            return False, None, 0

        if self.winner:
            return False, None, 0

        player = self.lobby.get_player(player_id)
        if not player or not player.card:
            return False, None, 0

        if player.has_claimed_bingo:
            return False, None, 0

        player.has_claimed_bingo = True

        # Check for the best win condition (highest points)
        best_win_result = get_best_win(player.card)

        if best_win_result:
            win_type, points = best_win_result
            self.winner = player
            self.win_type = win_type
            player.is_winner = True

            player.add_points(points)

            self.game_active = False

            logger.info(f"Valid bingo claim from {player.username} ({win_type}, {points} points)")
            return True, win_type, points
        else:
            logger.info(f"Invalid bingo claim from {player.username}")
            return False, None, 0
    
    def reset_for_new_round(self, keep_points: bool = True) -> None:
        """
        Reset for a new round.
        Args:
            keep_points: Whether to keep player points
        """
        self.lobby.reset_for_new_round(keep_points=keep_points)
        self.number_pool.reset()
        self.game_active = False
        self.winner = None
        self.win_type = None
        
        logger.info("Game coordinator reset for new round")
    
    def get_game_state(self) -> dict:
        """
        Get current game state.
        Returns:
            Dictionary with game state
        """
        return {
            'lobby_id': self.lobby.lobby_id,
            'game_active': self.game_active,
            'players': self.lobby.get_player_list(),
            'numbers_called': len(self.number_pool.called_numbers),
            'numbers_remaining': self.number_pool.remaining_count,
            'winner': self.winner.to_dict() if self.winner else None,
            'win_type': self.win_type
        }