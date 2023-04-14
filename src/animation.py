import pygame

from game_vars import *

class Animate:

    def __init__(self):
        self.piece = None
        self.held = False
        self.mX = 0
        self.mY = 0
        self.row = 0
        self.col = 0

    def draw(self, surface):
        piece_img = self.piece.sprite
        img_center = (self.mX, self.mY)
        # print((self.mX, self.mY))
        img_rect = piece_img.get_rect(center=img_center)
        surface.blit(piece_img,img_rect)


    def update_mouse(self, mx,my):
        self.mX, self.mY = mx,my

    def org_RF(self, mx, my):
        self.row, self.col = mx, my

    def hold(self, piece):
        self.piece = piece
        self.held = True

    def unhold(self):
        self.piece = None
        self.held = False