"""
CLI presenter for displaying bingo cards and game information in the terminal.
"""

class CLIPresenter:
    """Handles terminal display of bingo game elements."""
    
    # ANSI color codes for terminal highlighting
    RESET = '\033[0m'
    BOLD = '\033[1m'
    GREEN_BG = '\033[42m'  # Green background
    GREEN_TEXT = '\033[32m'  # Green text
    YELLOW_TEXT = '\033[33m'  # Yellow text
    WHITE_TEXT = '\033[37m'  # White text
    BLACK_TEXT = '\033[30m'  # Black text
    
    @staticmethod
    def display_card(card, title="BINGO CARD"):
        """
        Display a bingo card with marked numbers highlighted.
        
        Args:
            card: BingoCard instance
            title: Optional title for the card
        """
        print(f"\n{'=' * 50}")
        print(f"{title:^50}")
        print(f"{'=' * 50}\n")
        
        # Print column headers (B, I, N, G, O)
        headers = ['B', 'I', 'N', 'G', 'O']
        header_row = "  ".join(f"{h:^6}" for h in headers)
        print(f"     {header_row}")
        print("     " + "-" * 40)
        
        # Print each row
        # Access the card data (instance attribute takes precedence over method)
        card_data = card.bingo_card
        for row_idx, row in enumerate(card_data):
            row_display = []
            for col_idx, value in enumerate(row):
                # Format the cell value
                if value == 'FREE':
                    # Free space - always highlighted
                    formatted = f"{CLIPresenter.GREEN_BG}{CLIPresenter.BLACK_TEXT}{CLIPresenter.BOLD} FREE {CLIPresenter.RESET}"
                elif card.is_marked(value):
                    # Marked number - highlight with green background
                    formatted = f"{CLIPresenter.GREEN_BG}{CLIPresenter.BLACK_TEXT}{CLIPresenter.BOLD}{str(value):^6}{CLIPresenter.RESET}"
                else:
                    # Unmarked number - normal display
                    formatted = f"{str(value):^6}"
                
                row_display.append(formatted)
            
            print("     " + "  ".join(row_display))
        
        print()
    
    @staticmethod
    def display_called_number(number):
        """
        Display a called number prominently.
        
        Args:
            number: The number that was called
        """
        print(f"\n{CLIPresenter.BOLD}{CLIPresenter.YELLOW_TEXT}{'=' * 50}")
        print(f"  Number Called: {CLIPresenter.GREEN_BG}{CLIPresenter.BLACK_TEXT} {number:^3} {CLIPresenter.RESET}")
        print(f"{'=' * 50}{CLIPresenter.RESET}\n")
    
    @staticmethod
    def display_message(message, style="normal"):
        """
        Display a message with optional styling.
        
        Args:
            message: The message to display
            style: Style type ('normal', 'success', 'error', 'info')
        """
        styles = {
            'normal': CLIPresenter.RESET,
            'success': f"{CLIPresenter.GREEN_TEXT}{CLIPresenter.BOLD}",
            'error': f"\033[31m{CLIPresenter.BOLD}",  # Red text
            'info': f"{CLIPresenter.YELLOW_TEXT}"
        }
        
        style_code = styles.get(style, CLIPresenter.RESET)
        print(f"{style_code}{message}{CLIPresenter.RESET}")
    
    @staticmethod
    def clear_screen():
        """Clear the terminal screen."""
        print("\033[2J\033[H", end="")

