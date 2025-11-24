import pytest

from game_logic.auto_check import check_completed_lines


@pytest.fixture
def sample_card():
    return [
        [1, 16, 31, 46, 61],
        [2, 17, 32, 47, 62],
        [3, 18, "FREE", 48, 63],
        [4, 19, 34, 49, 64],
        [5, 20, 35, 50, 65],
    ]


def test_detects_completed_row(sample_card):
    marks = {1, 16, 31, 46, 61}
    result = check_completed_lines(sample_card, marks)

    assert result["rows"][0] is True
    assert result["has_line"] is True
    assert result["completed_lines"] == 1


def test_detects_completed_column(sample_card):
    marks = {31, 32, "FREE", 34, 35}
    result = check_completed_lines(sample_card, marks)

    assert result["columns"][2] is True
    assert result["has_line"] is True
    assert result["completed_lines"] == 1


def test_detects_both_diagonals(sample_card):
    primary_marks = {1, 17, "FREE", 49, 65}
    secondary_marks = {61, 47, "FREE", 19, 5}
    marks = primary_marks | secondary_marks

    result = check_completed_lines(sample_card, marks)

    assert result["diagonals"]["primary"] is True
    assert result["diagonals"]["secondary"] is True
    assert result["completed_lines"] == 2


def test_invalid_grid_raises():
    with pytest.raises(ValueError):
        check_completed_lines([[True, False], [True]], {True})
