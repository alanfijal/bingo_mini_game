import asyncio
import websockets
import logging
import json
from pathlib import Path
from multiplayer.lobby import Lobby
from multiplayer.player import Player
from multiplayer.game_coordinator import GameCoordinator
from multiplayer.message_protocol import (
    Message, MessageType, create_error_message,
    create_player_joined_message, create_number_drawn_message,
    create_winner_message
)

# Setup logging to file
log_dir = Path('/app/logs')
log_dir.mkdir(exist_ok=True)
log_file = log_dir / 'bingo_server.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()  # Also log to console for Docker logs
    ]
)
logger = logging.getLogger(__name__)


class BingoServer:
    """WebSocket server for multiplayer bingo."""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        """
        Initialise the server.
        Args:
            host: Server host address
            port: Server port
        """
        self.host = host
        self.port = port
        
        self.connections: dict[str, any] = {}
        self.lobbies: dict[str, Lobby] = {}
        self.coordinators: dict[str, GameCoordinator] = {}
        self.player_lobby_map: dict[str, str] = {}

        logger.info(f"Bingo server initialised on {host}:{port}")

    async def register_connection(self, websocket, player_id: str):
        """Register a new WebSocket connection."""
        self.connections[player_id] = websocket
        logger.info(f"Connection registered for player {player_id}")
    
    async def unregister_connection(self, player_id: str):
        """Unregister a WebSocket connection."""
        if player_id in self.connections:
            del self.connections[player_id]
            logger.info(f"Connection unregistered for player {player_id}")
        
        if player_id in self.player_lobby_map:
            lobby_id = self.player_lobby_map[player_id]
            await self.handle_leave_lobby(player_id, lobby_id)
    
    async def broadcast_to_lobby(self, lobby_id: str, message: Message, exclude_player: str = None):
        """
        Broadcast a message to all players in a lobby.
        Args:
            lobby_id: Lobby ID
            message: Message to broadcast
            exclude_player: Optional player ID to exclude from broadcast
        """
        lobby = self.lobbies.get(lobby_id)
        if not lobby:
            return
        
        tasks = []
        for player_id in lobby.players:
            if player_id != exclude_player and player_id in self.connections:
                websocket = self.connections[player_id]
                tasks.append(self.send_message(websocket, message))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def send_message(self, websocket, message: Message):
        """Send a message to a specific WebSocket."""
        try:
            await websocket.send(message.to_json())
        except Exception as e:
            logger.error(f"Error sending message: {e}")

    async def handle_join_lobby(self, player_id: str, username: str, lobby_id: str = None):
        """
        Handle a player joining a lobby.
        Args:
            player_id: Player ID
            username: Player username
            lobby_id: Optional lobby ID (creates new if not provided)
        """
        player = Player(username, player_id)
        
        if not lobby_id or lobby_id not in self.lobbies:
            lobby_id = f"lobby_{len(self.lobbies) + 1}"
            lobby = Lobby(lobby_id, player)
            self.lobbies[lobby_id] = lobby
            self.coordinators[lobby_id] = GameCoordinator(lobby)
            logger.info(f"New lobby created: {lobby_id}")
        else:
            lobby = self.lobbies[lobby_id]
            if not lobby.add_player(player):
                error_msg = create_error_message("Cannot join lobby (full or locked)")
                await self.send_message(self.connections[player_id], error_msg)
                return
        
        self.player_lobby_map[player_id] = lobby_id
        
        join_msg = Message(MessageType.LOBBY_JOINED, {
            'lobby_id': lobby_id,
            'player': player.to_dict(),
            'players': lobby.get_player_list()
        })
        await self.send_message(self.connections[player_id], join_msg)
        
        player_joined_msg = create_player_joined_message(player)
        await self.broadcast_to_lobby(lobby_id, player_joined_msg, exclude_player=player_id)
    
    async def handle_leave_lobby(self, player_id: str, lobby_id: str):
        """Handle a player leaving a lobby."""
        lobby = self.lobbies.get(lobby_id)
        if not lobby:
            return
        
        player = lobby.remove_player(player_id)
        if player:
            if player_id in self.player_lobby_map:
                del self.player_lobby_map[player_id]
            
            leave_msg = Message(MessageType.PLAYER_LEFT, {
                'player_id': player_id,
                'username': player.username
            })
            await self.broadcast_to_lobby(lobby_id, leave_msg)
            
            if lobby.is_empty():
                del self.lobbies[lobby_id]
                del self.coordinators[lobby_id]
                logger.info(f"Lobby {lobby_id} removed (empty)")
    
    async def handle_start_game(self, player_id: str):
        """Handle game start request."""
        lobby_id = self.player_lobby_map.get(player_id)
        if not lobby_id:
            return
        
        lobby = self.lobbies[lobby_id]
        
        if player_id != lobby.host_id:
            error_msg = create_error_message("Only host can start the game")
            await self.send_message(self.connections[player_id], error_msg)
            return
        
        coordinator = self.coordinators[lobby_id]
        if coordinator.start_game():
            for pid, player in lobby.players.items():
                if pid in self.connections:
                    card_data = [[cell for cell in row] for row in player.card.bingo_card]
                    start_msg = Message(MessageType.GAME_STARTED, {
                        'lobby_id': lobby_id,
                        'card': card_data,
                        'player_count': len(lobby.players)
                    })
                    await self.send_message(self.connections[pid], start_msg)
    
    async def handle_request_draw(self, player_id: str):
        """Handle number draw request."""
        lobby_id = self.player_lobby_map.get(player_id)
        if not lobby_id:
            return
        
        coordinator = self.coordinators[lobby_id]
        number = coordinator.draw_number()
        
        if number:
            draw_msg = create_number_drawn_message(number)
            await self.broadcast_to_lobby(lobby_id, draw_msg)
        else:
            error_msg = create_error_message("No more numbers to draw")
            await self.send_message(self.connections[player_id], error_msg)
    
    async def handle_claim_bingo(self, player_id: str):
        """Handle bingo claim."""
        lobby_id = self.player_lobby_map.get(player_id)
        if not lobby_id:
            return

        coordinator = self.coordinators[lobby_id]
        is_valid, win_type, points_earned = coordinator.validate_bingo_claim(player_id)

        if is_valid:
            player = coordinator.lobby.get_player(player_id)

            valid_msg = Message(MessageType.BINGO_VALID, {
                'win_type': win_type,
                'points_earned': points_earned
            })
            await self.send_message(self.connections[player_id], valid_msg)

            winner_msg = create_winner_message(player, win_type, points_earned)
            await self.broadcast_to_lobby(lobby_id, winner_msg)

            lock_msg = Message(MessageType.GAME_LOCKED, {})
            await self.broadcast_to_lobby(lobby_id, lock_msg)
        else:
            invalid_msg = Message(MessageType.BINGO_INVALID, {
                'reason': 'Win condition not met'
            })
            await self.send_message(self.connections[player_id], invalid_msg)
    
    async def handle_new_round(self, player_id: str):
        """Handle new round request."""
        lobby_id = self.player_lobby_map.get(player_id)
        if not lobby_id:
            return
        
        lobby = self.lobbies[lobby_id]
        
        if player_id != lobby.host_id:
            error_msg = create_error_message("Only host can start new round")
            await self.send_message(self.connections[player_id], error_msg)
            return
        
        coordinator = self.coordinators[lobby_id]
        coordinator.reset_for_new_round(keep_points=True)
        
        new_round_msg = Message(MessageType.NEW_ROUND, {
            'lobby_id': lobby_id
        })
        await self.broadcast_to_lobby(lobby_id, new_round_msg)
    
    async def handle_message(self, websocket, message: Message, player_id: str):
        """
        Route incoming message to appropriate handler.
        Args:
            websocket: WebSocket connection
            message: Parsed message
            player_id: Player ID
        """
        handlers = {
            MessageType.JOIN_LOBBY: lambda: self.handle_join_lobby(
                player_id, 
                message.data.get('username'),
                message.data.get('lobby_id')
            ),
            MessageType.LEAVE_LOBBY: lambda: self.handle_leave_lobby(
                player_id,
                message.data.get('lobby_id')
            ),
            MessageType.START_GAME: lambda: self.handle_start_game(player_id),
            MessageType.REQUEST_DRAW: lambda: self.handle_request_draw(player_id),
            MessageType.CLAIM_BINGO: lambda: self.handle_claim_bingo(player_id),
            MessageType.NEW_ROUND: lambda: self.handle_new_round(player_id),
            MessageType.PING: lambda: self.send_message(
                websocket, 
                Message(MessageType.PONG)
            ),
        }
        
        handler = handlers.get(message.type)
        if handler:
            await handler()
        else:
            logger.warning(f"Unknown message type: {message.type}")
    
    async def connection_handler(self, websocket):
        """
        Handle a WebSocket connection.
        Args:
            websocket: WebSocket connection
        """
        player_id = None
        
        try:
            raw_message = await websocket.recv()
            initial_msg = Message.from_json(raw_message)
            
            player_id = initial_msg.data.get('player_id')
            if not player_id:
                logger.error("No player_id in initial message")
                return
            
            await self.register_connection(websocket, player_id)
            
            async for raw_message in websocket:
                try:
                    message = Message.from_json(raw_message)
                    await self.handle_message(websocket, message, player_id)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON received: {raw_message}")
                except Exception as e:
                    logger.error(f"Error handling message: {e}", exc_info=True)
        
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Connection closed for player {player_id}")
        except Exception as e:
            logger.error(f"Connection error: {e}", exc_info=True)
        finally:
            if player_id:
                await self.unregister_connection(player_id)
    
    async def start(self):
        """Start the WebSocket server."""
        logger.info(f"Starting Bingo WebSocket server on {self.host}:{self.port}")
        async with websockets.serve(self.connection_handler, self.host, self.port):
            await asyncio.Future()


async def main():
    """Main entry point for the server."""
    server = BingoServer(host="0.0.0.0", port=8000)
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())