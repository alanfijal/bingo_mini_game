"""
Bingo game rules configuration.
"""

# Default rules for the bingo game
DEFAULT_RULES = {
    'free_space': True,  # Whether to include a free space in the center
    'card_size': 5,  # Size of the bingo card (5x5)
    'number_ranges': [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)],
      # Column ranges
    'win_condition': 'single_line',  # Default win condition mode
    # Available win condition modes:
    # - 'single_line': Any one row, column, or diagonal
    # - 'two_lines': Any two lines (rows, columns, or diagonals)
    # - 'full_house': All numbers on the card marked
    # - 'four_corners': All four corner positions marked
    # - 'x_pattern': Both diagonals (X shape)
    # - 't_pattern': Top row and middle column (T shape)
    # - 'l_pattern': Top row and left column (L shape)
    # - 'blackout': All numbers marked (same as full_house)
}

def get_rules(custom_rules=None):
    """
    Get the rules configuration.
    
    Args:
        custom_rules: Optional dict to override default rules
        
    Returns:
        dict: The rules configuration
    """
    rules = DEFAULT_RULES.copy()
    if custom_rules:
        rules.update(custom_rules)
    return rules

def win_conditions(rules):
    """
    Get the win conditions for the bingo game.
    
    Args:
        rules: The rules configuration
        
    Returns:
        list: The win conditions
    """
    return rules.get('win_conditions', [])
