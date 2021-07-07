import pygame
import time
import sys

CROWN = pygame.transform.scale(pygame.image.load('crown.png'), (30,30))
WINDOW_WIDTH = 512
WINDOW_HEIGHT = 512

# Colours
BLACK = [(50, 50, 50), 'Black']
WHITE = [(245, 245, 245), 'White']
RED = [(210,0,0), 'Red']
GRAY = [(100,100,100), 'Gray']

BLOCK_SIZE = 64
ROWS = COLUMNS = 8
pieces = []

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

    def select(self, row, column):
        if self.selected:
            result = self._move(row, column)
            if not result:
                self.selected = None
                self.select(row, column)
        piece = self.board.get_board(row, column)
        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            return True
        return False


    def _move(self, row, column):
        piece = self.board.get_piece(row, column)
        if self.selected and piece == 0 and (row,column) in self.valid_moves:
            self.board.move(self.selected, row, column)
        else:
            return False

        return True

    def change_turn(self):
        if self.turn == RED:
            self.turn = WHITE
        else:
            self.turn = RED

    def get_valid_moves(self, piece):
        if piece:
            row, column = piece.row, piece.column
            for poss_row in range(row-1, row+2, 2):
                for poss_col in range(column-1, column+2, 2):
                    poss_piece = self.board.get_piece(poss_row,poss_col)
                    print(poss_piece)
                    # if non-empty square
                    if poss_piece:
                        # if opposite colour piece on square
                        if poss_piece.colour != piece.colour:
                            poss_jump_loc = self.board.get_piece(row+(poss_row-row), column+(poss_col-column))
                            # if you can jump over it
                            if not poss_jump_loc:
                                self.valid_moves.append(poss_row, poss_col)
                                jump = True
                    else:
                        self.valid_moves.append([poss_row, poss_col])
            print(self.valid_moves)
            self.valid_moves = []



class Board:
    def __init__(self):
        self.board = []
        self.white_pieces = self.black_pieces = 12
        self.white_kings = self.white_kings = 0
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
                        self.board[row].append(Piece(row, column, RED))
                    elif row > 4:
                        self.board[row].append(Piece(row, column, BLACK))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)
                    
    def draw(self, SCREEN):
        self.draw_grid(SCREEN)
        for row in range(ROWS):
            for column in range(COLUMNS):
                piece = self.board[row][column]
                if piece:
                    piece.draw_piece(SCREEN)
    
    def move(self, piece, row, column):
        if piece != 0:
            self.board[piece.row][piece.column], self.board[row][column] = self.board[row][column], self.board[piece.row][piece.column]
            piece.move(piece, row, column)
            if row == ROWS or row == 0:
                piece.make_king()
                if piece.colour == WHITE:
                    self.white_kings += 1
                else:
                    self.black_kings += 1

    def get_piece(self, row, column):
        return self.board[row][column]

    def find_loc_from_mouse(self, pos):
        x, y = pos
        row = y // BLOCK_SIZE
        column = x // BLOCK_SIZE
        return row, column

    
class Piece:
    PADDING = 10
    BORDER = 2
    def __init__(self, row, column, colour):
        self.row = row
        self.column = column
        self.colour = colour[0]
        self.colour_name = colour[1]
        self.is_king = False
        self.is_selected = False
        self.direction = True if self.colour == RED else False      # if true (red) move down the board, if false (white) move up the board
        self.x, self.y = 0, 0
        self.calc_pos(row, column)

    def __repr__(self):
        return f'{str(self.colour_name)},({self.row},{self.column})' 

    def calc_pos(self, row, column):
        self.x = BLOCK_SIZE * column + BLOCK_SIZE // 2
        self.y = BLOCK_SIZE * row + BLOCK_SIZE // 2

    def make_king(self):
        self.is_king = True

    def draw_piece(self, SCREEN):
        radius = BLOCK_SIZE // 2 - self.PADDING
        pygame.draw.circle(SCREEN, GRAY[0], (self.x, self.y), radius + self.BORDER)
        pygame.draw.circle(SCREEN, self.colour, (self.x, self.y), radius)
        if self.is_king:
            SCREEN.blit(CROWN, (self.x - (CROWN.get_width() // 2), self.y - (CROWN.get_height() // 2)))
    
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
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, column = game.board.find_loc_from_mouse(pos)
                game.board.move(game.board.get_piece(0,1), 4,3)
                piece = game.board.get_piece(row, column)
                game.get_valid_moves(piece)
        game.update()

main()
