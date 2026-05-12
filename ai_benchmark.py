"""Simple command-line benchmark for the chess AI."""
import time

import BlupAI as AI
import ChessEngine


def run_position(name, setup=None, difficulty="medium"):
    gs = ChessEngine.GameState()
    if setup is not None:
        setup(gs)
    valid_moves = gs.getValidMoves()
    start = time.monotonic()
    move = AI.findBestMove(gs, valid_moves, difficulty=difficulty)
    elapsed = time.monotonic() - start
    notation = move.getChessNotation() if move is not None else "none"
    print(f"{name}: {notation} in {elapsed:.3f}s ({len(valid_moves)} legal moves)")


def main():
    run_position("Initial position", difficulty="medium")


if __name__ == "__main__":
    main()
