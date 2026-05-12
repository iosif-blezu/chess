"""
Small opening book for the chess AI.

The book is intentionally compact and deterministic enough for tests, while still
using weighted choices so games do not always begin the same way.
"""
import random

# Move sequences are expressed in the same coordinate notation returned by
# ChessEngine.Move.getChessNotation(), for example e2e4.
# Each key is the current move history tuple and the value is a list of legal
# candidate replies. Repeated moves act as simple weights.
OPENING_BOOK = {
    (): ["e2e4", "d2d4", "g1f3", "c2c4"],
    ("e2e4",): ["e7e5", "c7c5", "e7e6", "c7c6"],
    ("d2d4",): ["d7d5", "g8f6", "e7e6"],
    ("g1f3",): ["d7d5", "g8f6"],
    ("c2c4",): ["e7e5", "g8f6", "c7c5"],
    ("e2e4", "e7e5"): ["g1f3", "f1c4"],
    ("e2e4", "c7c5"): ["g1f3", "d2d4"],
    ("e2e4", "e7e6"): ["d2d4"],
    ("e2e4", "c7c6"): ["d2d4"],
    ("d2d4", "d7d5"): ["c2c4", "g1f3"],
    ("d2d4", "g8f6"): ["c2c4", "g1f3"],
    ("e2e4", "e7e5", "g1f3"): ["b8c6", "g8f6"],
    ("e2e4", "e7e5", "f1c4"): ["g8f6", "b8c6"],
    ("d2d4", "d7d5", "c2c4"): ["e7e6", "c7c6", "d5c4"],
}


def get_book_move(gs, valid_moves):
    """Return a legal book move for the current move history, or None."""
    history = tuple(move.getChessNotation() for move in gs.moveLog)
    candidates = OPENING_BOOK.get(history)
    if not candidates:
        return None

    legal_by_notation = {move.getChessNotation(): move for move in valid_moves}
    legal_candidates = [legal_by_notation[move] for move in candidates if move in legal_by_notation]
    if not legal_candidates:
        return None
    return random.choice(legal_candidates)
