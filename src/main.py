import sys
import logging
from pathlib import Path

src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from interfaces.cli_controller import CLIController  # noqa: E402
from domain.rules import get_rules  # noqa: E402


def setup_logging():
    """Configure logging for the application."""
    log_dir = Path(__file__).parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / 'bingo_game.log'

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
        ]
    )


def main():
    """Main entry point for the game."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("=== Mini Bingo Game Starting ===")
    
    try:
        rules = get_rules()
        controller = CLIController(rules=rules)
        controller.run()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\nFatal error occurred: {e}")
        sys.exit(1)
    
    logger.info("=== Mini Bingo Game Ended ===")


if __name__ == "__main__":
    main()