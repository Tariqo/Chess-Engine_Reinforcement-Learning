import pygame
import os
from piece import *
from game_vars import *
from tile import *
import copy



class Board:

    def __init__(self):
        self.tiles = [[0, 0, 0, 0, 0, 0, 0, 0] for col in range(COLS)]
        self.last_move = None
        self._create()
        self._add_pieces('white')
        self.white_k = self.tiles[7][4].piece
        self.white_check = False
        self._add_pieces('black')
        self.black_k = self.tiles[0][4].piece
        self.black_check = False
        self.try_move_piece = None
        self.engine_try_move_piece = None
        self.last_move_castle_left = False
        self.last_move_castle_right = False
        self.last_move_castle_left_engine = False
        self.last_move_castle_right_engine = False
        self.turn = ""
        self.move_count = 0
        self.demo_en_passant = False
        self.demo_promotion = False
        self.demo_castle_left = False
        self.demo_castle_right = False
        self.dummy_piece = None
        self.dummy_eaten_piece = None
        self.demo_org_tile = [9,9]
        self.move_being_undone = False

        # cnt = 0
        # for row in self.tiles:
        #     for sqr in row:
        #         cnt +=1
    def set_turn(self, num):
        self.move_count += 1
        if num == 1:
            self.turn == 'white'
        else:
            self.turn == 'black'
             
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

    def triggerPromotion(self, piece):
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
        else:
            return self.check_black_k_in_check()
    
    def is_checkmate(self,color):
        return self.check_for_checkmate()
    def check_for_game_end(self):
        if self.check_for_checkmate():
            return True
        else:
            return self.check_for_stalemate()
        

    def check_for_checkmate(self):
        if self.last_move == None:
            return False
        check_mate_color = "white" if self.last_move.color == "black" else "black"
        for rank in self.tiles:
            for tile in rank:
                if tile.has_piece() and tile.piece.color == check_mate_color:
                    if len(self.piece_legal_moves(tile.piece)) >0:
                        return False
                    
        if check_mate_color == 'black' and self.black_check:
            print(self.last_move.color + " wins")

            with open("winner.log", "a") as file:
                file.write(self.last_move.color + " wins\n")
            return True
        elif check_mate_color == 'white' and self.white_check:

            print(self.last_move.color + " wins")
            with open("winner.log", "a") as file:
                file.write(self.last_move.color + " wins\n")


            return True
        return False    
    
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
            if demo:
                with open("winner.log", "a") as file:
                    file.write("Stalemate\n")
                    print("stalemate")
            return True
        if stale_mate:
            if demo:
                with open("winner.log", "a") as file:
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
                    if mv[1] == piece.file:
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
        elif isinstance(piece,Queen) or isinstance(piece,Bishop) or  isinstance(piece,Rook):
            for dir_moves in original_legal_move_list:
                for mv in dir_moves:
                    tile = self.tiles[mv[0]][mv[1]]
                    if tile.has_piece():
                        if tile.piece.color != piece.color:
                            approved_moves.append(mv)
                            break
                        else:
                            break
                    else:
                        approved_moves.append(mv)
        #if king is in check, we only allow moves that result in getting out of the check,
        #as well as moves that don't cause a check
        
        # we need to avoid recursive calls back so we skip this part if we are already in it
        if not recursive:
            legal_moves = []
            for mv in approved_moves:
                #try the move
                temp_board = self.try_move(piece, self.tiles[mv[0]][mv[1]])
                temp_king_piece = temp_board.black_k if king_piece.color == 'black' else temp_board.white_k
                if not temp_board.king_in_check(temp_king_piece):
                    legal_moves.append(mv)
                # self.undo_move(piece, self.tiles[mv[0]][mv[1]])
            return legal_moves
        else:
            return approved_moves
    def king_in_check(self,piece:Piece):
        if piece.color == 'white':
            return self.check_white_k_in_check()
        else:
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


    # def undo_move(self, piece, tile):
    #     self.move_being_undone = True
    #     move_was_undone = self.move_piece(piece, self.tiles[self.demo_org_tile[0]][self.demo_org_tile[1]])
    #     # try:
    #     # except Exception as E:
    #     #     print(piece.color, piece.name, "from", "(",piece.rank, ",", piece.file, ")" , "to", "(",self.demo_org_tile[0], ",", self.demo_org_tile[1], ")" , "was: False")
    #     #     exit(-1)
    #     self.dummy_piece = None
    #     self.demo_org_tile = [8,8]
    #     self.demo_en_passant = False
    #     self.demo_castle_left = False
    #     self.demo_castle_right = False
    #     self.dummy_eaten_piece = None
    #     self.move_being_undone = False
    #     # log_string = piece.color + " to play: " + "\n" + piece.color + " " + piece.name + " from (" + str(piece.rank)  + "," + str(piece.file) + ") to (" + str(tile.row) + "," + str(tile.col) + ") been undone:\n"
    #     # for i in self.tiles:
    #     #     for j in i:
    #     #         if not j.has_piece():
    #     #             log_string += "--- "
    #     #         else:
    #     #             name = j.piece.name[0].upper() if j.piece.name != 'knight' else 'N'
    #     #             log_string += j.piece.color[0].upper() + "-" + name + " "
    #     #     log_string+= "\n"
    #     # log_string+= "------------------------------------------------\n"
    #     # with open("move_try_log.log", "a") as file: 
    #     #     file.write(log_string)


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
                    piece = self.triggerPromotion(piece)

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


            return True
        
        return False
    def update_castling(self):
        king_piece = self.white_k if self.last_move == None or self.last_move.color == "black" else self.black_k
        #if there are any pieces in between:
        #left 
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
        for row in self.tiles:
            for tile in row:
                if tile.has_piece():
                    if tile.piece.color == "black":
                        if (self.white_k.rank, self.white_k.file) in self.piece_legal_moves(tile.piece, True):
                            return True
        return False

    def check_black_k_in_check(self):
        for row in self.tiles:
            for tile in row:
                if tile.has_piece():
                    if tile.piece.color == "white":
                        if (self.black_k.rank, self.black_k.file) in self.piece_legal_moves(tile.piece, True):

                            return True
        return False
