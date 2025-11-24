import asyncio
import websockets
import uuid
import json
import sys
from pathlib import Path

src_dir = Path(__file__).parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from interfaces.cli_presenter import CLIPresenter  # noqa: E402
from multiplayer.message_protocol import Message, MessageType  # noqa: E402


class MultiplayerClient:
    """CLI client for multiplayer bingo."""

    def __init__(self, server_url: str = "ws://localhost:8000"):
        """
        Initialise the client.
        Args:
            server_url: WebSocket server URL
        """
        self.server_url = server_url
        self.websocket = None
        self.player_id = str(uuid.uuid4())
        self.username = None
        self.lobby_id = None
        self.card = None
        self.drawn_numbers = set()  
        self.presenter = CLIPresenter()
        self.running = False
        self.is_host = False

    async def connect(self):
        """Connect to the server."""
        try:
            self.websocket = await websockets.connect(self.server_url)

            init_msg = Message(MessageType.PING, {'player_id': self.player_id})
            await self.websocket.send(init_msg.to_json())

            self.presenter.display_message("Connected to server!", style="success")
            return True
        except Exception as e:
            self.presenter.display_message(f"Connection failed: {e}", style="error")
            return False

    async def send_message(self, message: Message):
        """Send a message to the server."""
        if self.websocket:
            await self.websocket.send(message.to_json())

    async def join_lobby(self, lobby_id: str = None):
        """
        Join a lobby.

        Args:
            lobby_id: Optional lobby ID (creates new if not provided)
        """
        msg = Message(MessageType.JOIN_LOBBY, {
            'username': self.username,
            'lobby_id': lobby_id
        })
        await self.send_message(msg)

    async def start_game(self):
        """Request to start the game (host only)."""
        msg = Message(MessageType.START_GAME, {})
        await self.send_message(msg)

    async def draw_number(self):
        """Request to draw a number."""
        msg = Message(MessageType.REQUEST_DRAW, {})
        await self.send_message(msg)

    async def claim_bingo(self):
        """Claim bingo."""
        msg = Message(MessageType.CLAIM_BINGO, {})
        await self.send_message(msg)

    async def new_round(self):
        """Request new round (host only)."""
        msg = Message(MessageType.NEW_ROUND, {})
        await self.send_message(msg)

    async def handle_server_message(self, message: Message):
        """Handle incoming message from server."""

        if message.type == MessageType.LOBBY_JOINED:
            self.lobby_id = message.data['lobby_id']
            players = message.data['players']

            self.presenter.display_message(
                f"\nJoined lobby: {self.lobby_id}",
                style="success"
            )
            self.presenter.display_message(f"Players in lobby: {len(players)}", style="info")
            for p in players:
                marker = " (YOU)" if p['player_id'] == self.player_id else ""
                marker += " (HOST)" if players[0]['player_id'] == p['player_id'] else ""
                print(f"  - {p['username']}{marker}")

            self.is_host = (players[0]['player_id'] == self.player_id)

        elif message.type == MessageType.PLAYER_JOINED:
            player = message.data
            self.presenter.display_message(
                f"\n{player['username']} joined the lobby!",
                style="info"
            )

        elif message.type == MessageType.PLAYER_LEFT:
            username = message.data['username']
            self.presenter.display_message(
                f"\n{username} left the lobby.",
                style="info"
            )

        elif message.type == MessageType.GAME_STARTED:
            self.card = message.data['card']
            self.presenter.display_message("\nGame Started! ", style="success")
            self.display_card()

        elif message.type == MessageType.NUMBER_DRAWN:
            number = message.data['number']
            self.drawn_numbers.add(number)  
            self.presenter.display_called_number(number)

            if self.card:
                for row in self.card:
                    for i, val in enumerate(row):
                        if val == number:
                            self.presenter.display_message(
                                f"✓ Number {number} is on your card!",
                                style="success"
                            )
                            break

            self.display_card()

        elif message.type == MessageType.WINNER_ANNOUNCED:
            winner_name = message.data['username']
            win_type = message.data['win_type']
            points = message.data['points_earned']

            self.presenter.display_message(
                f"\n🏆 {winner_name} wins with {win_type}! (+{points} points) 🏆",
                style="success"
            )

        elif message.type == MessageType.BINGO_VALID:
            win_type = message.data['win_type']
            points = message.data['points_earned']
            self.presenter.display_message(
                f"\n🎉 BINGO! You won with {win_type}! (+{points} points) 🎉",
                style="success"
            )

        elif message.type == MessageType.BINGO_INVALID:
            reason = message.data.get('reason', 'Invalid claim')
            self.presenter.display_message(
                f"\n❌ Invalid bingo claim: {reason}",
                style="error"
            )

        elif message.type == MessageType.GAME_LOCKED:
            self.presenter.display_message(
                "\n🔒 Game locked - Winner declared!",
                style="info"
            )

        elif message.type == MessageType.NEW_ROUND:
            self.card = None
            self.drawn_numbers.clear()  
            self.presenter.display_message(
                "\n🔄 Starting new round...",
                style="info"
            )

        elif message.type == MessageType.ERROR:
            error = message.data['error']
            self.presenter.display_message(f"Error: {error}", style="error")

        elif message.type == MessageType.PONG:
            pass 

    def display_card(self):
        """Display the player's bingo card with highlighted drawn numbers."""
        if not self.card:
            self.presenter.display_message("No card assigned yet.", style="info")
            return

        print("\n" + "="*50)
        print("YOUR BINGO CARD".center(50))
        print("="*50)

        headers = ['B', 'I', 'N', 'G', 'O']
        print("     " + "  ".join(f"{h:^6}" for h in headers))
        print("     " + "-" * 40)

        GREEN_BG = '\033[42m'
        BLACK_TEXT = '\033[30m'
        BOLD = '\033[1m'
        RESET = '\033[0m'

        for row in self.card:
            row_display = []
            for val in row:
                if val == 'FREE':
                    row_display.append(f"{GREEN_BG}{BLACK_TEXT}{BOLD} FREE {RESET}")
                elif val in self.drawn_numbers:
                    row_display.append(f"{GREEN_BG}{BLACK_TEXT}{BOLD}{val:^6}{RESET}")
                else:
                    row_display.append(f"{val:^6}")
            print("     " + "  ".join(row_display))
        print()

        print(f"  {GREEN_BG}{BLACK_TEXT} Highlighted {RESET} = Drawn numbers on your card")

    async def receive_messages(self):
        """Listen for messages from server."""
        try:
            async for raw_message in self.websocket:
                try:
                    message = Message.from_json(raw_message)
                    await self.handle_server_message(message)

                    if self.running:
                        print(f"{CLIPresenter.GREEN_TEXT}>{CLIPresenter.RESET} ", end='', flush=True)

                except json.JSONDecodeError as e:
                    self.presenter.display_message(f"Invalid message from server: {e}", style="error")
        except websockets.exceptions.ConnectionClosed:
            self.presenter.display_message("\nConnection to server closed.", style="error")
            self.running = False

    async def handle_user_input(self):
        """Handle user input."""
        loop = asyncio.get_event_loop()

        while self.running:
            try:
                user_input = await loop.run_in_executor(
                    None,
                    lambda: input(f"{CLIPresenter.GREEN_TEXT}>{CLIPresenter.RESET} ")
                )

                if not user_input.strip():
                    continue

                parts = user_input.strip().lower().split(maxsplit=1)
                command = parts[0]
                args = parts[1] if len(parts) > 1 else ""

                if command == "join":
                    lobby_id = args if args else None
                    await self.join_lobby(lobby_id)

                elif command == "start":
                    if self.is_host:
                        await self.start_game()
                    else:
                        self.presenter.display_message("Only the host can start the game.", style="error")

                elif command == "draw":
                    await self.draw_number()

                elif command == "claim":
                    await self.claim_bingo()

                elif command == "newround":
                    if self.is_host:
                        await self.new_round()
                    else:
                        self.presenter.display_message("Only the host can start a new round.", style="error")

                elif command == "card":
                    self.display_card()

                elif command == "help":
                    self.show_help()

                elif command in ["quit", "exit", "q"]:
                    self.presenter.display_message("Exiting...", style="info")
                    self.running = False
                    break

                else:
                    self.presenter.display_message(
                        f"Unknown command: '{command}'. Type 'help' for available commands.",
                        style="error"
                    )

            except EOFError:
                self.running = False
                break
            except KeyboardInterrupt:
                print()
                self.presenter.display_message("Exiting...", style="info")
                self.running = False
                break
            except Exception as e:
                self.presenter.display_message(f"Error: {e}", style="error")

    def show_help(self):
        """Display help information."""
        self.presenter.display_message("\n=== Multiplayer Commands ===", style="info")

        commands = [
            ("join [lobby_id]", "Join a lobby (creates new if no ID provided)"),
            ("start", "Start the game (host only)"),
            ("draw", "Draw a number (any player can request)"),
            ("claim", "Claim bingo"),
            ("newround", "Start a new round (host only)"),
            ("card", "Display your card"),
            ("help", "Show this help message"),
            ("quit/exit", "Exit the game"),
        ]

        for cmd, desc in commands:
            print(f"  {CLIPresenter.GREEN_TEXT}{cmd:20}{CLIPresenter.RESET} {desc}")
        print()

    async def run(self):
        """Run the multiplayer client."""
        self.presenter.clear_screen()
        self.presenter.display_message(
            "\n╔═══════════════════════════════════════════════╗",
            style="success"
        )
        self.presenter.display_message(
            "║      Mini Bingo - Multiplayer Client          ║",
            style="success"
        )
        self.presenter.display_message(
            "╚═══════════════════════════════════════════════╝\n",
            style="success"
        )

        self.username = input("Enter your username: ").strip()
        if not self.username:
            self.username = f"Player_{self.player_id[:8]}"

        if not await self.connect():
            return

        self.presenter.display_message(
            "\nType 'join' to create/join a lobby, or 'help' for commands.\n",
            style="info"
        )

        self.running = True

        receive_task = asyncio.create_task(self.receive_messages())
        input_task = asyncio.create_task(self.handle_user_input())

        await input_task

        self.presenter.display_message("\nDisconnecting...", style="info")

        if not receive_task.done():
            receive_task.cancel()
            try:
                await asyncio.wait_for(receive_task, timeout=1.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass  

        if self.websocket:
            try:
                await asyncio.wait_for(self.websocket.close(), timeout=2.0)
            except (asyncio.TimeoutError, Exception):
                pass

        self.presenter.display_message("Goodbye!", style="success")

async def main():
    """Main entry point."""
    import sys

    server_url = "ws://localhost:8000"
    if len(sys.argv) > 1:
        server_url = sys.argv[1]

    client = MultiplayerClient(server_url)
    await client.run()


if __name__ == "__main__":
    asyncio.run(main())