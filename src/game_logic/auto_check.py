from typing import Any, Iterable, List, Sequence

Grid = Sequence[Sequence[Any]]


def _validate_grid(grid: Grid) -> int:
    if not grid:
        raise ValueError("Card grid must contain at least one row.")

    size = len(grid)
    for row in grid:
        if len(row) != size:
            raise ValueError("Card grid must be square (same number of rows and columns).")
    return size


def _normalize_marks(grid: Grid, marked_values: Iterable[Any] | None) -> List[List[bool]]:
    marks = set(marked_values or [])
    normalized: List[List[bool]] = []

    for row in grid:
        normalized_row: List[bool] = []
        for cell in row:
            if isinstance(cell, bool):
                normalized_row.append(cell)
            elif cell == "FREE":
                normalized_row.append(True)
            else:
                normalized_row.append(cell in marks)
        normalized.append(normalized_row)
    return normalized


def check_completed_lines(card_grid: Grid, marked_values: Iterable[Any] | None = None) -> dict:
    """
    Check the provided Bingo card for completed rows, columns, and diagonals.

    Args:
        card_grid: 2D square grid representing the Bingo card layout.
        marked_values: Iterable of values that have been called/marked. The FREE
            space is automatically treated as marked.

    Returns:
        Dictionary containing completion flags for rows, columns, diagonals, and
        aggregate helpers (`has_line`, `completed_lines`).
    """

    size = _validate_grid(card_grid)
    normalized = _normalize_marks(card_grid, marked_values)

    rows = [all(row) for row in normalized]
    columns = [all(normalized[row_idx][col_idx] for row_idx in range(size)) for col_idx in range(size)]

    primary_diag = all(normalized[idx][idx] for idx in range(size))
    secondary_diag = all(normalized[idx][size - 1 - idx] for idx in range(size))
    diagonals = {"primary": primary_diag, "secondary": secondary_diag}

    completed_lines = sum(rows) + sum(columns) + sum(diagonals.values())

    return {
        "rows": rows,
        "columns": columns,
        "diagonals": diagonals,
        "completed_lines": int(completed_lines),
        "has_line": completed_lines > 0,
    }
