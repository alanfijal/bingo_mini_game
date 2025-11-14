"""
Win condition implementations for different bingo game modes.
"""

def check_single_line(card):
    """
    Check if any single line (row, column, or diagonal) is complete.
    
    Args:
        card: BingoCard instance
        
    Returns:
        bool: True if any line is complete, False otherwise
    """
    card_data = card.bingo_card
    card_size = len(card_data)
    
    # Check rows
    for row in range(card_size):
        if all(_is_position_marked(card, row, col) for col in range(card_size)):
            return True
    
    # Check columns
    for col in range(card_size):
        if all(_is_position_marked(card, row, col) for row in range(card_size)):
            return True
    
    # Check main diagonal (top-left to bottom-right)
    if all(_is_position_marked(card, i, i) for i in range(card_size)):
        return True
    
    # Check anti-diagonal (top-right to bottom-left)
    if all(_is_position_marked(card, i, card_size - 1 - i) for i in range(card_size)):
        return True
    
    return False


def check_two_lines(card):
    """
    Check if any two lines (rows, columns, or diagonals) are complete.
    
    Args:
        card: BingoCard instance
        
    Returns:
        bool: True if at least two lines are complete, False otherwise
    """
    card_data = card.bingo_card
    card_size = len(card_data)
    completed_lines = 0
    
    # Check rows
    for row in range(card_size):
        if all(_is_position_marked(card, row, col) for col in range(card_size)):
            completed_lines += 1
    
    # Check columns
    for col in range(card_size):
        if all(_is_position_marked(card, row, col) for row in range(card_size)):
            completed_lines += 1
    
    # Check main diagonal
    if all(_is_position_marked(card, i, i) for i in range(card_size)):
        completed_lines += 1
    
    # Check anti-diagonal
    if all(_is_position_marked(card, i, card_size - 1 - i) for i in range(card_size)):
        completed_lines += 1
    
    return completed_lines >= 2


def check_full_house(card):
    """
    Check if all numbers on the card are marked (full house/blackout).
    
    Args:
        card: BingoCard instance
        
    Returns:
        bool: True if all positions are marked, False otherwise
    """
    card_data = card.bingo_card
    card_size = len(card_data)
    
    for row in range(card_size):
        for col in range(card_size):
            if not _is_position_marked(card, row, col):
                return False
    
    return True


def check_four_corners(card):
    """
    Check if all four corner positions are marked.
    
    Args:
        card: BingoCard instance
        
    Returns:
        bool: True if all four corners are marked, False otherwise
    """
    card_data = card.bingo_card
    card_size = len(card_data)
    
    corners = [
        (0, 0),  # Top-left
        (0, card_size - 1),  # Top-right
        (card_size - 1, 0),  # Bottom-left
        (card_size - 1, card_size - 1)  # Bottom-right
    ]
    
    return all(_is_position_marked(card, row, col) for row, col in corners)


def check_x_pattern(card):
    """
    Check if both diagonals form an X pattern (both diagonals complete).
    
    Args:
        card: BingoCard instance
        
    Returns:
        bool: True if both diagonals are complete, False otherwise
    """
    card_data = card.bingo_card
    card_size = len(card_data)
    
    # Check main diagonal
    main_diagonal = all(_is_position_marked(card, i, i) for i in range(card_size))
    
    # Check anti-diagonal
    anti_diagonal = all(_is_position_marked(card, i, card_size - 1 - i) for i in range(card_size))
    
    return main_diagonal and anti_diagonal


def check_t_pattern(card):
    """
    Check if top row and middle column form a T pattern.
    
    Args:
        card: BingoCard instance
        
    Returns:
        bool: True if T pattern is complete, False otherwise
    """
    card_data = card.bingo_card
    card_size = len(card_data)
    center_col = card_size // 2
    
    # Check top row
    top_row = all(_is_position_marked(card, 0, col) for col in range(card_size))
    
    # Check middle column
    middle_col = all(_is_position_marked(card, row, center_col) for row in range(card_size))
    
    return top_row and middle_col


def check_l_pattern(card):
    """
    Check if top row and left column form an L pattern.
    
    Args:
        card: BingoCard instance
        
    Returns:
        bool: True if L pattern is complete, False otherwise
    """
    card_data = card.bingo_card
    card_size = len(card_data)
    
    # Check top row
    top_row = all(_is_position_marked(card, 0, col) for col in range(card_size))
    
    # Check left column
    left_col = all(_is_position_marked(card, row, 0) for row in range(card_size))
    
    return top_row and left_col


def _is_position_marked(card, row, col):
    """
    Helper function to check if a position on the card is marked.
    
    Args:
        card: BingoCard instance
        row: Row index
        col: Column index
        
    Returns:
        bool: True if the position is marked, False otherwise
    """
    card_data = card.bingo_card
    value = card_data[row][col]
    
    # Free space is always considered marked
    if value == 'FREE':
        return True
    
    # Check if the number is in the marked set
    return card.is_marked(value)


# Mapping of win condition names to their check functions
WIN_CONDITION_FUNCTIONS = {
    'single_line': check_single_line,
    'two_lines': check_two_lines,
    'full_house': check_full_house,
    'four_corners': check_four_corners,
    'x_pattern': check_x_pattern,
    't_pattern': check_t_pattern,
    'l_pattern': check_l_pattern,
    'blackout': check_full_house,  # Alias for full_house
}


def check_win_condition(card, win_condition_mode=None):
    """
    Check if the card meets the win condition based on the game mode.
    
    Args:
        card: BingoCard instance
        win_condition_mode: String specifying the win condition mode.
                          If None, uses card.rules['win_condition']
        
    Returns:
        bool: True if the win condition is met, False otherwise
    """
    if win_condition_mode is None:
        win_condition_mode = card.rules.get('win_condition', 'single_line')
    
    check_function = WIN_CONDITION_FUNCTIONS.get(win_condition_mode)
    
    if check_function is None:
        raise ValueError(f"Unknown win condition mode: {win_condition_mode}. "
                        f"Available modes: {list(WIN_CONDITION_FUNCTIONS.keys())}")
    
    return check_function(card)


def get_available_win_conditions():
    """
    Get a list of all available win condition modes.
    
    Returns:
        list: List of available win condition mode names
    """
    return list(WIN_CONDITION_FUNCTIONS.keys())

