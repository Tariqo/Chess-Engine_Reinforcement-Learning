import pygame
import sys

from game import *
from game_vars import *
from board import *
import pygame_menu
from pygame.locals import *
class Main:
    
    def __init__(self):
        pygame.init()
        self.game_display = pygame.display.set_mode((WIDTH, WIDTH))
        self.screen = pygame.display.set_mode( (WIDTH, HEIGHT) )
        pygame.display.set_caption('Chess')
        self.game = Game(self.screen)
        pygame.display.set_caption("Menu")
        self.menu = self._create_menu()
        # self.menu.mainloop(self.game_display)


    def run(self):
        display = self.screen
        running = True
        self.game._draw_board(display)
        self.game._draw_pieces(display)
        while running:
            self._event_handler()
            pygame.display.update()


    def _event_handler(self):
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
                        self.game.animate.org_RF(mx,my)  
                        self.game.animate.hold(self.game.selected_piece)  

            elif event.type == pygame.MOUSEMOTION:
                mx , my = pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]
                self.game.animate.update_mouse(mx,my)
                if self.game.animate.held:
                    self.game.animate.update_mouse(mx,my)
                    self.game.update_screen()
                    self.game._draw_highlights(self.screen)
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

        
    def _start_the_game(slef):
        # Do the job here !
        pass
    
    def _create_menu(self):
        menu = pygame_menu.Menu('Welcome', 400, 300, theme=pygame_menu.themes.THEME_BLUE)
        menu.add.button('Play', self._start_the_game)
        menu.add.button('Quit', pygame_menu.events.EXIT)
        return menu

main = Main()
main.run()