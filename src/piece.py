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
        self._moved = False
        self.sprite_load = pygame.image.load(os.path.join(IMAGE_DIR, sprt_name + '.png'))
        self.sprite = pygame.transform.scale(self.sprite_load, (80 , 80))
    # def _load_sprite(self, sprt_name):
    #     self.sprite = 
    #     print(self.sprite)
    
    def draw(self, display):
        piece_img = self.sprite
        img_center = self.file * TSIZE + TSIZE // 2, self.rank * TSIZE + TSIZE // 2
        img_rect = piece_img.get_rect(center=img_center)
        display.blit(piece_img,img_rect)
    
    def moved(self):
        self._moved = True
        self.legals.clear()

    def legal_moves(self,board):
        pass     


class Pawn(Piece):
    def __init__(self, color, rank = 0, file= 0):
        super().__init__( rank , file,'pawn', color, 1.0, 'bP' if color == 'black' else 'wP')
        self.en_passant_tile = (self.rank + 1 * self.dir,self.file)
    def legal_moves(self, board):
        sq = 2
        if not self._moved:
            sq = 3
        for i in range(1, sq):
            if self.rank + (i*self.dir) < 0 or self.rank + (i*self.dir) >= COLS :
                continue
            if not board.tiles[self.rank + (i*self.dir)][self.file].has_piece():
                self.legals.append((self.rank + (i*self.dir),self.file))


        #--TODO-- eat right or left
        diags = [(self.rank + (1*self.dir), self.file + 1),(self.rank + (1*self.dir), self.file - 1)]
        for t in diags:
            if t[0] < 0 or t[0] >= ROWS or t[1] < 0 or t[1] >= COLS:
                continue
            tile =board.tiles[t[0]][t[1]]
            if tile.has_piece():
                if tile.piece.color != self.color:
                    self.legals.append(t)
            elif tile.can_en_passant():
                self.legals.append(t)

        return self.legals
    def promote(self):
        pass

class King(Piece):
    def __init__(self, color, rank = 0, file= 0):
        self.castle_left = True
        self.castle_right = True
        self.in_check = False
        self.castle_left_tile = (0,0)
        self.castle_right_tile = (0,0)
        super().__init__( rank , file,'king', color, 9999.9, 'bK' if color == 'black' else 'wK')

    def legal_moves(self, board):
        possible_moves = [(self.rank + i, self.file + j) for i,j in [(0,1),(1,0),(1,1),(-1,0),(-1,-1),(0,-1),(1,-1),(-1,1)]]
        for m in possible_moves:
            if m[0] >= 0 and m[0] < ROWS and m[1] >= 0 and m[1] < COLS:
                tile =board.tiles[m[0]][m[1]]
                if tile.has_piece():
                    if tile.piece.color != self.color:
                        self.legals.append(m)
                else:
                        self.legals.append(m)
        #castling
        if self._moved:
            self.castle_left = False
            self.castle_right= False
            
        #castle left
        if self.castle_left:
            piece_files = [(self.rank, self.file - i) for i in range(1,4)]
            for i,j in piece_files:
                if not board.tiles[i][j].has_piece():
                    self.add_castle_left()
        #castle_right
        if self.castle_right:        
            piece_files = [(self.rank, self.file + i) for i in range(1,3)]
            for i,j in piece_files:
                if not board.tiles[i][j].has_piece():
                    self.add_castle_right()
        return self.legals
    
    def can_castle_left(self):
        return self.castle_left
    
    def can_castle_right(self):
        return self.castle_right
    
    def add_castle_left(self):
        self.legals.append((self.rank, self.file - 2))
        self.castle_left_tile=(self.rank, self.file - 2)

    def add_castle_right(self):
        self.legals.append((self.rank, self.file + 2))
        self.castle_right_tile=(self.rank, self.file + 2)


class Queen(Piece):
    def __init__(self, color, rank = 0, file= 0):
        super().__init__( rank , file,'queen', color, 9.0, 'bQ' if color == 'black' else 'wQ')

class Rook(Piece):
    def __init__(self, color, rank = 0, file= 0):
        super().__init__( rank , file,'rook', color, 5.0, 'bR' if color == 'black' else 'wR')
    def legal_moves(self, board):
        pass
class Bishop(Piece):
    def __init__(self, color, rank = 0, file= 0):
        super().__init__( rank , file,'bishop', color, 3.0, 'bB' if color == 'black' else 'wB')

class Knight(Piece):
    def __init__(self, color, rank = 0, file= 0):
        super().__init__( rank , file,'knight', color, 3.0, 'bN' if color == 'black' else 'wN')