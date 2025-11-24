import logging
from multiplayer.player import Player

logger = logging.getLogger(__name__)


class Lobby:
    """Manages a game lobby with multiple players."""
    
    def __init__(self, lobby_id: str, host_player: Player, max_players: int = 10):
        """
        Initialise a lobby
        Args:
            lobby_id: Unique lobby identifier
            host_player: The player who created the lobby (host)
            max_players: Maximum number of players allowed
        """
        self.lobby_id = lobby_id
        self.host_id = host_player.player_id
        self.max_players = max_players
        self.players: dict[str, Player] = {host_player.player_id: host_player}
        self.is_game_started = False
        self.is_locked = False
        
        logger.info(f"Lobby {lobby_id} created by {host_player.username}")
    
    def add_player(self, player: Player) -> bool:
        """
        Add a player to the lobby
        Args:
            player: Player to add
        Returns:
            True if successfully added, False if lobby is full or locked
        """
        if self.is_locked:
            logger.warning(f"Cannot add player to locked lobby {self.lobby_id}")
            return False
        
        if len(self.players) >= self.max_players:
            logger.warning(f"Lobby {self.lobby_id} is full")
            return False
        
        if player.player_id in self.players:
            logger.warning(f"Player {player.username} already in lobby")
            return False
        
        self.players[player.player_id] = player
        logger.info(f"Player {player.username} joined lobby {self.lobby_id}")
        return True
    
    def remove_player(self, player_id: str) -> Player | None:
        """
        Remove a player from the lobby
        Args:
            player_id: ID of player to remove
        Returns:
            Removed player, or None if not found
        """
        if player_id in self.players:
            player = self.players.pop(player_id)
            logger.info(f"Player {player.username} left lobby {self.lobby_id}")
            
            if player_id == self.host_id and self.players:
                new_host = next(iter(self.players.values()))
                self.host_id = new_host.player_id
                logger.info(f"New host: {new_host.username}")
            
            return player
        return None
    
    def get_player(self, player_id: str) -> Player | None:
        """Get a player by ID."""
        return self.players.get(player_id)
    
    def get_player_list(self) -> list[dict]:
        """Get list of all players as dictionaries."""
        return [player.to_dict() for player in self.players.values()]
    
    def start_game(self) -> bool:
        """
        Start the game (lock the lobby).
        Returns:
            True if game started successfully
        """
        if len(self.players) < 2:
            logger.warning(f"Cannot start game in lobby {self.lobby_id}: need at least 2 players")
            return False
        
        self.is_game_started = True
        self.is_locked = True
        logger.info(f"Game started in lobby {self.lobby_id} with {len(self.players)} players")
        return True
    
    def reset_for_new_round(self, keep_points: bool = True) -> None:
        """
        Reset lobby for a new round.
        Args:
            keep_points: Whether to keep player points
        """
        for player in self.players.values():
            player.reset_for_new_round(keep_points=keep_points)
        
        self.is_game_started = False
        self.is_locked = False
        logger.info(f"Lobby {self.lobby_id} reset for new round")
    
    def is_empty(self) -> bool:
        """Check if lobby is empty."""
        return len(self.players) == 0
    
    def __repr__(self) -> str:
        return f"Lobby(id={self.lobby_id}, players={len(self.players)}/{self.max_players}, started={self.is_game_started})"