# Imports
import pygame
import pygame.freetype
from pygame.locals import MOUSEBUTTONDOWN, QUIT
import time
import sys

# Constants / Files
CROWN = pygame.transform.scale(pygame.image.load('crown.png'), (30, 30))
FOOTER_HEIGHT = 256
GRID_HEIGHT = GRID_WIDTH = WINDOW_WIDTH = 512
WINDOW_HEIGHT = FOOTER_HEIGHT + GRID_HEIGHT
BLOCK_SIZE = 64
ROWS = COLUMNS = 8

# Define Colours
# [(Red, Green, Blue), 'Name for debugging']
FOOTER = [(10, 10, 10), 'Footer Black']
WHITE = [(245, 245, 245), 'White']
RED = [(210, 0, 0), 'Red']
BLACK = [(50, 50, 50), 'Black']
LIGHT_GRAY = [(100, 100, 100), 'Light Gray']
BLUE = [(150, 150, 210), 'Blue']


# Game Object; stores initialisation variables as well as helper, constant and reset methods
class Game:
    def __init__(self, SCREEN):
        self._init()
        self.fonts = {
            'bold': pygame.freetype.SysFont('Comic Sans MS', 30, bold=True),
            'normal': pygame.freetype.SysFont('Comic Sans MS', 30),
            'button': pygame.freetype.SysFont('Comic Sans MS', 24, italic=True)
        }
        self.screen = SCREEN

    def update(self):
        self.board.draw(self.screen)
        self.draw_footer()
        self.check_win()
        pygame.display.update()

    def draw_footer(self):
        pygame.draw.rect(
            self.screen, FOOTER[0], (0, GRID_HEIGHT, GRID_WIDTH, FOOTER_HEIGHT))
        if self.winner:
            win_message = self.fonts['bold'].render(
                f'{self.winner[1]} won!', WHITE[0])
            replay_button = self.fonts['button'].render(
                'Click anywhere in black box to play again.', WHITE[0])

            self.screen.blit(win_message[0], (30, GRID_HEIGHT + 90))
            self.screen.blit(replay_button[0], (30, GRID_HEIGHT + 140))
        else:
            turn_label = self.fonts['bold'].render(
                f'Turn: {self.turn[1]}', WHITE[1])
            self.screen.blit(turn_label[0], (30, GRID_HEIGHT + 30))

            red_title = self.fonts['bold'].render('Red:', WHITE[0])
            red_kings = self.fonts['normal'].render(
                f'Kings: {self.board.kings[RED[1]]}', WHITE[0])
            red_pieces = self.fonts['normal'].render(
                f'Pieces: {self.board.pieces[RED[1]]}', WHITE[0])
            self.screen.blit(red_title[0], (30, GRID_HEIGHT + 100))
            self.screen.blit(red_kings[0], (30, GRID_HEIGHT + 150))
            self.screen.blit(red_pieces[0], (30, GRID_HEIGHT + 190))

            black_title = self.fonts['bold'].render('Black:', WHITE[0])
            black_kings = self.fonts['normal'].render(
                f'Kings: {self.board.kings[BLACK[1]]}', WHITE[0])
            black_pieces = self.fonts['normal'].render(
                f'Pieces: {self.board.pieces[BLACK[1]]}', WHITE[0])
            self.screen.blit(
                black_title[0], (30 + GRID_WIDTH // 2, GRID_HEIGHT + 100))
            self.screen.blit(
                black_kings[0], (30 + GRID_WIDTH // 2, GRID_HEIGHT + 150))
            self.screen.blit(
                black_pieces[0], (30 + GRID_WIDTH // 2, GRID_HEIGHT + 190))

    def _init(self):
        self.winner = None
        self.selected = None
        self.board = Board(self)
        self.turn = BLACK
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

    def check_win(self):
        if self.board.pieces[RED[1]] == 0:
            self.winner = BLACK
        if self.board.pieces[BLACK[1]] == 0:
            self.winner = RED


# Board Class; stores all variables and methods relating to the grid.
# Includes drawings methods for the grid, and some helper functions.
class Board:
    def __init__(self, game):
        self.game = game
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
            self.game.change_turn()

    def get_piece(self, row, column):
        return self.board[row][column]

    def find_loc_from_mouse(self, pos):
        x, y = pos
        row = y // BLOCK_SIZE
        column = x // BLOCK_SIZE
        return row, column

    def draw_sugg_moves(self, SCREEN):
        for row, column, jumps in self.sugg_moves:
            pygame.draw.circle(SCREEN, BLUE[0], (column*BLOCK_SIZE+(
                BLOCK_SIZE//2), row*BLOCK_SIZE+(BLOCK_SIZE//2)), BLOCK_SIZE//5)

# Piece Class; stores all variables and methods relating to the checker itself.
# Includes drawings methods for the checker, as well as helper methods for position and state changes.


class Piece:
    PADDING = 10
    BORDER = 2

    def __init__(self, row, column, colour, board):
        self.row = row
        self.column = column
        self.colour = colour
        self.is_king = False
        self.board = board
        self.x, self.y = 0, 0
        self.calc_pos(row, column)

    def __repr__(self):
        return f'{str(self.colour[1])}, ({self.row},{self.column})'

    def calc_pos(self, row, column):
        self.x = BLOCK_SIZE * column + BLOCK_SIZE // 2
        self.y = BLOCK_SIZE * row + BLOCK_SIZE // 2

    def make_king(self):
        self.is_king = True

    def draw_piece(self, SCREEN):
        radius = BLOCK_SIZE // 2 - self.PADDING
        pygame.draw.circle(
            SCREEN, LIGHT_GRAY[0], (self.x, self.y), radius + self.BORDER)
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

# Main loop; Handles user input, and calls some initial game-related constants.


def main():
    global SCREEN, CLOCK
    pygame.init()
    CLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Checkers')
    game = Game(SCREEN)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if 0 < pos[0] < GRID_WIDTH and GRID_HEIGHT < pos[1] < WINDOW_HEIGHT and game.winner:
                    game.reset()
                else:
                    row, column = game.board.find_loc_from_mouse(pos)
                    piece = game.board.get_piece(row, column)
                    if piece:
                        if piece.colour == game.turn:
                            game.board.sugg_piece = piece
                            game.get_valid_moves(piece)
                    else:
                        picked_move = [
                            move for move in game.board.sugg_moves if move[0] == row and move[1] == column]
                        if picked_move:
                            row, column, jump = picked_move[0]
                            game.board.move(game.board.sugg_piece,
                                            row, column, jump)
                        game.board.sugg_moves = []

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game.winner = RED
        game.update()


main()
