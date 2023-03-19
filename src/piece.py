import os
import pygame
from game_vars import *
class Piece:
    def __init__(self,rank, file, name, color, value, sprt_name):
        self.rank = rank
        self.file = file
        self.name = name
        self.color = color
        self.color_val = 1 if color == "black" else -1
        self.value = value * self.color_val
        self.dir = self.color_val
        self.legals = []
        self.moved = False
        self.sprite = pygame.image.load(os.path.join(IMAGE_DIR, sprt_name + '.png'))

    
    def draw(self, display):
        piece_img = self.sprite
        img_center = self.file * TSIZE + TSIZE // 2, self.rank * TSIZE + TSIZE // 2
        img_rect = piece_img.get_rect(center=img_center)
        display.blit(piece_img,img_rect)
    
    def _moved(self):
        self.moved = True
        self.legals.clear()

    def legal_moves(self,board):
        if board.white_check and self.color == 'white' or (board.black_check and self.color == 'black'):
            return self.in_check_legals(board)
        else:
            return self.check_pin(board)


    def legal_moves_pre_check(self,board):
        pass

    def legal_straight_moves(self,board, dirs):
        self.legals.clear()
        r,f = self.rank, self.file
        for dir in dirs:
            rank_i = dir[0]
            file_i = dir[1]
            while True:    
                if rank_i + r >= 0 and rank_i + r < ROWS and file_i + f >= 0 and file_i + f < COLS:
                    tile =board.tiles[rank_i + r][file_i + f]
                    if tile.has_piece():
                        if tile.piece.color != self.color:
                            if not (rank_i + r, file_i + f) in self.legals: 
                                self.legals.append((rank_i + r, file_i + f))
                        break
                    else:
                        if not (rank_i + r, file_i + f) in self.legals:
                            self.legals.append((rank_i + r, file_i + f))
                else:
                    break
                rank_i += dir[0]
                file_i += dir[1]
        return self.legals

    def in_check_legals(self, board):
        legals = []
        cnt = 0
        to_check = [i for i in self.legal_moves_pre_check(board)]
        for (r,f) in to_check:
            if board.check_for_move_uncheck(self.rank, self.file, r,f):
                legals.append((r,f))
            # cnt += 1

        return legals
    def check_pin(self, board):
        legals = self.legal_moves_pre_check(board)
        final_legals = []
        for move in legals:
            if board.check_pin_move(self.rank,self.file,move[0], move[1]):
                final_legals.append(move)
            
        return final_legals

    


class Pawn(Piece):
    def __init__(self, color, rank = 0, file= 0):
        super().__init__( rank , file,'pawn', color, 1.0, 'bP' if color == 'black' else 'wP')
        self.en_passant_tile = (self.rank + 1 * self.dir,self.file)
    def legal_moves_pre_check(self, board):
        self.legals.clear()
        sq = 2
        if not self.moved:
            sq = 3
        for i in range(1, sq):
            if self.rank + (i*self.dir) < 0 or self.rank + (i*self.dir) >= COLS :
                continue
            if board.tiles[self.rank + (i*self.dir)][self.file].has_piece():
                break

            if not (self.rank + (i*self.dir),self.file) in self.legals:
                self.legals.append((self.rank + (i*self.dir),self.file))


        #--TODO-- eat right or left
        diags = [(self.rank + (1*self.dir), self.file + 1),(self.rank + (1*self.dir), self.file - 1)]
        for t in diags:
            if t[0] < 0 or t[0] >= ROWS or t[1] < 0 or t[1] >= COLS:
                continue
            tile =board.tiles[t[0]][t[1]]
            if tile.has_piece():
                if tile.piece.color != self.color:
                    if not t in self.legals:
                        self.legals.append(t)
            elif tile.can_en_passant(self.dir):
                if not t in self.legals:
                    self.legals.append(t)
            #check if promotion
        return self.legals
    def promote(self, board):
        if self.dir == -1 and self.rank == 0 or self.dir == 1 and self.rank == 7 : 
            board.triggerPromotion(self.rank,self.file, self.color)
            
class King(Piece):
    def __init__(self, color, rank = 0, file= 0):
        self.castle_left = True
        self.castle_right = True
        self.in_check = False
        self.castle_left_tile = (0,0)
        self.castle_right_tile = (0,0)
        super().__init__( rank , file,'king', color, 9999.9, 'bK' if color == 'black' else 'wK')

    def legal_moves_pre_check(self, board):
        self.legals.clear()
        possible_moves = [(self.rank + i, self.file + j) for i,j in [(0,1),(1,0),(1,1),(-1,0),(-1,-1),(0,-1),(1,-1),(-1,1)]]
        for m in possible_moves:
            if m[0] >= 0 and m[0] < ROWS and m[1] >= 0 and m[1] < COLS:
                tile =board.tiles[m[0]][m[1]]
                if tile.has_piece():
                    if tile.piece.color != self.color:
                        if not m in self.legals:    
                            self.legals.append(m)
                else:
                    if not m in self.legals:    
                        self.legals.append(m)
        #castling
        if self.moved:
            self.castle_left = False
            self.castle_right= False
            
        #castle left
        if self.castle_left and board.get_in_check(self.color):
            castle = True
            piece_files = [(self.rank, self.file - i) for i in range(1,4)]
            for i,j in piece_files:
                if board.tiles[i][j].has_piece():
                    castle = False
            if castle:
                self.add_castle_left()
        #castle_right
        if self.castle_right and board.get_in_check(self.color):        
            castle = True
            piece_files = [(self.rank, self.file + i) for i in range(1,3)]
            for i,j in piece_files:
                if board.tiles[i][j].has_piece():
                    castle = False
            if castle:
                self.add_castle_right()
        return self.legals
    
    def can_castle_left(self):
        return self.castle_left
    
    def can_castle_right(self):
        return self.castle_right
    
    def add_castle_left(self):
        if not (self.rank, self.file - 2) in self.legals: 
            self.legals.append((self.rank, self.file - 2))
        self.castle_left_tile=(self.rank, self.file - 2)

    def add_castle_right(self):
        if not (self.rank, self.file + 2) in self.legals: 
            self.legals.append((self.rank, self.file + 2))
        self.castle_right_tile=(self.rank, self.file + 2)


class Queen(Piece):
    def __init__(self, color, rank = 0, file= 0):
        super().__init__( rank , file,'queen', color, 9.0, 'bQ' if color == 'black' else 'wQ')
    def legal_moves_pre_check(self, board):
        self.legals.clear()
        return super().legal_straight_moves(board, dirs = [(0,1),(1,0),(1,1),(-1,0),(-1,-1),(0,-1),(1,-1),(-1,1)])

class Rook(Piece):
    def __init__(self, color, rank = 0, file= 0):
        super().__init__( rank , file,'rook', color, 5.0, 'bR' if color == 'black' else 'wR')
    def legal_moves_pre_check(self, board):
        self.legals.clear()
        return super().legal_straight_moves(board, dirs = [(0,1),(1,0),(0,-1),(-1,0)])
class Bishop(Piece):
    def __init__(self, color, rank = 0, file= 0):
        super().__init__( rank , file,'bishop', color, 3.0, 'bB' if color == 'black' else 'wB')
    def legal_moves_pre_check(self, board):
        self.legals.clear()
        return super().legal_straight_moves(board, dirs = [(1,1),(-1,-1),(1,-1),(-1,1)])

class Knight(Piece):
    def __init__(self, color, rank = 0, file= 0):
        super().__init__( rank , file,'knight', color, 3.0, 'bN' if color == 'black' else 'wN')
        
    def legal_moves_pre_check(self, board):
        self.legals.clear()
        possible_moves = [(self.rank + i, self.file + j) for i,j in [(-2,1),(-1,2),(1,2),(2,1),(2,-1),(1,-2),(-1,-2),(-2,-1)]]
        for m in possible_moves:
            if m[0] >= 0 and m[0] < ROWS and m[1] >= 0 and m[1] < COLS:
                tile =board.tiles[m[0]][m[1]]
                if tile.has_piece():
                    if tile.piece.color != self.color:
                        if not m in self.legals:
                            self.legals.append(m)
                else:
                    if not m in self.legals:
                        self.legals.append(m)
        return self.legals