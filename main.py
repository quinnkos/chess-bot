import chess
import chess.polyglot
import random
import time
import cProfile

import PSTs

board = chess.Board()
searchDepth = 4
transpositionTable = {}
whitePSTs, blackPSTs, pieceValues = PSTs.whitePSTs, PSTs.blackPSTs, PSTs.pieceValues

piece_to_index = {
    chess.PAWN: 0,
    chess.KNIGHT: 1,
    chess.BISHOP: 2,
    chess.ROOK: 3,
    chess.QUEEN: 4,
    chess.KING: 5
}

openingBook = chess.polyglot.open_reader("codekiddy.bin")
    
def evaluate(board) -> int:
    
    if board.result() == "1-0":
        return 9999
    elif board.result() == "0-1":
        return -9999
    elif board.result() == "1/2-1/2":
        return 0

    zobrist_key = chess.polyglot.zobrist_hash(board)
    if zobrist_key in transpositionTable:
        return transpositionTable[zobrist_key]
    
    whiteEvalScore, blackEvalScore, whitePSTScore, blackPSTScore = 0, 0, 0, 0
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if not piece:
            continue
        else: #piece found on square          
            if piece.color == chess.WHITE:
                whiteEvalScore += pieceValues[piece.piece_type] #piece value
            else:
                blackEvalScore += pieceValues[piece.piece_type]
    
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if not piece:
            continue
        else:
            if piece.color == chess.WHITE:
                if piece.piece_type == chess.KING and blackEvalScore <= pieceValues[chess.KING] + 2000:
                    whitePSTScore += whitePSTs[piece.piece_type][square] #adjusted value depending on square (king in endgame)
                else:
                    whitePSTScore += whitePSTs[piece.piece_type-1][square] #adjusted value depending on square
            else:
                if piece.piece_type == chess.KING and whiteEvalScore <= pieceValues[chess.KING] + 2000:
                    blackPSTScore += blackPSTs[piece.piece_type][square]
                else:
                    blackPSTScore += blackPSTs[piece.piece_type-1][square]
    
    
    staticEval = ((whiteEvalScore+whitePSTScore)-(blackEvalScore+blackPSTScore))
    return staticEval


def mvv_lva(move):
    victimValue = pieceValues.get(board.piece_type_at(move.to_square), 0)
    attackerValue = pieceValues.get(board.piece_type_at(move.from_square), 0)
    return victimValue - attackerValue


def quiescence(depth, legalMoves, alpha, beta) -> int:

    zobrist_key = chess.polyglot.zobrist_hash(board)
    if zobrist_key in transpositionTable:
        return transpositionTable[zobrist_key]

    standPat = evaluate(board)
    
    if depth == 0:
        return standPat

    if standPat >= beta:
        return beta
    if standPat > alpha:
        alpha = standPat

    captureMoves = [move for move in board.legal_moves if board.is_capture(move)]
    captureMoves.sort(key=mvv_lva, reverse=True)

    for child in captureMoves:
        if board.is_capture(child):
            board.push(child)
            childEval = -quiescence(depth-1, legalMoves, -beta, -alpha)
            board.pop()

            if childEval >= beta:
                return beta
            if childEval > alpha:
                alpha = childEval

    transpositionTable[zobrist_key] = alpha
    return alpha
    

def minimax(depth, legalMoves, alpha, beta, isMaximizingPlayer, isHighestDepth) -> tuple[int, any]:

    zobrist_key = chess.polyglot.zobrist_hash(board)
    if not isHighestDepth and zobrist_key in transpositionTable:
        return transpositionTable[zobrist_key], None
        
    if depth == 0 or board.is_game_over():
        return evaluate(board), None 
        #return quiescence(2, legalMoves, alpha, beta), None

    legalMoves = sorted(legalMoves, key=lambda move: (board.is_capture(move), board.gives_check(move), mvv_lva(move)), reverse=True)
    
    if isMaximizingPlayer: #white
        maxEval = -9999
        for i, child in enumerate(legalMoves):
            board.push(child)

            if i > 3 and depth > 2 and not board.is_capture(child) and not board.gives_check(child) and not board.is_check():
                childEval, _ = minimax(depth - 2, list(board.legal_moves), alpha, beta, False, False)
            else:
                childEval, _ = minimax(depth - 1, list(board.legal_moves), alpha, beta, False, False)

            
            board.pop()
            maxEval = max(maxEval, childEval)
            alpha = max(alpha, childEval)
            if beta <= alpha:
                break
        transpositionTable[zobrist_key] = maxEval
        #print(maxEval, depth)
        return maxEval, None
    
    else: #black
        
        minEval = 9999
        bestMove = legalMoves[0]
        for i, child in enumerate(legalMoves):
            board.push(child)

            if i > 3 and depth > 2 and not board.is_capture(child) and not board.gives_check(child) and not board.is_check():
                childEval, _ = minimax(depth - 2, list(board.legal_moves), alpha, beta, True, False)
            else:
                childEval, _ = minimax(depth - 1, list(board.legal_moves), alpha, beta, True, False)
                
            board.pop()
            if childEval < minEval:
                minEval = childEval
                bestMove = child
            beta = min(beta, childEval)
            if beta <= alpha:
                break
        transpositionTable[zobrist_key] = minEval
        #print(minEval, depth, bestMove if isHighestDepth else None)
        return minEval, bestMove


def prelimSearch(legalMoves, alpha, beta) -> dict:

    evalList = {}
    for child in legalMoves:
        board.push(child)
        childEval = evaluate(board)
        beta = min(beta, childEval)
        board.pop()
        evalList[child] = childEval
        if beta <= alpha:
            break
    #evalList = dict(sorted(evalList.items(), key=lambda item: item[1]))
    return evalList
    

def main():

    #User's move
    move = input()
    try: 
        board.push_san(move)
    except ValueError:
        print("Invalid move.")
        main()
    print(board)

    if board.is_game_over():
        print(board.result())
        return
        
    elif board.ply() % 2 == 1:

        try: #Engine uses opening book
            responseUCI = openingBook.weighted_choice(board)[-1]
        except IndexError: #Engine evaluates position
            heuristicEvals = prelimSearch(list(board.legal_moves), -9999, 9999)
            sortedLegalMoves = dict(sorted(heuristicEvals.items(), key=lambda item: item[1]))
            sortedLegalMoves = list(sortedLegalMoves.keys())
            start = time.time()
            _, responseUCI = minimax(searchDepth, sortedLegalMoves, -9999, 9999, False, True)
            print("Elapsed: " + str(time.time() - start))
        board.push_san(str(responseUCI))
        #except: print("problematic UCI: '" + str(responseUCI) + "' of type: " + str(type(responseUCI)))
        print('"' + str(responseUCI) + '"')
        print(board)
        #gui.draw(str(board))

    if not board.is_game_over():
        main()
    else:
        print(board.result())

print(board)
#gui.draw(str(board))

if __name__ == "__main__":
    main()
