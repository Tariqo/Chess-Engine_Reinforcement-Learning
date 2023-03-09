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
        self.game = Game()
        pygame.display.set_caption("Menu")
        self.menu = self._create_menu()
        # self.menu.mainloop(self.game_display)


    def run(self):
        display = self.screen
        running = True
        while running:
            self._event_handler()
            pygame.display.update()
            self.game._draw_board(display)
            self.game._draw_pieces(display)

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
                pass
        
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