from enum import Enum
from typing import Any
import json


class MessageType(Enum):
    """Types of messages exchanged between client and server."""
    
    # Client -> Server
    JOIN_LOBBY = "join_lobby"
    LEAVE_LOBBY = "leave_lobby"
    START_GAME = "start_game"
    CLAIM_BINGO = "claim_bingo"
    REQUEST_DRAW = "request_draw"
    MARK_NUMBER = "mark_number"
    
    # Server -> Client
    LOBBY_JOINED = "lobby_joined"
    LOBBY_LEFT = "lobby_left"
    PLAYER_JOINED = "player_joined"
    PLAYER_LEFT = "player_left"
    GAME_STARTED = "game_started"
    NUMBER_DRAWN = "number_drawn"
    NUMBER_MARKED = "number_marked"
    BINGO_CLAIMED = "bingo_claimed"
    BINGO_VALID = "bingo_valid"
    BINGO_INVALID = "bingo_invalid"
    WINNER_ANNOUNCED = "winner_announced"
    GAME_LOCKED = "game_locked"
    NEW_ROUND = "new_round"
    ERROR = "error"
    
    # Bidirectional
    PING = "ping"
    PONG = "pong"
    PLAYER_LIST = "player_list"


class Message:
    """Represents a WebSocket message."""
    
    def __init__(self, message_type: MessageType, data: dict[str, Any] = None):
        """
        Create a message.
        Args:
            message_type: Type of message
            data: Message payload
        """
        self.type = message_type
        self.data = data or {}
    
    def to_json(self) -> str:
        """Serialize message to JSON string."""
        return json.dumps({
            'type': self.type.value,
            'data': self.data
        })
    
    @staticmethod
    def from_json(json_str: str) -> 'Message':
        """
        Deserialise message from JSON string.
        Args:
            json_str: JSON string
        Returns:
            Message object
        """
        obj = json.loads(json_str)
        message_type = MessageType(obj['type'])
        return Message(message_type, obj.get('data', {}))
    
    def __repr__(self) -> str:
        return f"Message(type={self.type.name}, data={self.data})"


def create_error_message(error_text: str) -> Message:
    """Create an error message."""
    return Message(MessageType.ERROR, {'error': error_text})


def create_player_joined_message(player: 'Player') -> Message:
    """Create a player joined notification."""
    return Message(MessageType.PLAYER_JOINED, player.to_dict())


def create_number_drawn_message(number: int) -> Message:
    """Create a number drawn notification."""
    return Message(MessageType.NUMBER_DRAWN, {'number': number})


def create_winner_message(player: 'Player', win_type: str, points_earned: int) -> Message:
    """Create a winner announcement message."""
    return Message(MessageType.WINNER_ANNOUNCED, {
        'player_id': player.player_id,
        'username': player.username,
        'win_type': win_type,
        'points_earned': points_earned
    })