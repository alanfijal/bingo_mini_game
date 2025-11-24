import uuid
from datetime import datetime
from domain.bingo_card import BingoCard


class Player:
    """Represents a player in a multiplayer bingo game"""
    
    def __init__(self, username: str, player_id: str | None = None):
        """
        Initialise a player.
        Args:
            username: Player's chosen username
            player_id: Optional unique player ID (generated if not provided)
        """
        self.player_id = player_id or str(uuid.uuid4())
        self.username = username
        self.card: BingoCard | None = None
        self.points = 0
        self.session_created = datetime.now()
        self.is_connected = True
        self.has_claimed_bingo = False
        self.is_winner = False
    
    def assign_card(self, card: BingoCard) -> None:
        """Assign a bingo card to the player"""
        self.card = card
    
    def add_points(self, points: int) -> None:
        """Add points to the player's score"""
        self.points += points
    
    def mark_number(self, number: int) -> bool:
        """
        Mark a number on the player's card
        Args:
            number: The number to mark
        Returns:
            True if successfully marked, False otherwise
        """
        if self.card:
            return self.card.mark_number(number)
        return False
    
    def reset_for_new_round(self, keep_points: bool = True) -> None:
        """
        Reset player state for a new round
        Args:
            keep_points: Whether to keep points from previous rounds
        """
        self.card = None
        self.has_claimed_bingo = False
        self.is_winner = False
        if not keep_points:
            self.points = 0
    
    def to_dict(self) -> dict:
        """Convert player to dictionary for serialization."""
        return {
            'player_id': self.player_id,
            'username': self.username,
            'points': self.points,
            'is_connected': self.is_connected,
            'has_claimed_bingo': self.has_claimed_bingo,
            'is_winner': self.is_winner
        }
    
    def __repr__(self) -> str:
        return f"Player(id={self.player_id[:8]}, username='{self.username}', points={self.points})"