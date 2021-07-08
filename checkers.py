import pygame
from pygame.locals import MOUSEBUTTONDOWN, QUIT
import time
import sys

CROWN = pygame.transform.scale(pygame.image.load('crown.png'), (30, 30))
WINDOW_WIDTH = 512
WINDOW_HEIGHT = 512

# Colours
BLACK = [(50, 50, 50), 'Black']
WHITE = [(245, 245, 245), 'White']
RED = [(210, 0, 0), 'Red']
GRAY = [(100, 100, 100), 'Gray']
BLUE = [(0, 0, 210), 'Blue']
BLOCK_SIZE = 64
ROWS = COLUMNS = 8


class Game:
    def __init__(self, SCREEN):
        self._init()
        self.screen = SCREEN

    def update(self):
        self.board.draw(self.screen)
        pygame.display.update()

    def _init(self):
        self.selected = None
        self.board = Board()
        self.turn = RED
        self.valid_moves = []

    def reset(self):
        self._init()

    def change_turn(self):
        if self.turn == RED:
            self.turn = BLACK
        else:
            self.turn = RED

    def get_valid_moves(self, piece):
        jumps = []
        valid_moves = self.valid_moves = []
        if piece:
            row, column = piece.row, piece.column
            if piece.colour == BLACK or piece.is_king:
                poss_row = row - 1
                for poss_col in range(column-1, column+2, 2):
                    # if on the board
                    if (0 <= poss_row <= 7) and (0 <= poss_col <= 7):
                        poss_piece = self.board.get_piece(
                            poss_row, poss_col)
                        # if non-empty square
                        if poss_piece:
                            # if opposite colour piece on square
                            if poss_piece.colour != piece.colour:
                                if (0 <= 2*poss_row-row <= 7) and (0 <= 2*poss_col-column <= 7):
                                    poss_jump_loc = self.board.get_piece(
                                        2*poss_row-row, 2*poss_col-column)
                                        # if you can jump over it
                                    if not poss_jump_loc:
                                        jumps.append((poss_row, poss_col))
                                        valid_moves.append(
                                            (2*poss_row-row, 2*poss_col-column, poss_piece))
                        else:
                            valid_moves.append((poss_row, poss_col, None))

            if piece.colour == RED or piece.is_king:
                poss_row = row + 1
                for poss_col in range(column-1, column+2, 2):
                    # if on the board
                    if (0 <= poss_row <= 7) and (0 <= poss_col <= 7):
                        poss_piece = self.board.get_piece(
                            poss_row, poss_col)
                        # if non-empty square
                        if poss_piece:
                            # if opposite colour piece on square
                            if poss_piece.colour != piece.colour:
                                if (0 <= 2*poss_row-row <= 7) and (0 <= 2*poss_col-column <= 7):
                                    poss_jump_loc = self.board.get_piece(
                                        2*poss_row-row, 2*poss_col-column)
                                    # if you can jump over it
                                    if not poss_jump_loc:
                                        valid_moves.append(
                                            (2*poss_row-row, 2*poss_col-column, poss_piece))
                        else:
                            valid_moves.append((poss_row, poss_col, None))
        self.board.sugg_moves = valid_moves
        return valid_moves


class Board:
    def __init__(self):
        self.board = []
        self.pieces = {
            RED[1]: 12,
            BLACK[1]: 12
        }
        self.kings = {
            RED[1]: 0,
            BLACK[1]: 0
        }
        self.sugg_moves = []
        self.sugg_piece = ''
        self.create_board()

    def draw_grid(self, SCREEN):
        SCREEN.fill(WHITE[0])
        for row in range(ROWS):
            for column in range(row % 2, COLUMNS, 2):
                pygame.draw.rect(SCREEN, BLACK[0], (row*BLOCK_SIZE, column*BLOCK_SIZE,
                                                    BLOCK_SIZE, BLOCK_SIZE))

    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for column in range(COLUMNS):
                if column % 2 == ((row+1) % 2):
                    if row < 3:
                        self.board[row].append(Piece(row, column, RED, self))
                    elif row > 4:
                        self.board[row].append(Piece(row, column, BLACK, self))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)

    def draw(self, SCREEN):
        self.draw_grid(SCREEN)
        self.draw_sugg_moves(SCREEN)
        for row in range(ROWS):
            for column in range(COLUMNS):
                piece = self.board[row][column]
                if piece:
                    piece.draw_piece(SCREEN)

    def move(self, piece, row, column, jump):
        if piece:
            self.board[piece.row][piece.column], self.board[row][column] = self.board[row][column], self.board[piece.row][piece.column]
            piece.move(piece, row, column)
            if row == (ROWS-1) or row == 0:
                piece.make_king()
                self.kings[piece.colour[1]] += 1
            if jump:
                jump.remove()

    def get_piece(self, row, column):
        return self.board[row][column]

    def find_loc_from_mouse(self, pos):
        x, y = pos
        row = y // BLOCK_SIZE
        column = x // BLOCK_SIZE
        return row, column

    def draw_sugg_moves(self, SCREEN):
        for row, column, jumps in self.sugg_moves:
            pass
        #pygame.draw.circle(SCREEN, BLUE[0], (column*BLOCK_SIZE+(BLOCK_SIZE//2), row*BLOCK_SIZE+(BLOCK_SIZE//2)), BLOCK_SIZE//5)


class Piece:
    PADDING = 10
    BORDER = 2

    def __init__(self, row, column, colour, board):
        self.row = row
        self.column = column
        self.colour = colour
        self.colour_name = colour[1]
        self.is_king = False
        self.is_selected = False
        self.board = board
        # if true (red) move down the board, if false (black) move up the board
        self.direction = 1 if self.colour == RED else -1
        self.x, self.y = 0, 0
        self.calc_pos(row, column)

    def __repr__(self):
        return f'{str(self.colour_name)}, ({self.row},{self.column})'

    def calc_pos(self, row, column):
        self.x = BLOCK_SIZE * column + BLOCK_SIZE // 2
        self.y = BLOCK_SIZE * row + BLOCK_SIZE // 2

    def make_king(self):
        self.is_king = True

    def draw_piece(self, SCREEN):
        radius = BLOCK_SIZE // 2 - self.PADDING
        pygame.draw.circle(
            SCREEN, GRAY[0], (self.x, self.y), radius + self.BORDER)
        pygame.draw.circle(SCREEN, self.colour[0], (self.x, self.y), radius)
        if self.is_king:
            SCREEN.blit(CROWN, (self.x - (CROWN.get_width() // 2),
                        self.y - (CROWN.get_height() // 2)))

    def remove(self):
        self.board.board[self.row][self.column] = 0
        self.board.pieces[self.colour[1]] -= 1
        if self.is_king:
            self.board.kings[self.colour[1]] -= 1

    def move(self, piece, row, column):
        self.row = row
        self.column = column
        self.calc_pos(row, column)

def main():
    global SCREEN, CLOCK
    pygame.init()
    CLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    game = Game(SCREEN)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, column = game.board.find_loc_from_mouse(pos)
                piece = game.board.get_piece(row, column)
                if piece:
                    game.board.sugg_piece = piece
                    game.get_valid_moves(piece)
                else:
                    picked_move = [move for move in game.board.sugg_moves if move[0] == row and move[1] == column]
                    if picked_move:
                        row, column, jump = picked_move[0]
                        game.board.move(game.board.sugg_piece, row, column, jump)
                    game.board.sugg_moves = []
        game.update()


main()
