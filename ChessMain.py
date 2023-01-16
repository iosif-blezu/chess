"""
Main - user input, GameState
"""

import pygame as p
import ChessEngine
import BlupAI as AI
from multiprocessing import Process, Queue

WIDTH = HEIGHT = 720
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 14
IMAGES = {}


def loadImages():  # load images
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']  # piece names
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def highlightSquares(screen, gs, valid_moves, sq_selected):
    if sq_selected != ():
        r, c = sq_selected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):  # selects a piece that can be moved
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # val. transparency
            s.fill(p.Color('light blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            s.fill(p.Color('light blue'))
            for move in valid_moves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (SQ_SIZE * move.endCol, move.endRow * SQ_SIZE))


def drawGameState(screen, gs, valid_moves, sq_selected):
    drawBoard(screen)  # draws board
    highlightSquares(screen, gs, valid_moves, sq_selected)
    drawPieces(screen, gs.board)  # draws pieces


def drawBoard(screen):  # draws board
    colors = [p.Color("#EFEFEF"), p.Color("#8877B7")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawText(screen, text):
    # color = ('#FFFFFF')
    # p.draw.rect(screen, color, p.Rect(300, 300, 200, 200))
    font = p.font.SysFont("Arial", 60, True, True)
    textObject = font.render(text, True, p.Color('Black'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textObject.get_width() / 2,
                                                    HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)


def main_pygame():
    global return_queue
    p.init()
    p.mixer.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    p.display.set_caption('BLUP Chess Engine')

    Icon = p.image.load("Prefabs/blogo.jpg")

    p.display.set_icon(Icon)
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False  # when move made - flag type variable
    moveSound = p.mixer.Sound('sfx/Move.wav')
    checkSound = p.mixer.Sound('sfx/Check.wav')
    captureSound = p.mixer.Sound('sfx/Capture.wav')

    loadImages()
    running = True
    sqSelected = ()  # remembers last click - row, col
    playerClicks = []  # all clicks
    gameOver = False

    ai_thinking = False
    move_undone = False
    move_finder_process = None

    playerOne = True   # if a human is playing white
    playerTwo = False  # if human is playing black

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()  # mouse coordinates
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col):  # click on the same square 2 times
                        sqSelected = ()  # reset
                        playerClicks = []  # reset
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)  # append for the first and second clicks
                    if len(playerClicks) == 2 and humanTurn:  # after 2nd click
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        pcCounter = gs.pieceCounter()
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                if gs.inCheck():
                                    checkSound.play()
                                else:
                                    if gs.pieceCounter() < pcCounter:
                                        captureSound.play()
                                    else:
                                        moveSound.play()
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo on z press
                    gs.undoMove()
                    moveMade = True
                    gameOver = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True
                if e.key == p.K_r:  # complete reset on r press
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    gameOver = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True

        if not gameOver and not humanTurn and not move_undone:
            if not ai_thinking:
                ai_thinking = True
                return_queue = Queue()
                move_finder_process = Process(target=AI.findBestMove, args=(gs, validMoves, return_queue))
                move_finder_process.start()

            if not move_finder_process.is_alive():
                ai_move = return_queue.get()
                if ai_move is None:
                    ai_move = AI.findRandomMove(validMoves)
                gs.makeMove(ai_move)
                moveMade = True
                ai_thinking = False
        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False
            move_undone = False

        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, 'Black wins by checkmate')
            else:
                drawText(screen, 'White wins by checkmate')
        elif gs.staleMate:
            gameOver = True
            drawText(screen, 'Stalemate')

        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameStateConsole(gs):
    drawBoardConsole(gs)  # draws board


def drawBoardConsole(gs):
    for r in range(DIMENSION):
        print(gs.board[r])


def main_console():
    global return_queue
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False  # when move made - flag type variable

    running = True
    gameOver = False

    drawGameStateConsole(gs)

    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}

    ai_thinking = False
    move_undone = False
    move_finder_process = None

    playerOne = True  # if a human is playing white
    playerTwo = False  # if human is playing black

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        command = input("Enter command: ")
        if len(command) == 4:
            if not gameOver and humanTurn:
                if command == 'z':  # undo on z press
                    gs.undoMove()
                    moveMade = True
                elif command == 'r':  # complete reset on r press
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    moveMade = False

                elif command == 'q':
                    running = False

                else:
                    start_col = command[0]
                    start_row = command[1]
                    end_col = command[2]
                    end_row = command[3]
                    start = (ranksToRows[start_row], filesToCols[start_col])
                    end = (ranksToRows[end_row], filesToCols[end_col])
                    move = ChessEngine.Move(start, end, gs.board)
                    print(move.getChessNotation())
                    # pcCounter = gs.pieceCounter()
                    for i in range(len(validMoves)):
                        if move == validMoves[i]:
                            gs.makeMove(validMoves[i])
                            moveMade = True
                            if gs.inCheck():
                                print("Check")

            if not gameOver and not humanTurn and not move_undone:
                if not ai_thinking:
                    ai_thinking = True
                    return_queue = Queue()
                    move_finder_process = Process(target=AI.findBestMove, args=(gs, validMoves, return_queue))
                    move_finder_process.start()

                if not move_finder_process.is_alive():
                    ai_move = return_queue.get()
                    if ai_move is None:
                        ai_move = AI.findRandomMove(validMoves)
                    gs.makeMove(ai_move)
                    moveMade = True
                    ai_thinking = False

            if moveMade:
                validMoves = gs.getValidMoves()
                moveMade = False
                move_undone = False

            drawGameStateConsole(gs)

            if gs.checkMate:
                gameOver = True
                if gs.whiteToMove:
                    print('Black wins by checkmate')
                else:
                    print('White wins by checkmate')
            elif gs.staleMate:
                gameOver = True
                print('Stalemate')
        else:
            print("Invalid command")


if __name__ == "__main__":
    print("Choose app type:")
    print("  1. Console.")
    print("  2. Visual.")

    choice = input()
    if choice == '1':
        main_console()
    elif choice == '2':
        main_pygame()
    else:
        print("Invalid choice.")
