"""
Game logic for drawing numbers and marking cards.
"""

def mark_number_on_card(card, number):
    """
    Mark a number on a bingo card if it exists.
    
    Args:
        card: BingoCard instance
        number: The number to mark
        
    Returns:
        bool: True if the number was found and marked, False otherwise
    """
    return card.mark_number(number)

