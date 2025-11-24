import pytest
from domain.bingo_card import BingoCard

@pytest.fixture
def card():
    return BingoCard()

def test_dimensions(card):
    assert len(card.bingo_card) == 5
    for row in card.bingo_card:
        assert len(row) == 5

def test_no_duplicates(card):
    nums = [n for row in card.bingo_card for n in row if n != 'FREE']
    assert len(nums) == len(set(nums))

def test_center_free(card):
    assert card.bingo_card[2][2] == 'FREE'

def test_column_ranges(card):
    ranges = [(1,15), (16,30), (31,45), (46,60), (61,75)]
    for col, (start, end) in enumerate(ranges):
        for row in range(5):
            value = card.bingo_card[row][col]
            if value != 'FREE':
                assert start <= value <= end, f"Number {value} in column {col} is out of range {start}-{end}"