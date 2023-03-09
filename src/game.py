
from game_vars import *
from board import *

class Game:
    def __init__(self):
        self.board = Board()
        self.font = pygame.font.SysFont('monospace', 18, bold=True)
        pass


    
    def update_game(self):
        pass

    
    def _draw_board(self, display):
        blk = "#f0c39c"
        wht = "#783c07"
        for row in range(ROWS):
            for col in range(COLS):
                # color
                color = blk if (row + col) % 2 == 0 else wht
                # rect
                rect = (col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE)
                # blit
                pygame.draw.rect(display, color, rect)

                # row coordinates
                if col == 0:
                    # color
                    color =  blk  if row % 2 != 0 else wht
                    # label
                    lbl = self.font.render(str(ROWS-row), 1, color)
                    lbl_pos = (5, 5 + row * SQSIZE)
                    # blit
                    display.blit(lbl, lbl_pos)
                # col coordinates
                if row == 7:
                    # color
                    color = blk if (row + col) % 2 != 0 else wht
                    # label
                    lbl = self.font.render(chr(97 + col), 1, color)
                    lbl_pos = (col * SQSIZE + SQSIZE - 20, HEIGHT - 20)
                    # blit
                    display.blit(lbl, lbl_pos)
        
        
    def _draw_pieces(self, display):
        for row in range(ROWS):
            for col in range(COLS):
                if self.board.squares[row][col].has_piece():
                    piece = self.board.squares[row][col].piece
                    piece.draw(display)
                    
            


   

    