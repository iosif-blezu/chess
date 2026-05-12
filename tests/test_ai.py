import unittest

import BlupAI as AI
import ChessEngine


FAST_SETTINGS = AI.DifficultySettings(
    "test", max_depth=2, time_limit=0.75, use_opening_book=False,
    use_quiescence=True, use_transposition_table=True, random_move_chance=0.0
)
TACTICAL_SETTINGS = AI.DifficultySettings(
    "tactical", max_depth=3, time_limit=1.0, use_opening_book=False,
    use_quiescence=True, use_transposition_table=True, random_move_chance=0.0
)


def empty_state(white_to_move=True):
    gs = ChessEngine.GameState()
    gs.board = [["--" for _ in range(8)] for _ in range(8)]
    gs.whiteToMove = white_to_move
    gs.moveLog = []
    gs.enpassantPossible = ()
    gs.currentCastlingRights = ChessEngine.CastleRights(False, False, False, False)
    gs.castleRightsLog = [ChessEngine.CastleRights(False, False, False, False)]
    gs.checkMate = False
    gs.staleMate = False
    return gs


def place(gs, square, piece):
    col = ChessEngine.Move.filesToCols[square[0]]
    row = ChessEngine.Move.ranksToRows[square[1]]
    gs.board[row][col] = piece
    if piece == "wK":
        gs.whiteKingLocation = (row, col)
    elif piece == "bK":
        gs.blackKingLocation = (row, col)


def best_move_notation(gs, settings=FAST_SETTINGS):
    valid_moves = gs.getValidMoves()
    move = AI.findBestMove(gs, valid_moves, difficulty=settings)
    return move.getChessNotation(), move, valid_moves


class TestChessAI(unittest.TestCase):
    def test_ai_captures_hanging_queen(self):
        gs = empty_state()
        place(gs, "e1", "wK")
        place(gs, "e8", "bK")
        place(gs, "a1", "wR")
        place(gs, "a8", "bQ")

        notation, _, _ = best_move_notation(gs)

        self.assertEqual("a1a8", notation)

    def test_ai_finds_mate_in_one(self):
        gs = empty_state()
        place(gs, "f6", "wK")
        place(gs, "g7", "wQ")
        place(gs, "h8", "bK")

        _, move, _ = best_move_notation(gs, TACTICAL_SETTINGS)
        gs.makeMove(move)
        gs.getValidMoves()

        self.assertTrue(gs.checkMate)

    def test_ai_escapes_immediate_rook_check(self):
        gs = empty_state(white_to_move=False)
        place(gs, "e1", "wK")
        place(gs, "e8", "bK")
        place(gs, "e2", "wR")

        _, move, valid_moves = best_move_notation(gs, TACTICAL_SETTINGS)

        self.assertIn(move, valid_moves)
        gs.makeMove(move)
        gs.getValidMoves()
        gs.whiteToMove = False
        self.assertFalse(gs.inCheck())
        gs.whiteToMove = True

    def test_ai_promotes_available_pawn(self):
        gs = empty_state()
        place(gs, "e1", "wK")
        place(gs, "h8", "bK")
        place(gs, "a7", "wp")

        notation, move, _ = best_move_notation(gs)

        self.assertEqual("a7a8", notation)
        self.assertTrue(move.isPawnPromotion)

    def test_ai_returns_legal_move_from_initial_position(self):
        gs = ChessEngine.GameState()
        valid_moves = gs.getValidMoves()

        move = AI.findBestMove(gs, valid_moves, difficulty=FAST_SETTINGS)

        self.assertIn(move, valid_moves)


if __name__ == "__main__":
    unittest.main()
