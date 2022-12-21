"""
Main - user input, GameState
"""

import pygame as p
import ChessEngine

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


def drawBoardConsole():
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            print("--")


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPiecesConsole(board):
    pass


def drawText(screen, text):
    # color = ('#FFFFFF')
    # p.draw.rect(screen, color, p.Rect(300, 300, 200, 200))
    font = p.font.SysFont("Arial", 60, True, True)
    textObject = font.render(text, True, p.Color('Black'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textObject.get_width() / 2,
                                                    HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)


def main_pygame():
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
    while running:
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
                    if len(playerClicks) == 2:
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
                if e.key == p.K_r:  # complete reset on r press
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

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


def main_console():
    pass



if __name__ == "__main__":
    print("Choose app type:")
    print("  1. Console.")
    print("  2. Visual.")

    choice = input()
    if choice == '1':
        main_pygame()
    elif choice == '2':
        main_console()
    else:
        print("Invalid choice.")
