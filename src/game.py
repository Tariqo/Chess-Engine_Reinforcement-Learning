
from game_vars import *
from board import *

class Game:
    def __init__(self):
        self.board = Board()
        self.font = pygame.font.SysFont('monospace', 18, bold=True)
        self.selected_piece = None
        self.current_player = 1
        self.move_count = 1

    def piece_selected(self):
        return self.selected_piece != None
    
    def _white_to_move(self):
        return self.current_player == 1
    
    def _black_to_move(self):
        return self.current_player == 2
    #select piece based on rank and file
    def select_piece(self, pr,pf):
        tile = self.board.tiles[pr][pf]
        if tile.has_piece():
            if self.legal_selection(tile.piece):
                self.selected_piece = tile.piece
                return True
        return False
        
    def legal_selection(self, piece):
        return (self._white_to_move() and piece.color == white) or (self._black_to_move() and piece.color == black) 

    def update_game(self):
        self.selected_piece = None
        self.current_player = 1 if self.current_player == 2 else 2
        self.move_count+=1 

        if self.move_count % 2 ==0:
            self.board.reset_en_passant_board()

    def move_piece(self, pr,pf):
        tiles = self.board.tiles
        current_piece = self.selected_piece
   
        new_tile = tiles[pr][pf]
        r,f = current_piece.rank, current_piece.file

        print(r, f, "->", pr, pf)
        
        #check if piece is moved
        if pr == r and pf == f:
            return False 
        
        #--TODO-- check if legal move
        print(current_piece.legal_moves(self.board))
        if (pr,pf) in current_piece.legal_moves(self.board):
        #change older tile's piece to None
            #En Passant 
            if isinstance(current_piece, Pawn):
                if (pr - current_piece.dir, pf) == current_piece.en_passant_tile:
                    print("enPassant possible")
                    self.board.tiles[pr - current_piece.dir][pf].set_en_passant()                                

            tiles[r][f].piece_moved()
            current_piece.rank, current_piece.file = pr, pf
            current_piece.moved()
            new_tile.set_piece(current_piece)
            return True
        return False
    def deselect(self):
        self.selected_piece = None

    def _draw_board(self, display):
        blk = "#f0c39c"
        wht = "#783c07"
        for row in range(ROWS):
            for col in range(COLS):
                # color
                color = blk if (row + col) % 2 == 0 else wht
                # rect
                rect = (col * TSIZE, row * TSIZE, TSIZE, TSIZE)
                # blit
                pygame.draw.rect(display, color, rect)

                # row coordinates
                if col == 0:
                    # color
                    color =  blk  if row % 2 != 0 else wht
                    # label
                    lbl = self.font.render(str(ROWS-row), 1, color)
                    lbl_pos = (5, 5 + row * TSIZE)
                    # blit
                    display.blit(lbl, lbl_pos)
                # col coordinates
                if row == 7:
                    # color
                    color = blk if (row + col) % 2 != 0 else wht
                    # label
                    lbl = self.font.render(chr(97 + col), 1, color)
                    lbl_pos = (col * TSIZE + TSIZE - 20, HEIGHT - 20)
                    # blit
                    display.blit(lbl, lbl_pos)
        
        
    def _draw_pieces(self, display):
        for row in range(ROWS):
            for col in range(COLS):
                if self.board.tiles[row][col].has_piece():
                    piece = self.board.tiles[row][col].piece
                    piece.draw(display)
                    
            


   

    