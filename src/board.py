import os
import copy
import pygame
import chess
from piece import Piece, Pawn, King, Queen, Rook, Bishop, Knight
from game_vars import *
from tile import Tile



class Board:

    def __init__(self, testing = False, fen=""):
        self.move_count = 0
        self.turn = "white"
        if fen:
            self.tiles = [[0, 0, 0, 0, 0, 0, 0, 0] for col in range(COLS)]
            self.white_k = None
            self.black_k = None
            self.white_check = False
            self.black_check = False
            self.last_move = None
            self.load_from_FEN(fen_string=fen)
        else:
            self.tiles = [[0, 0, 0, 0, 0, 0, 0, 0] for col in range(COLS)]
            self.last_move = None
            self._create()
            if not testing:
                self._add_pieces('white')
                self.white_k = self.tiles[7][4].piece
                self.white_check = False
                self._add_pieces('black')
                self.black_k = self.tiles[0][4].piece
                self.white_check = False
                self.black_check = False
            else:
                self.white_check = False
                self.black_check = False
                self.white_k = None
                self.black_k = None

        self.try_move_piece = None
        self.engine_try_move_piece = None
        self.last_move_castle_left = False
        self.last_move_castle_right = False
        self.last_move_castle_left_engine = False
        self.last_move_castle_right_engine = False
        self.demo_en_passant = False
        self.demo_promotion = False
        self.demo_castle_left = False
        self.demo_castle_right = False
        self.dummy_piece = None
        self.dummy_eaten_piece = None
        self.demo_org_tile = [9,9]
        self.move_being_undone = False
        self.black_attacking_sqrs = []
        self.white_attacking_sqrs = []

    def set_turn(self, num):
        self.move_count += 1
        if num == 1:
            self.turn = 'white'
        else:
            self.turn = 'black'             
    def _create(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.tiles[row][col] = Tile(row, col)

    def reset_en_passant_board(self, color):
        for i in self.tiles:
            for j in i:
                if color == j.en_passant_color:
                    j.reset_passant()                

    def _add_pieces(self, color):
        row_pawn, row_other = (6, 7) if color == 'white' else (1, 0)
         # pawns
        for col in range(COLS):
            self.tiles[row_pawn][col] = Tile(
                row_pawn, col, Pawn(color, row_pawn, col))

        # knights
        self.tiles[row_other][1] = Tile(
            row_other, 1, Knight(color, row_other, 1))
        self.tiles[row_other][6] = Tile(
            row_other, 6, Knight(color, row_other, 6))

        # bishops
        self.tiles[row_other][2] = Tile(
            row_other, 2, Bishop(color, row_other, 2))
        self.tiles[row_other][5] = Tile(
            row_other, 5, Bishop(color, row_other, 5))

        # rooks
        self.tiles[row_other][0] = Tile(
            row_other, 0, Rook(color, row_other, 0))
        self.tiles[row_other][7] = Tile(
            row_other, 7, Rook(color, row_other, 7))

        # queen
        self.tiles[row_other][3] = Tile(
            row_other, 3, Queen(color, row_other, 3))

        # king
        self.tiles[row_other][4] = Tile(
            row_other, 4, King(color, row_other, 4))

    def trigger_Promotion(self, piece):
        color = piece.color
        r,f = piece.rank,piece.file
        return Queen(color, r, f)

    def check_for_check(self):
        if self.last_move.color == 'black':
            self.white_check = self.check_white_k_in_check()
        else:
            self.black_check = self.check_black_k_in_check()


    def is_in_check(self, color):
        if color == 'white':
            return self.check_white_k_in_check()
        return self.check_black_k_in_check()
    
    def is_checkmate(self):
        return self.check_for_checkmate()
    
    def check_for_game_end(self):
        self.check_for_check()
        checkMate, winner = self.check_for_checkmate()
        if checkMate:
            return True, winner
        else:
            stale_mate = self.check_for_stalemate()
            return stale_mate, 'Stalemate' if stale_mate else ''
        

    def check_for_checkmate(self,test = False):
        if self.last_move is None:
            return False, ''
        check_mate_color = "white" if self.last_move.color == "black" else "black"
        for rank in self.tiles:
            for tile in rank:
                if tile.has_piece() and tile.piece.color == check_mate_color:
                    if len(self.piece_legal_moves(tile.piece)) >0:
                        return False, ''
                    
        if check_mate_color == 'black' and self.black_check:
            if not test:
                print(self.last_move.color + " wins")
                with open("logs/winner.out", "a") as file:
                    file.write(self.last_move.color + " wins\n")
            return True, self.last_move.color
        elif check_mate_color == 'white' and self.white_check:
            if not test:        
                print(self.last_move.color + " wins")
                with open("logs/winner.out", "a") as file:
                    file.write(self.last_move.color + " wins\n")
            return True, self.last_move.color
        return False, ''
    
    def check_for_stalemate(self, demo = False):
        remaining_pieces_white = []
        remaining_pieces_black = []
        stale_mate = True
        check_mate_color = "white" if self.last_move.color == "black" else "black"
        for rank in self.tiles:
            for tile in rank:
                if tile.has_piece():
                    if tile.piece.color == 'white':
                        remaining_pieces_white.append(tile.piece)
                    if tile.piece.color == 'black':
                        remaining_pieces_black.append(tile.piece)
                    if tile.piece.color == check_mate_color:
                        if len(self.piece_legal_moves(tile.piece)) >0:
                            stale_mate = False
        
        if len(remaining_pieces_black) == len(remaining_pieces_white) and len(remaining_pieces_black) == 1:
            # if demo:
            with open("logs/winner.out", "a") as file:
                file.write("Stalemate\n")
                print("stalemate")
            return True
        if stale_mate:
            # if not demo:
            with open("logs/winner.out", "a") as file:
                file.write("Stalemate\n")
                print("stalemate")
            return True
        return stale_mate
    
    def get_legal_moves_random(self,color):
        pieces = []
        for rank in self.tiles:
            for tile in rank:
                if tile.has_piece() and tile.piece.color == color:
                    org_legals = self.piece_legal_moves(tile.piece)
                    if len(org_legals) > 0:
                        pieces.append((tile.piece, org_legals))
        return pieces
    
    def get_legal_moves_engine(self,color):
        legals = []
        for rank in self.tiles:
            for tile in rank:
                if tile.has_piece() and tile.piece.color == color:
                    org_legals = self.piece_legal_moves(tile.piece)
                    if len(org_legals) > 0:
                        for mv in org_legals:
                            move_name = chr(97 + tile.piece.file) + str(ROWS - tile.piece.rank) + chr(97 + mv[1]) + str(ROWS - mv[0])
                            move = (tile.piece.rank, tile.piece.file, mv[0], mv[1])
                            legals.append((move,move_name))
        return legals
    
    def piece_legal_moves(self,piece : Piece, recursive = False):
        king_piece = self.white_k if piece.color == 'white' else self.black_k
        original_legal_move_list = piece.legal_moves().copy()
        approved_moves = []
        #pawn
        if isinstance(piece,Pawn):
            for mv in original_legal_move_list:
                tile = self.tiles[mv[0]][mv[1]]
                if tile.has_piece():
                    if mv[1] != piece.file and tile.piece.color != piece.color:
                        approved_moves.append(mv)
                else:
                    if mv[1] == piece.file and (not self.tiles[piece.rank + piece.dir][piece.file].has_piece()):
                        approved_moves.append(mv)
            #En Passant
            if isinstance(self.last_move, Pawn):
                r,f = self.last_move.rank, self.last_move.file
                mvr,mvf = r - self.last_move.dir, f
                tile = self.tiles[mvr][mvf]
                if tile.can_en_passant(piece.dir) and (mvr, mvf) in original_legal_move_list:
                    piece.en_passant = (mvr,mvf)
                    approved_moves.append((mvr,mvf))
        #knight
        elif isinstance(piece,Knight):
            for mv in original_legal_move_list:
                tile = self.tiles[mv[0]][mv[1]]
                if tile.has_piece():
                    if tile.piece.color != piece.color:
                        approved_moves.append(mv)
                else:
                    approved_moves.append(mv)

        #king
        elif isinstance(piece,King):
            for mv in original_legal_move_list:
                tile = self.tiles[mv[0]][mv[1]]
                if tile.has_piece():
                    if tile.piece.color != piece.color:
                        approved_moves.append(mv)
                else:
                    approved_moves.append(mv)
            #castling
            if piece.can_castle_left() and not piece.blocking_left and not piece.is_in_check():
                approved_moves.append(piece.castle_left_tile)
                
            if piece.can_castle_right() and not piece.blocking_right and not piece.is_in_check():
                approved_moves.append(piece.castle_right_tile)

        #queen, bishop or rook
        elif isinstance(piece, (Bishop, Queen, Rook)):
            for dir_moves in original_legal_move_list:
                for mv in dir_moves:
                    tile = self.tiles[mv[0]][mv[1]]
                    if tile.has_piece():
                        if tile.piece.color != piece.color:
                            approved_moves.append(mv)
                            break
                        break
                    else:
                        approved_moves.append(mv)
        """
        if king is in check, we only allow moves that result in getting out of the check,
        as well as moves that don't cause a check
        
        -we need to avoid recursive calls back so we skip this part if we are already in it
        """
        if not recursive and king_piece is not None:
            legal_moves = []
            for mv in approved_moves:
                #try the move
                board = chess.Board(self.save_to_FEN())
                uci = chr(97 + piece.file) + str(ROWS - piece.rank) + chr(97 + mv[1]) + str(ROWS - mv[0])
                if isinstance(piece, Pawn) and (uci[-1] == '8' or uci[-1] == '1'):
                    uci += 'q'
                move = chess.Move.from_uci(uci)
                if move in board.legal_moves:
                    legal_moves.append(mv)


                # temp_board = self.try_move(piece, self.tiles[mv[0]][mv[1]])
                # temp_king_piece = temp_board.black_k if king_piece.color == 'black' else temp_board.white_k
                # if not temp_board.king_in_check(temp_king_piece):
                #     legal_moves.append(mv)
                # self.undo_move(piece, self.tiles[mv[0]][mv[1]])
            return legal_moves
        else:
            return approved_moves
    def king_in_check(self,piece:Piece):
        if piece.color == 'white':
            return self.check_white_k_in_check()
        return self.check_black_k_in_check()
        
    def try_move(self, piece: Piece, tile: Tile, who_called = ""):
        temp_piece = copy.deepcopy(piece)
        temp_board = copy.deepcopy(self)
        temp_board.move_piece(temp_piece, temp_board.tiles[tile.row][tile.col], testing=True)

        if isinstance(piece,King):
            if piece.color == 'white':
                temp_board.white_k = temp_board.tiles[tile.row][tile.col].piece
            else:
                temp_board.black_k = temp_board.tiles[tile.row][tile.col].piece

        return temp_board

    def move_piece(self, piece : Piece, tile: Tile, demo = False, testing = False):
        if piece.rank == tile.row and piece.file == tile.col:
            return False
        
        if demo or self.move_being_undone or (not demo and not self.move_being_undone and (tile.row,tile.col) in self.piece_legal_moves(piece, testing)) :
            org_tile = self.tiles[piece.rank][piece.file]

            if isinstance(piece, Pawn):
                #En Passant 
                if (tile.row - piece.dir, tile.col) == piece.en_passant_tile and not piece.moved and not demo:
                    self.tiles[tile.row - piece.dir][tile.col].set_en_passant(-piece.dir) 
                #if we move to an en passant square we kill the other pawn
                elif tile.can_en_passant(piece.dir) or self.demo_en_passant:
                    if self.demo_en_passant:
                        self.tiles[piece.rank - piece.dir][piece.file].piece = self.dummy_piece
                    elif demo:
                        self.dummy_piece = self.tiles[tile.row - piece.dir][tile.col].piece 
                        self.demo_en_passant = True
                        self.tiles[tile.row - piece.dir][tile.col].piece = None
                    elif tile.can_en_passant(piece.dir):
                        self.tiles[tile.row - piece.dir][tile.col].piece = None
                #promotion
                if (tile.row == 0 or  tile.row == 7) and not demo and not self.move_being_undone:
                    piece = self.trigger_Promotion(piece)

            #castle
            if isinstance(piece, King):
                #castling
                if ((tile.row, tile.col) == piece.castle_left_tile and piece.can_castle_left() and not piece.is_in_check()) or (self.demo_castle_left):
                    if self.demo_castle_left:
                        self.move_piece(self.tiles[piece.rank][piece.file + 1].piece, self.tiles[piece.rank][piece.file -2])
                    elif demo:
                        self.demo_castle_left = True 
                        self.move_piece(self.tiles[tile.row][tile.col - 2].piece,self.tiles[tile.row][tile.col + 1], True)
                    else:
                        self.move_piece(self.tiles[tile.row][tile.col - 2].piece,self.tiles[tile.row][tile.col + 1])
                if ((tile.row, tile.col) == piece.castle_right_tile and piece.can_castle_right() and not piece.is_in_check()) or self.demo_castle_right:
                    if self.demo_castle_right: 
                        self.move_piece(self.tiles[piece.rank][piece.file - 1].piece,self.tiles[piece.rank][piece.file + 1])
                    elif demo:
                        self.demo_castle_right = True
                        self.move_piece(self.tiles[tile.row][tile.col + 1].piece,self.tiles[tile.row][tile.col - 1], True)
                    else:
                        self.move_piece(self.tiles[tile.row][tile.col + 1].piece,self.tiles[tile.row][tile.col - 1])
            
            if isinstance(piece, Rook) and (not demo) and (not self.move_being_undone):
                king_piece = self.black_k if piece.color == "black" else self.white_k
                if piece.file == 0 and king_piece.can_castle_left() and not self.demo_castle_left:
                    king_piece.cant_castle_left()
                if piece.file == 7 and king_piece.can_castle_right() and not self.demo_castle_right:
                    king_piece.cant_castle_right()
            
            if not demo and not self.move_being_undone:
                piece.rank,piece.file = tile.row,tile.col
                if tile.piece:
                    tile.piece = None

                tile.set_piece(piece)
                piece._moved()
                self.last_move = piece
                self.update_castling()
                org_tile.set_piece(None)
            elif demo:
                piece.rank,piece.file = tile.row,tile.col
                if tile.piece:
                    tile.piece = None
                tile.set_piece(piece)
                org_tile.set_piece(None)

            elif self.move_being_undone:
                r,f = piece.rank,piece.file
                piece.rank,piece.file = tile.row,tile.col
                tile.set_piece(piece)
                self.tiles[r][f].set_piece(self.dummy_eaten_piece)

            # if not testing:
            #     self.update_attacked_squares(piece.color)
            self.set_turn(2 if piece.color == 'white'else 1)
            return True
        
        return False
    
    def update_castling(self):
        king_piece = self.white_k if self.last_move is None or self.last_move.color == "black" else self.black_k
        #if there are any pieces in between:
        #left 
        if king_piece is not None:
            if king_piece.can_castle_left():
                piece_in_between = False
                piece_files = [(king_piece.rank, king_piece.file - i) for i in range(1,4)]
                for i,j in piece_files:
                    if self.tiles[i][j].has_piece():
                        piece_in_between = True
                        break
                king_piece.blocking_left = piece_in_between
            #right
            if king_piece.can_castle_right():
                piece_in_between = False
                piece_files = [(king_piece.rank, king_piece.file + i) for i in range(1,3)]
                for i,j in piece_files:
                    if self.tiles[i][j].has_piece():
                        piece_in_between = True
                        break
                king_piece.blocking_right = piece_in_between
            #if king is in check:
            if king_piece.color == 'white':
                if self.check_white_k_in_check():
                    king_piece.in_check()
                else:
                    king_piece.not_in_check()

            if king_piece.color == 'black':
                if self.check_black_k_in_check():
                    king_piece.in_check()
                else:
                    king_piece.not_in_check()

            #if the middle square is attacked
            #left
            if self.is_tile_attacked(king_piece.rank,king_piece.file-1, king_piece.color):
                king_piece.blocking_left = True
                
            if self.is_tile_attacked(king_piece.rank,king_piece.file+1, king_piece.color):
                king_piece.blocking_right = True


    def is_tile_attacked(self,tile_r,tile_f,color):
        for i in self.tiles:
            for j in i:
                if j.has_piece():
                    if j.piece.color != color:
                        if (tile_r,tile_f) in self.piece_legal_moves(j.piece, True):
                            return True
        return False

    def check_white_k_in_check(self):
        # if (self.white_k.rank, self.white_k.file) in self.black_attacking_sqrs and (not self.white_check):
        #     return True
        
        for row in self.tiles:
            for tile in row:
                if tile.has_piece():
                    if tile.piece.color == "black":
                        if (self.white_k.rank, self.white_k.file) in self.piece_legal_moves(tile.piece, True):
                            return True
        return False

    def check_black_k_in_check(self):
        # if (self.black_k.rank, self.black_k.file) in self.white_attacking_sqrs and (not self.black_check):
        #     return True
        
        for row in self.tiles:
            for tile in row:
                if tile.has_piece():
                    if tile.piece.color == "white":
                        if (self.black_k.rank, self.black_k.file) in self.piece_legal_moves(tile.piece, True):
    
                            return True
        return False
    #This doesns't check for pinned moves 
    def update_attacked_squares(self, color):
        attacked_sqrs = []
        for row in self.tiles:
            for tile in row:
                if tile.has_piece():
                    if tile.piece.color == color:
                        piece_leg = self.piece_legal_moves(tile.piece, True)
                        if len(piece_leg) > 0:
                            attacked_sqrs.extend(piece_leg)
        if color == 'black':
            self.black_attacking_sqrs = attacked_sqrs
        else:
            self.white_attacking_sqrs = attacked_sqrs
        return attacked_sqrs
    def save_to_FEN(self):
        FEN_str = ""
        for i in self.tiles:
            rank_empties = 0
            for tile in i:
                if tile.has_piece():
                    if rank_empties > 0:
                        FEN_str += str(rank_empties)
                        rank_empties = 0
                    if tile.piece.color == "black":
                        FEN_str += tile.piece.name[0].lower() if tile.piece.name != "knight" else 'n'
                    else:
                        FEN_str += tile.piece.name[0].upper() if tile.piece.name != "knight" else 'N'
                else:
                    rank_empties += 1
                    if tile.col == 7:
                        FEN_str += str(rank_empties)
    
            FEN_str +='/'
        FEN_str = FEN_str[:-1]
        FEN_str += " " + self.turn[0] + " "
        if self.white_k.can_castle_left():
            FEN_str += "Q"
        if self.white_k.can_castle_right():
            FEN_str += "K"
        if self.black_k.can_castle_left():
            FEN_str += "q"
        if self.black_k.can_castle_right():
            FEN_str += "k"
        if not (self.white_k.can_castle_left() or self.white_k.can_castle_right()
                or self.black_k.can_castle_left() or self.black_k.can_castle_right()):
            FEN_str += "-"
        FEN_str += " "
        if self.last_move and isinstance(self.last_move, Pawn) and \
          self.tiles[self.last_move.rank - self.last_move.dir][self.last_move.file].can_en_passant(-self.last_move.dir):
            FEN_str += chr(97 + self.last_move.file) + str((ROWS - self.last_move.rank) + self.last_move.dir  ) + " "
        else:
            FEN_str += "- "
        FEN_str += str((self.move_count + 1) // 2) + " "
        FEN_str += str(self.move_count) 
        return FEN_str

    def load_from_FEN(self, fen_string):
   
        # Split the FEN string into its components
        fen_parts = fen_string.split()
        # Load the piece positions onto the board
        row = 0
        col = 0
        for char in fen_parts[0]:
            if char == "/":
                row += 1
                col = 0
            elif char.isdigit():
                for i in range(int(char)):
                    self.tiles[row][col] = Tile(row, col)
                    col += 1
                
            else:
                if char == "p":
                    self.tiles[row][col] = Tile(row, col, Pawn("black", row, col))
                elif char == "n":
                    self.tiles[row][col] = Tile(row, col, Knight("black", row, col))
                elif char == "b":
                    self.tiles[row][col] = Tile(row, col, Bishop("black", row, col))
                elif char == "r":
                    self.tiles[row][col] = Tile(row, col, Rook("black", row, col))
                elif char == "q":
                    self.tiles[row][col] = Tile(row, col, Queen("black", row, col))
                elif char == "k":
                    self.tiles[row][col] = Tile(row, col, King("black", row, col))
                    if self.tiles[row][col].piece.color == "black":
                        self.black_k = self.tiles[row][col].piece
                elif char == "P":
                    self.tiles[row][col] = Tile(row, col, Pawn("white", row, col))
                elif char == "N":
                    self.tiles[row][col] = Tile(row, col, Knight("white", row, col))
                elif char == "B":
                    self.tiles[row][col] = Tile(row, col, Bishop("white", row, col))
                elif char == "R":
                    self.tiles[row][col] = Tile(row, col, Rook("white", row, col))
                elif char == "Q":
                    self.tiles[row][col] = Tile(row, col, Queen("white", row, col))
                elif char == "K":
                    self.tiles[row][col] = Tile(row, col, King("white", row, col))
                    if self.tiles[row][col].piece.color == "white":
                        self.white_k = self.tiles[row][col].piece

                else: # empty space
                    self.tiles[row][col] = Tile(row, col)

                col += 1

        # Set the turn
        self.set_turn(1 if fen_parts[1] == "w" else 0)

        # Handle castling rights
        self.white_k.cant_castle_right()
        self.white_k.cant_castle_left()
        self.black_k.cant_castle_right()
        self.black_k.cant_castle_left()

        if fen_parts[2] != "-":
            for char in fen_parts[2]:
                if char == "K":
                    self.white_k.castle_right = True
                elif char == "Q":
                    self.white_k.castle_left = True
                elif char == "k":
                    self.black_k.castle_right = True
                elif char == "q":
                    self.black_k.castle_left = True

        # Set the en passant square
        if fen_parts[3] != "-":
            col = ord(fen_parts[3][0]) - ord("a")
            row = (8 - int(fen_parts[3][1]))  
            self.tiles[row][col].set_en_passant(1 if self.turn == "black" else -1)

        # Set the move count and halfmove clock
        self.move_count = int(fen_parts[5])

