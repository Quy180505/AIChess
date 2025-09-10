import random


pieceScore = {
    "K": 1000, "Q": 9, "R": 6, "B": 3, "N": 3, "p": 1
}


def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)] if validMoves else None

def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square == "--":
                continue
            side, piece = square[0], square[1]
            val = pieceScore.get(piece, 0)
            if side == 'w':
                score += val
            else:
                score -= val
    return score


def checkStateGame(gs):
    if gs.checkMate:
        return "Black wins" if gs.whiteToMove else "White wins"
    elif gs.staleMate:
        return "Draw"
    else:
        return "Next"


MATE_SCORE = 99999

def findGreedyMove(gs, validMoves):
    bestMove = None
    maxScore = -float('inf')
    for move in validMoves:
        gs.makeMove(move)
        score = scoreMaterial(gs.board)
        if score > maxScore:
            maxScore = score
            bestMove = move
        gs.undoMove()

    else:
        minScore = float('inf')
        for move in validMoves:
            gs.makeMove(move)
            score = scoreMaterial(gs.board)
            if score < minScore:
                minScore = score
                bestMove = move
            gs.undoMove()
    return bestMove





def terminal_eval(gs, depth):
    if gs.checkMate:
        return True, (-MATE_SCORE if gs.whiteToMove else MATE_SCORE)
    if gs.staleMate:
        return True, 0
    if depth == 0:
        return True, scoreMaterial(gs.board)
    return False, 0

def minmax(gs, depth, isMaximizingPlayer):
    is_term, val = terminal_eval(gs, depth)
    if is_term:
        return val
    validMoves = gs.getValidMoves()
    if not validMoves:
        return scoreMaterial(gs.board)
    if isMaximizingPlayer:
        bestVal = -float('inf')
        for move in validMoves:
            gs.makeMove(move)
            childVal = minmax(gs, depth - 1, False)
            gs.undoMove()
            if childVal > bestVal:
                bestVal = childVal
        return bestVal
    else:
        bestVal = float('inf')
        for move in validMoves:
            gs.makeMove(move)
            childVal = minmax(gs, depth - 1, True)
            gs.undoMove()
            if childVal < bestVal:
                bestVal = childVal
        return bestVal


def findBestMoveMinmax(gs, validMoves, depth):
    if not validMoves:
        return None
    bestMove = findRandomMove(validMoves)
    if gs.whiteToMove:
        bestEval = -float('inf')
        for move in validMoves:
            gs.makeMove(move)
            eval_val = minmax(gs, depth - 1, False)
            gs.undoMove()
            if eval_val > bestEval:
                bestEval = eval_val
                bestMove = move
    else:
        bestEval = float('inf')
        for move in validMoves:
            gs.makeMove(move)
            eval_val = minmax(gs, depth - 1, True)
            gs.undoMove()
            if eval_val < bestEval:
                bestEval = eval_val
                bestMove = move

    return bestMove
