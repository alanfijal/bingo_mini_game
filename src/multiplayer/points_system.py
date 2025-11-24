# Points awarded for different win types
WIN_TYPE_POINTS: dict[str, int] = {
    'single_line': 10,          # Little bingo
    'two_lines': 25,             # Double bingo
    'three_lines': 32,           # Triple bingo
    'four_lines': 40,            # Quad bingo
    'four_corners': 15,          # Corner pattern
    'x_pattern': 20,             # X pattern
    't_pattern': 20,             # T pattern
    'l_pattern': 20,             # L pattern
    'full_house': 50,            # Big bingo / Blackout
    'blackout': 50,              # Alias for full_house
}


def calculate_points(win_type: str) -> int:
    """
    Calculate points for a win type.
    Args:
        win_type: Type of win
    Returns:
        Points earned
    """
    return WIN_TYPE_POINTS.get(win_type, 10)


def get_win_type_name(win_type: str) -> str:
    """
    Get human-readable name for win type.
    Args:
        win_type: Win type identifier
    Returns:
        Human-readable name
    """
    names = {
        'single_line': 'Little Bingo (Single Line)',
        'two_lines': 'Double Bingo (Two Lines)',
        'three_lines': 'Triple Bingo (Three Lines)',
        'four_lines': 'Quad Bingo (Four Lines)',
        'four_corners': 'Four Corners',
        'x_pattern': 'X Pattern',
        't_pattern': 'T Pattern',
        'l_pattern': 'L Pattern',
        'full_house': 'Big Bingo (Full House)',
        'blackout': 'Blackout',
    }
    return names.get(win_type, win_type.replace('_', ' ').title())