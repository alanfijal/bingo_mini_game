WIN_TYPE_POINTS = {
    'full_house': 50,
    'blackout': 50,
    'four_lines': 40,
    'three_lines': 32,
    'two_lines': 25,
    'x_pattern': 20,
    't_pattern': 20,
    'l_pattern': 20,
    'four_corners': 15,
    'single_line': 10,
}

def check_single_line(card):
    """Check if any single line (row, column, or diagonal) is complete."""
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

    # Check main diagonal
    if all(_is_position_marked(card, i, i) for i in range(card_size)):
        return True

    # Check anti-diagonal
    if all(_is_position_marked(card, i, card_size - 1 - i) for i in range(card_size)):
        return True

    return False


def _count_completed_lines(card):
    """Helper function to count total completed lines."""
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

    return completed_lines


def check_two_lines(card):
    """Check if exactly two lines (rows, columns, or diagonals) are complete."""
    return _count_completed_lines(card) == 2


def check_three_lines(card):
    """Check if exactly three lines (rows, columns, or diagonals) are complete."""
    return _count_completed_lines(card) == 3


def check_four_lines(card):
    """Check if exactly four lines (rows, columns, or diagonals) are complete."""
    return _count_completed_lines(card) == 4


def check_full_house(card):
    """Check if all numbers on the card are marked (full house/blackout)."""
    card_data = card.bingo_card
    card_size = len(card_data)

    for row in range(card_size):
        for col in range(card_size):
            if not _is_position_marked(card, row, col):
                return False
    return True


def check_four_corners(card):
    """Check if all four corner positions are marked."""
    card_data = card.bingo_card
    card_size = len(card_data)
    corners = [(0, 0), (0, card_size - 1), (card_size - 1, 0), (card_size - 1, card_size - 1)]
    return all(_is_position_marked(card, row, col) for row, col in corners)


def check_x_pattern(card):
    """Check if both diagonals form an X pattern."""
    card_data = card.bingo_card
    card_size = len(card_data)
    main_diag = all(_is_position_marked(card, i, i) for i in range(card_size))
    anti_diag = all(_is_position_marked(card, i, card_size - 1 - i) for i in range(card_size))
    return main_diag and anti_diag


def check_t_pattern(card):
    """Check if top row and middle column form a T pattern."""
    card_data = card.bingo_card
    card_size = len(card_data)
    center_col = card_size // 2
    top_row = all(_is_position_marked(card, 0, col) for col in range(card_size))
    middle_col = all(_is_position_marked(card, row, center_col) for row in range(card_size))
    return top_row and middle_col


def check_l_pattern(card):
    """Check if top row and left column form an L pattern."""
    card_data = card.bingo_card
    card_size = len(card_data)
    top_row = all(_is_position_marked(card, 0, col) for col in range(card_size))
    left_col = all(_is_position_marked(card, row, 0) for row in range(card_size))
    return top_row and left_col


def _is_position_marked(card, row, col):
    """Helper function to check if a position on the card is marked."""
    card_data = card.bingo_card
    value = card_data[row][col]
    if value == 'FREE':
        return True
    return card.is_marked(value)


# Mapping of win condition names to their check functions
WIN_CONDITION_FUNCTIONS = {
    'single_line': check_single_line,
    'two_lines': check_two_lines,
    'three_lines': check_three_lines,
    'four_lines': check_four_lines,
    'full_house': check_full_house,
    'four_corners': check_four_corners,
    'x_pattern': check_x_pattern,
    't_pattern': check_t_pattern,
    'l_pattern': check_l_pattern,
    'blackout': check_full_house,
}


def check_win_condition(card, win_condition_mode=None):
    """
    Check if the card meets the specific win condition asked for.
    """
    if win_condition_mode is None:
        # Default behavior: check if ANY win exists
        return get_best_win(card) is not None

    check_function = WIN_CONDITION_FUNCTIONS.get(win_condition_mode)
    if check_function is None:
        raise ValueError(f"Unknown win condition mode: {win_condition_mode}")

    return check_function(card)


def get_best_win(card):
    """
    Checks ALL win conditions and returns the one with the highest point value.

    Args:
        card: BingoCard instance

    Returns:
        tuple: (win_type_string, points_int) or None if no win.
    """
    best_win = None
    max_points = 0

    # Iterate through all possible win functions
    for win_type, check_func in WIN_CONDITION_FUNCTIONS.items():
        if check_func(card):
            points = WIN_TYPE_POINTS.get(win_type, 0)

            # If this win is worth more than what we found so far, keep it
            if points > max_points:
                max_points = points
                best_win = win_type

    if best_win:
        return best_win, max_points
    return None

def get_available_win_conditions():
    """Get a list of all available win condition modes."""
    return list(WIN_CONDITION_FUNCTIONS.keys())

