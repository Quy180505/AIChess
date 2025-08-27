"""
this Class responsible for storing all the information about the current state of a chess game. It will
also be responsible for determining valid moves at current state. it will also keep a move log

"""
import copy

class gameState():
    def __init__(self):
        # hiện thực bàn cờ vua 8*8 ban đầu, chữ đầu thể hiện màu quân cờ, chữ sau thể hiện loại quân cờ
        # "--": thể hiện chỗ trống không có quân cờ
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.moveFunctions={'p':self.getPawnMove,'R':self.getRookMove,'N':self.getKnightMove,
                            'B':self.getBishopMove,'Q':self.getQueenMove,'K':self.getKingMove}
        self.whiteToMove = True
        self.moveLog = []  # ghi nhận các object Move
        self.whiteKingLocation=(7,4)
        self.blackKingLocation=(0,4)
        self.checkMate=False
        self.staleMate=False
        self.enpassantPossible=() #coordinate the square where enpassant is possible
        self.currentCastlingRight=CastleRight(True,True,True,True)
        self.castleRightsLog=[CastleRight(self.currentCastlingRight.wks,self.currentCastlingRight.bks,
                                          self.currentCastlingRight.wqs,self.currentCastlingRight.bqs)]



    def makeMove(self,move):
        self.board[move.startRow][move.startCol] ="--"
        self.board[move.endRow][move.endCol]=move.pieceMoved
        self.moveLog.append(move) #log the move for undo later
        self.whiteToMove=not self.whiteToMove #swap players
        # update king position if moved
        if move.pieceMoved=="wK":
            self.whiteKingLocation=(move.endRow,move.endCol)
        elif  move.pieceMoved=="bK":
            self.blackKingLocation=(move.endRow,move.endCol)

        #pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] +'Q'

        #enpassant
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol]='--'

        #update enpassantPossible variable
        if move.pieceMoved[1]=='p' and abs(move.startRow-move.endRow)==2: #only on 2 square pawn advanced
            self.enpassantPossible=((move.startRow+move.endRow)//2,move.startCol)
        else:
            self.enpassantPossible=()

        #castle move
        if move.isCastleMove:
            if move.endCol-move.startCol==2: #king side castle
                self.board[move.endRow][move.endCol-1]=self.board[move.endRow][move.endCol+1] #move the rook
                self.board[move.endRow][move.endCol+1]='--'#erase old rook
            else: #queen side castle
                if move.startCol - move.endCol == 2:  # queen side castle
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol -2]  # move the rook
                    self.board[move.endRow][ move.endCol -2] = '--'  # erase old rook

        #update castling right -whenever rook/king move
        self.updateCastleRight(move)
        self.castleRightsLog.append(CastleRight(self.currentCastlingRight.wks,
                                            self.currentCastlingRight.bks,
                                            self.currentCastlingRight.wqs,
                                            self.currentCastlingRight.bqs))

    #undo last move
    def undoMove(self):
        if len(self.moveLog)!= 0:
            move=self.moveLog.pop()
            self.board[move.startRow][move.startCol]=move.pieceMoved
            self.board[move.endRow][move.endCol]=move.pieceCaptured
            self.whiteToMove= not self.whiteToMove #switch turn back
            #update king position if needed
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

            #undo enpassant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol]='--' #leave landing square blank
                self.board[move.startRow][move.endCol]=move.pieceCaptured
                self.enpassantPossible=(move.endRow,move.endCol)
            #undo a 2 square pawn advance
            if move.pieceMoved[1]=='p' and abs(move.startRow-move.endRow)==2:
                self.enpassantPossible=()

            #undo castling rights

            # self.castleRightsLog.pop() #get rid of the castle rights from the move undoing
            # self.currentCastlingRight =self.castleRightsLog[-1] #set the current castle rights to the last one in the list
            # -> hai dòng trên sai trong trường hợp vừa castling thì undo ngay, nếu muốn castle lại thì phải undo cả đối thủ
            # -> cách fix: import copy và thay thế 2 dòng trên bằng 3 dòng dưới
            self.castleRightsLog.pop()
            castlerights=copy.deepcopy(self.castleRightsLog[-1])
            self.currentCastlingRight=castlerights

            #undo castle move
            if move.isCastleMove:
                if move.endCol-move.startCol==2: #king side
                    self.board[move.endRow][move.endCol+1]=self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1]='--'
                else: #queen side
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = '--'





    def updateCastleRight(self,move):
        if move.pieceMoved=='wK':
            self.currentCastlingRight.wks=False
            self.currentCastlingRight.wqs=False
        elif move.pieceMoved=='bK':
            self.currentCastlingRight.bks=False
            self.currentCastlingRight.bqs=False
        elif move.pieceMoved=="wR":
            if move.startRow==7:
                if move.startCol==0:
                    self.currentCastlingRight.wqs=False
                if move.startCol==7:
                    self.currentCastlingRight.wks=False
        elif move.pieceMoved=="bR":
            if move.startRow==0:
                if move.startCol==0:
                    self.currentCastlingRight.bqs=False
                if move.startCol==7:
                    self.currentCastlingRight.bks=False
        # if a rook is captured
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                        self.currentCastlingRight.wqs = False
                elif move.endCol == 7:
                        self.currentCastlingRight.wks = False
        elif move.pieceCaptured == 'bR':
                if move.endRow == 0:
                    if move.endCol == 0:
                        self.currentCastlingRight.bqs = False
                    elif move.endCol == 7:
                        self.currentCastlingRight.bks = False
    '''
     Determine whether player in check or not
    '''
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0],self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    '''
     Determine if the enemy can attack square r,c
    '''
    def squareUnderAttack(self,r,c):
        self.whiteToMove=not self.whiteToMove #switch to oppenent turn
        opponentMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  # switch the turn back
        for move in opponentMoves:
            if move.endRow==r and move.endCol==c: #square is under attack
                return True
        return False

    def getValidMoves(self):
        self.checkMate = False
        self.staleMate = False

        tempEnpassantPossible = self.enpassantPossible
        tempCastlingRights = CastleRight(
            self.currentCastlingRight.wks,
            self.currentCastlingRight.bks,
            self.currentCastlingRight.wqs,
            self.currentCastlingRight.bqs
        )

        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMove(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMove(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()

        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True

        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRight = tempCastlingRights
        return moves

    def getAllPossibleMoves(self):
        moves=[]
        for r in range(len(self.board)):  #numbers of rows
            for c in range(len(self.board[r])):  #number of cols in given row
                turn=self.board[r][c][0] # lấy chữ cái đầu của vị trí board[r][c] để check là black,white hay là none
                if(turn=="w" and self.whiteToMove) or (turn=="b" and not self.whiteToMove):
                    pieceType =self.board[r][c][1]  # lấy chữ cái tiếp theo  của vị trí board[r][c] để check là quân gì
                    # call appropriate move function based on the type
                    self.moveFunctions[pieceType](r,c,moves) # type: ignore

        return moves


    def getPawnMove(self,r,c,moves):
        if self.whiteToMove:
            if self.board[r-1][c]=="--":
                moves.append(Move((r,c),(r-1,c),self.board))
                if r==6 and self.board[r-2][c]=="--":
                    moves.append(Move((r,c),(r-2,c),self.board))
            if c-1>=0: #captures to the left
                if self.board[r-1][c-1][0]=='b':
                    moves.append(Move((r, c), (r - 1, c-1), self.board))
                elif (r-1,c-1)==self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board,isEnpassantMove=True))

            if c+1<=7: #capture to the right
                if self.board[r-1][c+1][0]=='b':
                    moves.append(Move((r,c),(r-1,c+1),self.board))
                elif (r - 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board,isEnpassantMove=True))
        else:
            if self.board[r +1][c] == "--":
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":
                    moves.append(Move((r, c), (r + 2, c), self.board))
            #capture
            if c-1>=0: #capture to the right
                if self.board[r+1][c-1][0]=='w':
                    moves.append(Move((r,c),(r+1,c-1),self.board))
                elif (r + 1, c - 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board,isEnpassantMove=True))

            if c+1<=7: #capture to the left
                if self.board[r+1][c+1][0]=='w':
                    moves.append(Move((r, c), (r + 1, c+1), self.board))
                elif (r + 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board,isEnpassantMove=True))

    def getRookMove(self,r,c,moves):
        directions=((-1,0),(0,-1),(1,0),(0,1))
        enemyColor="b" if self.whiteToMove else "w"
        for d in directions:
            for i in range (1,8):
                endRow=r+d[0]*i
                endCol=c+d[1]*i
                if 0<=endRow<8 and 0<=endCol<8:   #on board
                    endPiece=self.board[endRow][endCol]
                    if endPiece=="--": #empty space valid
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    elif endPiece[0]==enemyColor:  #enemy piece valid
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                        break
                    else: break # invalid
                else: break #off board

    def getKnightMove(self, r, c, moves):
        knightsMoves=((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
        allyCol="w" if self.whiteToMove else "b"
        for m in knightsMoves:
            endRow=r+m[0]
            endCol=c+m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:  # on board
                endPiece=self.board[endRow][endCol]
                if endPiece[0]!=allyCol:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getBishopMove(self,r,c,moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1 , 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":  # empty space valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # enemy piece valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break  # invalid
                else:
                    break  # off board

    def getQueenMove(self, r, c, moves):
        self.getRookMove(r,c,moves)
        self.getBishopMove(r,c,moves)

    def getKingMove(self, r, c, moves):
        kingMoves=((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1))
        allyCol = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:  # on board
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyCol:
                    moves.append(Move((r, c), (endRow, endCol), self.board))


    def getCastleMove(self,r,c,moves):
        if self.squareUnderAttack(r,c):
            return #can not castle when in check
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r,c,moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves)




    def getKingsideCastleMoves(self,r,c,moves):
        if self.board[r][c+1]=='--' and self.board[r][c+2]=='--':
            if not self.squareUnderAttack(r,c+1) and not self.squareUnderAttack(r,c+2):
                moves.append(Move((r,c),(r,c+2),self.board,isCastleMove=True))


    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c-3]=='--':
            if not self.squareUnderAttack(r,c - 1) and not self.squareUnderAttack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board,isCastleMove=True))



class CastleRight():
    def __init__(self,wks,bks,wqs,bqs):
        self.wks=wks
        self.bks=bks
        self.wqs=wqs
        self.bqs=bqs



class Move():
    # dictionary các vị trí quân cờ sang tên gọi trong cờ, cột là files ,dòng là ranks
    # VD: vị trí (1,0) -> row 1 column 0 trong cờ gọi là A7 (tên gọi trong cờ file trước rank sau)
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1,
                   "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6,
                   "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    # constructor ghi nhận việc di chuyển quân (ô nào,quân nào,tới đâu) và xem có ăn quân không
    def __init__(self, startSq, endSq, board,isEnpassantMove=False,isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        #pawn promotion
        self.isPawnPromotion= (self.pieceMoved=="wp" and self.endRow==0) or (self.pieceMoved=="bp" and self.endRow==7)

        #en passant
        self.isEnpassantMove=isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured='wp' if self.pieceMoved=='bp' else 'bp'
        #castle
        self.isCastleMove=isCastleMove


        self.moveID=self.startRow*1000 +self.startCol*100 +self.endRow*10+self.endCol # kiểu kiểu hash function



    #Override equal method
    def __eq__(self, other):
        if isinstance(other,Move):
            return self.moveID==other.moveID
        return False


    def getChessNotation(self):
        return self.getRankFile(self.startRow,self.startCol) + self.getRankFile(self.endRow,self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c]+self.rowsToRanks[r]


