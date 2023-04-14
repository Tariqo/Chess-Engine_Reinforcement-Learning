import pygame
import sys

from game import *
from game_vars import *
from board import *
import pygame_menu
from pygame.locals import *
import os, sys

# set SDL to use the dummy NULL video driver, 
#   so it doesn't need a windowing system.
# os.environ["SDL_VIDEODRIVER"] = "dummy"


import pygame.transform
class Main:
    
    def __init__(self):
        pygame.init()
        self.game_display = pygame.display.set_mode((WIDTH, WIDTH))
        self.screen = pygame.display.set_mode( (WIDTH, HEIGHT) )
        pygame.display.set_caption('Chess')
        self.game = Game(self.screen)
        pygame.display.set_caption("Menu")
        self.menu = self._create_menu()
        self._engine_play = False
        self.simulate = False
        self.one_person = False
        self.two_persons = False

        # self.menu.mainloop(self.game_display)


    def run(self):
        display = self.screen
        running = True
        self.game._draw_board(display)
        self.game._draw_pieces(display)
        self.game.load_model()
        # self._engine_play = True
        self.simulate= True
        while running:
            if self._engine_play:
                self.game.make_engine_play()
            elif self.one_person:
                self.game.make_engine_play_black()
                self._event_handler()
            elif self.two_persons:
                self._event_handler()
            elif self.simulate:
                self._event_handler(self.simulate)
            pygame.display.update()


    def _event_handler(self, s = False):

        if s:
            
            pygame.key.set_repeat(1,100)
            for event in pygame.event.get():
                if event.type == QUIT or (
                    event.type  == KEYDOWN and (
                    event.key == K_ESCAPE or
                    event.key == K_q
                    )):
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.game.simulate_game()
                elif event.type == pygame.KEYDOWN:
                    self.game.simulate_game()


        else:
            for event in pygame.event.get():
                if event.type == QUIT or (
                    event.type == KEYDOWN and (
                    event.key == K_ESCAPE or
                    event.key == K_q
                    )):
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN: 
                    my, mx = pygame.mouse.get_pos()[0]//TSIZE,pygame.mouse.get_pos()[1]//TSIZE
                    #check if selected piece 
                    if self.game.piece_selected():
                        if self.game.move_piece(mx,my):
                            self.game.update_game()
                            self.game.update_screen()
                        else:
                            self.game.deselect()
                            self.game.update_screen()
                    #select (or drag) a piece to move
                    else:

                        #check if current player's turn
                        #check if clicked piece 
                        #check if legal move
                        self.game.update_screen()
                        if self.game.select_piece(mx,my):
                            self.game.draw_select(self.screen, my,mx)
                            self.game.draw_hover(self.screen,my,mx)
                            self.game.animate.org_RF(mx,my)  
                            self.game.animate.hold(self.game.selected_piece)  

                elif event.type == pygame.MOUSEMOTION:
                    mx , my = pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]
                    self.game.animate.update_mouse(mx,my)
                    if self.game.animate.held:
                        self.game.animate.update_mouse(mx,my)
                        self.game.update_screen()
                        self.game.draw_select(self.screen, self.game.selected_piece.file,self.game.selected_piece.rank)

                        self.game._draw_highlights(self.screen)
                        self.game.draw_hover(self.screen,mx//TSIZE,my//TSIZE)
                        self.game.animate.draw(self.screen)


                elif event.type == pygame.MOUSEBUTTONUP: 
                    my, mx = pygame.mouse.get_pos()[0]//TSIZE,pygame.mouse.get_pos()[1]//TSIZE
                    if self.game.animate.held:
                        if self.game.piece_selected():
                            if self.game.move_piece(mx,my):
                                self.game.update_game()
                                self.game.update_screen()
                            else:
                                self.game.deselect()
                                self.game.update_screen()
                    self.game.animate.unhold()
                    self.game.update_screen()


            # if self.game.piece_selected():
            #     self.game.

        
    def engine_play(self):
        self._engine_play = True
        self.run()
    def simulate_play(self):
        self.simulate = True
        self.run()
    
    def one_play(self):
        self.one_person = True
        self.run()
 
    def two_play(self):
        self.two_persons = True
        self.run()

    def _create_menu(self):
        menu = pygame_menu.Menu('Welcome', 400, 300, theme=pygame_menu.themes.THEME_BLUE)
        menu.add.button('Engine Play', self.engine_play)
        menu.add.button('Simulate last game', self.simulate_play)
        menu.add.button('Play Normal', self.one_play)
        menu.add.button('Play both', self.two_play)
        menu.add.button('Quit', pygame_menu.events.EXIT)
        return menu
import logging

LOG_FILENAME = 'logging_example.out'
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)

main = Main()
if os.path.isfile("move_log.log"):
    os.remove("move_log.log")

try:
    main.run()
except Exception as e:
    with open("Game.txt", "a") as file:
        file.write("--Error\n")
    print("main crashed. Error: %s", e)
    logging.exception('Got exception on main handler')    
    exit(-1)


# import chess
# import chess.engine


# engine = chess.engine.SimpleEngine.popen_uci("path/to/stockfish")


# board = chess.Board()


# while not board.is_game_over():
#     print(board)
#     result = engine.play(board, chess.engine.Limit(time=2.0))
#     board.push(result.move)


# engine.quit()