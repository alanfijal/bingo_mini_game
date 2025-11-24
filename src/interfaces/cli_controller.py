import logging
from typing import Callable
from game_logic.game_session import GameSession
from game_logic.win_con import get_available_win_conditions
from interfaces.cli_presenter import CLIPresenter

logger = logging.getLogger(__name__)

class CLIController:
    """Handles user input and command execution."""
    
    def __init__(self, rules: dict | None = None):
        """
        Initialise the CLI controller
        Args:
            rules: Optional custom rules configuration
        """
        self.session = GameSession(rules=rules)
        self.presenter = CLIPresenter()
        self.running = False
        
        self.commands: dict[str, Callable] = {
            'start': self.cmd_start,
            'reset': self.cmd_reset,
            'draw': self.cmd_draw,
            'mark': self.cmd_mark,
            'claim': self.cmd_claim,
            'card': self.cmd_show_card,
            'called': self.cmd_show_called,
            'stats': self.cmd_show_stats,
            'help': self.cmd_help,
            'quit': self.cmd_quit,
            'exit': self.cmd_quit,
        }
        
        logger.info("CLI controller initialised")
    
    def run(self) -> None:
        """Main game loop"""
        self.running = True
        self.presenter.clear_screen()
        self.presenter.display_message(
            "\n╔═══════════════════════════════════════════════╗",
            style="success"
        )
        self.presenter.display_message(
            "║          Welcome to Mini Bingo Game!          ║",
            style="success"
        )
        self.presenter.display_message(
            "╚═══════════════════════════════════════════════╝\n",
            style="success"
        )
        self.presenter.display_message(
            "Type 'help' for available commands or 'start' to begin.\n",
            style="info"
        )
        
        logger.info("Game loop started")
        
        while self.running:
            try:
                user_input = input(f"{CLIPresenter.GREEN_TEXT}bingo>{CLIPresenter.RESET} ").strip()
                
                if not user_input:
                    continue
                
                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""
                
                if command in self.commands:
                    self.commands[command](args)
                else:
                    self.presenter.display_message(
                        f"Unknown command: '{command}'. Type 'help' for available commands.",
                        style="error"
                    )
                    logger.warning(f"Unknown command entered: {command}")
            
            except KeyboardInterrupt:
                print()
                self.cmd_quit("")
            except EOFError:
                print()
                self.cmd_quit("")
            except Exception as e:
                self.presenter.display_message(
                    f"Error: {str(e)}",
                    style="error"
                )
                logger.error(f"Command execution error: {e}", exc_info=True)
    
    def cmd_start(self, args: str) -> None:
        """Start a new game"""
        self.session.start_new_game()
    
    def cmd_reset(self, args: str) -> None:
        """Reset the game with a new card"""
        self.session.reset_game()
    
    def cmd_draw(self, args: str) -> None:
        """Draw a number from the pool"""
        self.session.draw_number()
    
    def cmd_mark(self, args: str) -> None:
        """
        Mark a number on the card.
        Args:
            args: The number to mark
        """
        if not args:
            self.presenter.display_message(
                "Usage: mark <number>",
                style="error"
            )
            return
        
        try:
            number = int(args)
            self.session.mark_number(number)
            self.session.show_card()
        except ValueError:
            self.presenter.display_message(
                f"Invalid number: '{args}'",
                style="error"
            )
    
    def cmd_claim(self, args: str) -> None:
        """Claim bingo"""
        self.session.claim_bingo()
    
    def cmd_show_card(self, args: str) -> None:
        """Show the current card"""
        self.session.show_card()
    
    def cmd_show_called(self, args: str) -> None:
        """Show all called numbers"""
        self.session.show_called_numbers()
    
    def cmd_show_stats(self, args: str) -> None:
        """Show game statistics"""
        self.session.show_stats()
    
    def cmd_help(self, args: str) -> None:
        """Display help information"""
        self.presenter.display_message("\n=== Available Commands ===", style="info")
        
        commands_help = [
            ("start", "Start a new game with a fresh card"),
            ("reset", "Reset the game and generate a new card"),
            ("draw", "Draw a random number from the pool"),
            ("mark <num>", "Manually mark a number on your card"),
            ("claim", "Claim bingo (checks if you've won)"),
            ("card", "Display your current bingo card"),
            ("called", "Show all numbers that have been called"),
            ("stats", "Display game statistics"),
            ("help", "Show this help message"),
            ("quit/exit", "Exit the game"),
        ]
        
        for cmd, description in commands_help:
            print(f"  {CLIPresenter.GREEN_TEXT}{cmd:15}{CLIPresenter.RESET} {description}")
        
        print()
        self.presenter.display_message(f"Available win conditions: {', '.join(get_available_win_conditions())}", style="info")
        print()
    
    def cmd_quit(self, args: str) -> None:
        """Exit the game."""
        self.presenter.display_message("\nThanks for playing Mini Bingo! Goodbye!\n", style="success")
        logger.info("Game exited by user")
        self.running = False