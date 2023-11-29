import chess
import chess.polyglot
#import chess.pgn
#import numpy as np
#from tkinter import *

'''wn = Tk()
wn.title('Chess Bot')
wn.geometry('600x600')
wn.config(bg='darkgray')
chessBoard = Canvas(wn, width=400, height=400, bg='beige', highlightthickness=0)
chessBoard.place(x=100, y=100)

for row in range(4):
    for col in range(4):
        chessBoard.create_rectangle(row*100+50, col*100, row*100+100, col*100+50, fill='brown', outline='black')
        chessBoard.create_rectangle(row*100, col*100+50, row*100+50, col*100+100, fill='brown', outline='black')'''

board = chess.Board()
print(board)

reader = chess.polyglot.open_reader("/Users/ndkoster/Downloads/polyglot-collection/codekiddy.bin")

pgn = ""
fensAnalyzed, count = {}, 0


def main():

    global pgn

    move = input()
    board.push_san(move)
    pgn += "".join([str((board.ply()/2)+.5)[:-2], ". %s " % move])
    print(board)

    if board.is_game_over():
        print(board.result())
        pgn += "*"
        print(pgn)
        return

    '''game = chess.pgn.Game()
    node = game
    node = node.add_variation(move)
    print(game)'''
    
    searchDepth = 4


    def minimax(depth, legalMoves, alpha, beta, maximizingPlayer, isHighestDepth, isPrelim):

        global fensAnalyzed, count

        if depth == 0 or board.is_game_over():

            #if not isPrelim:
                #count += 1

            if board.fen() in fensAnalyzed:
                return fensAnalyzed[board.fen()]

            if board.result() == "1-0":
                return 9999*searchDepth
            elif board.result() == "0-1":
                return -9999*searchDepth
            elif board.result() == "1/2-1/2":
                return 0

            whiteEvalScore, blackEvalScore, whitePSTScore, blackPSTScore = 0, 0, 0, 0

            pieceValues = {
                chess.PAWN: 100, #Idx 1
                chess.ROOK: 500, #4
                chess.KNIGHT: 320, #2
                chess.BISHOP: 330, #3
                chess.QUEEN: 900, #5
                chess.KING: 20000 #6
            }

            whitePSTs = [ #https://www.chessprogramming.org/Simplified_Evaluation_Function check if same

                #Pawn
                [0,  0,  0,  0,  0,  0,  0,  0,
                5, 10, 10,-25,-25, 10, 10,  5,
                5, -5,-10,  0,  0,-10, -5,  5,
                0,  0,  0, 25, 25,  0,  0,  0,
                5,  5, 10, 27, 27, 10,  5,  5,
                10, 10, 20, 30, 30, 20, 10, 10,
                50, 50, 50, 50, 50, 50, 50, 50,
                0,  0,  0,  0,  0,  0,  0,  0],

                #Knight
                [-50,-40,-30,-30,-30,-30,-40,-50,
                 -40,-20,  0,  0,  0,  0,-20,-40,
                 -30,  0, 10, 15, 15, 10,  0,-30,
                -30,  5, 15, 20, 20, 15,  5,-30,
                -30,  0, 15, 20, 20, 15,  0,-30,
                -30,  5, 10, 15, 15, 10,  5,-30,
                -40,-20,  0,  5,  5,  0,-20,-40,
                -50,-40,-20,-30,-30,-20,-40,-50],

                #Bishop
                [-20,-10,-40,-10,-10,-40,-10,-20,
                -10,  5,  0,  0,  0,  0,  5,-10,
                -10, 10, 10, 10, 10, 10, 10,-10,
                -10,  0, 10, 10, 10, 10,  0,-10,
                -10,  5,  5, 10, 10,  5,  5,-10,
                -10,  0,  5, 10, 10,  5,  0,-10,
                -10,  0,  0,  0,  0,  0,  0,-10,
                -20,-10,-10,-10,-10,-10,-10,-20],

                #Rook
                [0,  0,  0,  5,  5,  0,  0,  0,
                -5,  0,  0,  0,  0,  0,  0, -5,
                -5,  0,  0,  0,  0,  0,  0, -5,
                -5,  0,  0,  0,  0,  0,  0, -5,
                -5,  0,  0,  0,  0,  0,  0, -5,
                -5,  0,  0,  0,  0,  0,  0, -5,
                5, 10, 10, 10, 10, 10, 10,  5,
                0,  0,  0,  0,  0,  0,  0,  0],

                #Queen
                [-20,-10,-10, -5, -5,-10,-10,-20,
                -10,  0,  0,  0,  0,  0,  0,-10,
                -10,  5,  5,  5,  5,  5,  0,-10,
                 0,  0,  5,  5,  5,  5,  0, -5,
                -5,  0,  5,  5,  5,  5,  0, -5,
                -10,  0,  5,  5,  5,  5,  0,-10,
                -10,  0,  0,  0,  0,  0,  0,-10,
                -20,-10,-10, -5, -5,-10,-10,-20],

                #King
                [20,  30,  10,   0,   0,  10,  30,  20,
                20,  20,   0,   0,   0,   0,  20,  20,
                -10, -20, -20, -20, -20, -20, -20, -10,
                -20, -30, -30, -40, -40, -30, -30, -20,
                -30, -40, -40, -50, -50, -40, -40, -30,
                -30, -40, -40, -50, -50, -40, -40, -30,
                -30, -40, -40, -50, -50, -40, -40, -30,
                -30, -40, -40, -50, -50, -40, -40, -30],

                #King (endgame)
                [-50,-30,-30,-30,-30,-30,-30,-50,
                -30,-30,  0,  0,  0,  0,-30,-30,
                -30,-10, 20, 30, 30, 20,-10,-30,
                -30,-10, 30, 40, 40, 30,-10,-30,
                -30,-10, 30, 40, 40, 30,-10,-30,
                -30,-10, 20, 30, 30, 20,-10,-30,
                -30,-20,-10,  0,  0,-10,-20,-30,
                -50,-40,-30,-20,-20,-30,-40,-50]

            ]

            blackPSTs = [

                #Pawn
                [0,  0,  0,  0,  0,  0,  0,  0,
                50, 50, 50, 50, 50, 50, 50, 50,
                10, 10, 20, 30, 30, 20, 10, 10,
                5,  5, 10, 27, 27, 10,  5,  5,
                0,  0,  0, 25, 25,  0,  0,  0,
                5, -5,-10,  0,  0,-10, -5,  5,
                5, 10, 10,-25,-25, 10, 10,  5,
                0,  0,  0,  0,  0,  0,  0,  0],

                #Knight
                [-50,-40,-30,-30,-30,-30,-40,-50,
                -40,-20,  0,  0,  0,  0,-20,-40,
                -30,  0, 10, 15, 15, 10,  0,-30,
                -30,  5, 15, 20, 20, 15,  5,-30,
                -30,  0, 15, 20, 20, 15,  0,-30,
                -30,  5, 10, 15, 15, 10,  5,-30,
                -40,-20,  0,  5,  5,  0,-20,-40,
                -50,-40,-20,-30,-30,-20,-40,-50],

                #Bishop
                [-20,-10,-10,-10,-10,-10,-10,-20,
                -10,  0,  0,  0,  0,  0,  0,-10,
                -10,  0,  5, 10, 10,  5,  0,-10,
                -10,  5,  5, 10, 10,  5,  5,-10,
                -10,  0, 10, 10, 10, 10,  0,-10,
                -10, 10, 10, 10, 10, 10, 10,-10,
                -10,  5,  0,  0,  0,  0,  5,-10,
                -20,-10,-40,-10,-10,-40,-10,-20],

                #Rook
                [0,  0,  0,  0,  0,  0,  0,  0,
                5, 10, 10, 10, 10, 10, 10,  5,
                -5,  0,  0,  0,  0,  0,  0, -5,
                -5,  0,  0,  0,  0,  0,  0, -5,
                -5,  0,  0,  0,  0,  0,  0, -5,
                -5,  0,  0,  0,  0,  0,  0, -5,
                -5,  0,  0,  0,  0,  0,  0, -5,
                0,  0,  0,  5,  5,  0,  0,  0],

                #Queen
                [-20,-10,-10, -5, -5,-10,-10,-20,
                -10,  0,  0,  0,  0,  0,  0,-10,
                -10,  5,  5,  5,  5,  5,  0,-10,
                0,  0,  5,  5,  5,  5,  0, -5,
                -5,  0,  5,  5,  5,  5,  0, -5,
                -10,  0,  5,  5,  5,  5,  0,-10,
                -10,  0,  0,  0,  0,  0,  0,-10,
                -20,-10,-10, -5, -5,-10,-10,-20],

                #King
                [-30, -40, -40, -50, -50, -40, -40, -30,
                -30, -40, -40, -50, -50, -40, -40, -30,
                -30, -40, -40, -50, -50, -40, -40, -30,
                -30, -40, -40, -50, -50, -40, -40, -30,
                -20, -30, -30, -40, -40, -30, -30, -20,
                -10, -20, -20, -20, -20, -20, -20, -10, 
                20,  20,   0,   0,   0,   0,  20,  20,
                20,  30,  10,   0,   0,  10,  30,  20],

                #King (endgame)
                [-50,-40,-30,-20,-20,-30,-40,-50,
                -30,-20,-10,  0,  0,-10,-20,-30,
                -30,-10, 20, 30, 30, 20,-10,-30,
                -30,-10, 30, 40, 40, 30,-10,-30,
                -30,-10, 30, 40, 40, 30,-10,-30,
                -30,-10, 20, 30, 30, 20,-10,-30,
                -30,-30,  0,  0,  0,  0,-30,-30,
                -50,-30,-30,-30,-30,-30,-30,-50]

            ]

                
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
                        if piece.piece_type == chess.KING and blackEvalScore <= 22000:
                            whitePSTScore += whitePSTs[piece.piece_type][square] #adjusted value depending on square (king in endgame)
                        else:
                            whitePSTScore += whitePSTs[piece.piece_type-1][square] #adjusted value depending on square
                    else:
                        if piece.piece_type == chess.KING and whiteEvalScore <= 22000:
                            blackPSTScore += blackPSTs[piece.piece_type][square]
                        else:
                            blackPSTScore += blackPSTs[piece.piece_type-1][square]

            
            staticEval = ((whiteEvalScore+whitePSTScore)-(blackEvalScore+blackPSTScore))/100.00
            fensAnalyzed[board.fen()] = staticEval
            return staticEval        
            

        if maximizingPlayer: #white
            maxEval = float('-inf')
            for child in range(len(legalMoves)):
                board.push_san(str(legalMoves[child]))
                childEval = minimax(depth-1, list(board.legal_moves), alpha, beta, False, False, isPrelim)
                maxEval, alpha = max(maxEval, childEval), max(alpha, childEval)
                board.pop()
                if beta <= alpha:
                    break
            return maxEval

        else: #black
            minEval = float('inf')
            evalList = {}
            for child in range(len(legalMoves)):
                board.push_san(str(legalMoves[child]))
                childEval = minimax(depth-1, list(board.legal_moves), alpha, beta, True, False, isPrelim)
                minEval, beta = min(minEval, childEval), min(beta, childEval)
                board.pop()
                if isHighestDepth:
                    evalList[legalMove] = childEval
                if beta <= alpha:
                    break
            if isHighestDepth:
                #if not isPrelim:
                    #print(count)
                return evalList
            return minEval

    if board.ply() % 2 == 1:
        
        try:
            responseUCI = str(reader.weighted_choice(board)[-1])
        except:
            heuristicEvals = minimax(1, list(board.legal_moves), float('-inf'), float('inf'), False, True, True)
            sortedLegalMoves = dict(sorted(heuristicEvals.items(), key=lambda item: item[1]))
            sortedLegalMoves = list(sortedLegalMoves.keys())
            gameEvals = minimax(searchDepth, sortedLegalMoves, float('-inf'), float('inf'), False, True, False)
            #print(gameEvals)
            responseUCI = min(gameEvals, key=gameEvals.get)
            
        board.push_san(responseUCI)
        #node = node.add_variation(responseUCI)
        pgn += responseUCI + " "
        print('"' + responseUCI + '"')
        print(board)
        try:
            print(" ".join("Eval:", gameEval))
        except:
            pass
    

    if not board.is_game_over():
        main()
    else:
        print(board.result())
        pgn += "*"
        print(pgn)

        

main()
#wn.mainloop()


