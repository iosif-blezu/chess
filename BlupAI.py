"""
Handling the AI moves.

The engine uses iterative-deepening negamax with alpha-beta pruning, move
ordering, quiescence search, a transposition table, a small opening book, and a
richer hand-written evaluation function.
"""
import random
import time
from dataclasses import dataclass

import OpeningBook

piece_score = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}

knight_scores = [[0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0],
                 [0.1, 0.3, 0.5, 0.5, 0.5, 0.5, 0.3, 0.1],
                 [0.2, 0.5, 0.6, 0.65, 0.65, 0.6, 0.5, 0.2],
                 [0.2, 0.55, 0.65, 0.7, 0.7, 0.65, 0.55, 0.2],
                 [0.2, 0.5, 0.65, 0.7, 0.7, 0.65, 0.5, 0.2],
                 [0.2, 0.55, 0.6, 0.65, 0.65, 0.6, 0.55, 0.2],
                 [0.1, 0.3, 0.5, 0.55, 0.55, 0.5, 0.3, 0.1],
                 [0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0]]

bishop_scores = [[0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0],
                 [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                 [0.2, 0.4, 0.5, 0.6, 0.6, 0.5, 0.4, 0.2],
                 [0.2, 0.5, 0.5, 0.6, 0.6, 0.5, 0.5, 0.2],
                 [0.2, 0.4, 0.6, 0.6, 0.6, 0.6, 0.4, 0.2],
                 [0.2, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.2],
                 [0.2, 0.5, 0.4, 0.4, 0.4, 0.4, 0.5, 0.2],
                 [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0]]

rook_scores = [[0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
               [0.5, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.5],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.25, 0.25, 0.25, 0.5, 0.5, 0.25, 0.25, 0.25]]

queen_scores = [[0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0],
                [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                [0.3, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                [0.4, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                [0.2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0]]

pawn_scores = [[0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
               [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
               [0.3, 0.3, 0.4, 0.5, 0.5, 0.4, 0.3, 0.3],
               [0.25, 0.25, 0.3, 0.45, 0.45, 0.3, 0.25, 0.25],
               [0.2, 0.2, 0.2, 0.4, 0.4, 0.2, 0.2, 0.2],
               [0.25, 0.15, 0.1, 0.2, 0.2, 0.1, 0.15, 0.25],
               [0.25, 0.3, 0.3, 0.0, 0.0, 0.3, 0.3, 0.25],
               [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]]

piece_position_scores = {"wN": knight_scores,
                         "bN": knight_scores[::-1],
                         "wB": bishop_scores,
                         "bB": bishop_scores[::-1],
                         "wQ": queen_scores,
                         "bQ": queen_scores[::-1],
                         "wR": rook_scores,
                         "bR": rook_scores[::-1],
                         "wp": pawn_scores,
                         "bp": pawn_scores[::-1]}

CHECKMATE = 100000
STALEMATE = 0
DEPTH = 3
TIME_LIMIT_SECONDS = 2.0
QUIESCENCE_DEPTH = 4
MAX_TRANSPOSITION_ENTRIES = 50000

EXACT = "exact"
LOWER_BOUND = "lower"
UPPER_BOUND = "upper"

next_move = None
search_deadline = None
search_timed_out = False
transposition_table = {}


@dataclass(frozen=True)
class DifficultySettings:
    name: str
    max_depth: int
    time_limit: float
    use_opening_book: bool = True
    use_quiescence: bool = True
    use_transposition_table: bool = True
    random_move_chance: float = 0.0


DIFFICULTY_SETTINGS = {
    "easy": DifficultySettings("easy", max_depth=1, time_limit=0.25,
                               use_opening_book=False, use_quiescence=False,
                               use_transposition_table=False, random_move_chance=0.35),
    "medium": DifficultySettings("medium", max_depth=3, time_limit=1.0,
                                 use_quiescence=True, use_transposition_table=True,
                                 random_move_chance=0.05),
    "hard": DifficultySettings("hard", max_depth=5, time_limit=TIME_LIMIT_SECONDS,
                               use_quiescence=True, use_transposition_table=True),
}


def getDifficultySettings(difficulty="hard"):
    """Return normalized settings for a difficulty name or existing settings object."""
    if isinstance(difficulty, DifficultySettings):
        return difficulty
    return DIFFICULTY_SETTINGS.get(str(difficulty).lower(), DIFFICULTY_SETTINGS["hard"])


def findBestMove(gs, valid_moves, return_queue=None, difficulty="hard"):
    """Find the best move and optionally place it into a multiprocessing queue."""
    settings = getDifficultySettings(difficulty)

    if not valid_moves:
        best_move = None
    elif random.random() < settings.random_move_chance:
        best_move = findRandomMove(valid_moves)
    else:
        best_move = None
        if settings.use_opening_book:
            best_move = OpeningBook.get_book_move(gs, valid_moves)
        if best_move is None:
            best_move = iterativeDeepening(gs, valid_moves, settings)
        if best_move is None:
            best_move = orderMoves(gs, valid_moves)[0]

    if return_queue is not None:
        return_queue.put(best_move)
    return best_move


def iterativeDeepening(gs, valid_moves, settings=None):
    """Use time-limited iterative deepening and return the best completed move."""
    global next_move, search_deadline, search_timed_out, transposition_table
    settings = getDifficultySettings(settings or "hard")
    next_move = None
    search_timed_out = False
    search_deadline = time.monotonic() + settings.time_limit
    if not settings.use_transposition_table:
        transposition_table = {}
    elif len(transposition_table) > MAX_TRANSPOSITION_ENTRIES:
        transposition_table = {}

    best_completed_move = orderMoves(gs, valid_moves)[0] if valid_moves else None
    turn_multiplier = 1 if gs.whiteToMove else -1

    for depth in range(1, settings.max_depth + 1):
        if isTimedOut():
            break
        next_move = None
        findMoveNegMaxAlphaBeta(gs, valid_moves, depth, -CHECKMATE, CHECKMATE,
                                turn_multiplier, settings, ply=0)
        if search_timed_out:
            break
        if next_move is not None:
            best_completed_move = next_move

    return best_completed_move


def findMoveNegMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turn_multiplier, settings=None, ply=0):
    """Negamax search with alpha-beta pruning, move ordering, and TT lookup."""
    global next_move, search_timed_out
    settings = getDifficultySettings(settings or "hard")

    if isTimedOut():
        search_timed_out = True
        return 0

    alpha_original = alpha
    board_key = getBoardKey(gs)
    table_entry = transposition_table.get(board_key) if settings.use_transposition_table else None
    if table_entry and table_entry["depth"] >= depth:
        if table_entry["flag"] == EXACT:
            if ply == 0:
                next_move = findMoveByNotation(validMoves, table_entry.get("move"))
            return table_entry["score"]
        if table_entry["flag"] == LOWER_BOUND:
            alpha = max(alpha, table_entry["score"])
        elif table_entry["flag"] == UPPER_BOUND:
            beta = min(beta, table_entry["score"])
        if alpha >= beta:
            return table_entry["score"]

    if depth == 0:
        if settings.use_quiescence:
            return quiescenceSearch(gs, alpha, beta, turn_multiplier, settings, QUIESCENCE_DEPTH)
        return turn_multiplier * scoreBoard(gs)

    if not validMoves:
        return turn_multiplier * scoreBoard(gs)

    max_score = -CHECKMATE
    best_move = None
    ordered_moves = orderMoves(gs, validMoves)

    for move in ordered_moves:
        gs.makeMove(move)
        next_moves = gs.getValidMoves()
        score = -findMoveNegMaxAlphaBeta(gs, next_moves, depth - 1, -beta, -alpha,
                                         -turn_multiplier, settings, ply + 1)
        gs.undoMove()

        if search_timed_out:
            return 0
        if score > max_score:
            max_score = score
            best_move = move
            if ply == 0:
                next_move = move
        alpha = max(alpha, max_score)
        if alpha >= beta:
            break

    if settings.use_transposition_table and not search_timed_out:
        flag = EXACT
        if max_score <= alpha_original:
            flag = UPPER_BOUND
        elif max_score >= beta:
            flag = LOWER_BOUND
        storeTransposition(board_key, depth, max_score, flag, best_move)

    return max_score


def quiescenceSearch(gs, alpha, beta, turn_multiplier, settings, remaining_depth):
    """Search only tactical capture/promotion continuations at leaf nodes."""
    global search_timed_out
    if isTimedOut():
        search_timed_out = True
        return 0

    stand_pat = turn_multiplier * scoreBoard(gs)
    if stand_pat >= beta:
        return beta
    alpha = max(alpha, stand_pat)
    if remaining_depth == 0:
        return stand_pat

    noisy_moves = [move for move in gs.getValidMoves() if isNoisyMove(move)]
    for move in orderMoves(gs, noisy_moves):
        gs.makeMove(move)
        score = -quiescenceSearch(gs, -beta, -alpha, -turn_multiplier, settings, remaining_depth - 1)
        gs.undoMove()
        if search_timed_out:
            return 0
        if score >= beta:
            return beta
        alpha = max(alpha, score)
    return alpha


def orderMoves(gs, moves):
    """Order likely strong moves first to improve alpha-beta pruning."""
    return sorted(moves, key=lambda move: scoreMove(gs, move), reverse=True)


def scoreMove(gs, move):
    score = 0
    if move.pieceCaptured != "--":
        score += 100 + 10 * getPieceValue(move.pieceCaptured[1]) - getPieceValue(move.pieceMoved[1])
    if move.isPawnPromotion:
        score += 90
    if move.isCastleMove:
        score += 25
    if givesCheck(gs, move):
        score += 40
    # Prefer developing pieces toward the center as a quiet-move tie breaker.
    score += centerBonus(move.endRow, move.endCol)
    return score


def isNoisyMove(move):
    return move.pieceCaptured != "--" or move.isPawnPromotion


def givesCheck(gs, move):
    gs.makeMove(move)
    in_check = gs.inCheck()
    gs.undoMove()
    return in_check


def centerBonus(row, col):
    return 3.5 - (abs(3.5 - row) + abs(3.5 - col)) / 2


def scoreBoard(gs):
    """Return a positive score for white advantage and negative for black."""
    if gs.checkMate:
        return -CHECKMATE if gs.whiteToMove else CHECKMATE
    if gs.staleMate:
        return STALEMATE

    return (evaluateMaterialAndPosition(gs)
            + evaluatePawnStructure(gs)
            + evaluateKingSafety(gs)
            + evaluateMobility(gs))


def basicScore(gs):
    """Backward-compatible name for material and piece-square evaluation."""
    return evaluateMaterialAndPosition(gs)


def evaluateMaterialAndPosition(gs):
    score = 0
    for row in range(8):
        for col in range(8):
            piece = gs.board[row][col]
            if piece == "--":
                continue
            piece_value = getPieceValue(piece[1])
            positional_value = piece_position_scores.get(piece, [[0] * 8 for _ in range(8)])[row][col]
            value = piece_value + positional_value
            score += value if piece[0] == "w" else -value
    return score


def evaluateMobility(gs):
    current_turn = gs.whiteToMove
    white_mobility = pseudoLegalMobility(gs, "w")
    black_mobility = pseudoLegalMobility(gs, "b")
    gs.whiteToMove = current_turn
    return 0.03 * (white_mobility - black_mobility)


def pseudoLegalMobility(gs, color):
    old_turn = gs.whiteToMove
    gs.whiteToMove = color == "w"
    mobility = len(gs.getAllPossibleMoves())
    gs.whiteToMove = old_turn
    return mobility


def evaluateKingSafety(gs):
    score = 0
    score += kingSafetyForColor(gs, "w", gs.whiteKingLocation)
    score -= kingSafetyForColor(gs, "b", gs.blackKingLocation)
    return score


def kingSafetyForColor(gs, color, king_location):
    row, col = king_location
    safety = 0
    home_row = 7 if color == "w" else 0
    pawn_direction = -1 if color == "w" else 1

    if row == home_row and col in (1, 2, 6):
        safety += 0.35  # castled or tucked toward a castled square
    if row != home_row:
        safety -= 0.15

    shield_row = row + pawn_direction
    if 0 <= shield_row < 8:
        for shield_col in (col - 1, col, col + 1):
            if 0 <= shield_col < 8:
                safety += 0.12 if gs.board[shield_row][shield_col] == color + "p" else -0.06
    return safety


def evaluatePawnStructure(gs):
    score = 0
    for color in ("w", "b"):
        pawns_by_file = [[] for _ in range(8)]
        enemy_pawns = []
        for row in range(8):
            for col in range(8):
                piece = gs.board[row][col]
                if piece == color + "p":
                    pawns_by_file[col].append(row)
                elif piece != "--" and piece[0] != color and piece[1] == "p":
                    enemy_pawns.append((row, col))

        color_score = 0
        for file_index, rows in enumerate(pawns_by_file):
            if len(rows) > 1:
                color_score -= 0.15 * (len(rows) - 1)
            for row in rows:
                adjacent_has_pawn = any(
                    0 <= adj_file < 8 and pawns_by_file[adj_file]
                    for adj_file in (file_index - 1, file_index + 1)
                )
                if not adjacent_has_pawn:
                    color_score -= 0.12
                if isPassedPawn(row, file_index, color, enemy_pawns):
                    advancement = (6 - row) if color == "w" else (row - 1)
                    color_score += 0.2 + max(0, advancement) * 0.08
        score += color_score if color == "w" else -color_score
    return score


def isPassedPawn(row, col, color, enemy_pawns):
    for enemy_row, enemy_col in enemy_pawns:
        if abs(enemy_col - col) > 1:
            continue
        if color == "w" and enemy_row < row:
            return False
        if color == "b" and enemy_row > row:
            return False
    return True


def getBoardKey(gs):
    rights = gs.currentCastlingRights
    return (tuple(tuple(row) for row in gs.board),
            gs.whiteToMove,
            gs.enpassantPossible,
            rights.wks, rights.bks, rights.wqs, rights.bqs)


def storeTransposition(board_key, depth, score, flag, move):
    if len(transposition_table) > MAX_TRANSPOSITION_ENTRIES:
        transposition_table.clear()
    transposition_table[board_key] = {
        "depth": depth,
        "score": score,
        "flag": flag,
        "move": move.getChessNotation() if move is not None else None,
    }


def findMoveByNotation(moves, notation):
    if notation is None:
        return None
    for move in moves:
        if move.getChessNotation() == notation:
            return move
    return None


def isTimedOut():
    return search_deadline is not None and time.monotonic() >= search_deadline


def findRandomMove(validMoves):
    """Picks and returns a random valid move."""
    return random.choice(validMoves)


def getPieceValue(pieceType):
    """Return the value of the piece based on its type."""
    return piece_score.get(pieceType, 0)
