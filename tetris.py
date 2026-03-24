#cmd 
#pip install pygame
import random
import sys

import pygame


CELL_SIZE = 30
COLS = 10
ROWS = 20
PANEL_WIDTH = 200
WIDTH = COLS * CELL_SIZE + PANEL_WIDTH
HEIGHT = ROWS * CELL_SIZE
FPS = 60

FALL_EVENT = pygame.USEREVENT + 1
FALL_INTERVAL_MS = 350


COLORS = {
    "I": (0, 240, 240),
    "O": (240, 240, 0),
    "T": (160, 0, 240),
    "S": (0, 240, 0),
    "Z": (240, 0, 0),
    "J": (0, 0, 240),
    "L": (240, 160, 0),
    "grid": (45, 45, 55),
    "bg": (20, 20, 28),
    "panel": (30, 30, 40),
    "text": (230, 230, 240),
    "ghost": (120, 120, 140),
}


SHAPES = {
    "I": [
        [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],
        [[0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 1, 0]],
    ],
    "O": [
        [[1, 1], [1, 1]],
    ],
    "T": [
        [[0, 1, 0], [1, 1, 1], [0, 0, 0]],
        [[0, 1, 0], [0, 1, 1], [0, 1, 0]],
        [[0, 0, 0], [1, 1, 1], [0, 1, 0]],
        [[0, 1, 0], [1, 1, 0], [0, 1, 0]],
    ],
    "S": [
        [[0, 1, 1], [1, 1, 0], [0, 0, 0]],
        [[0, 1, 0], [0, 1, 1], [0, 0, 1]],
    ],
    "Z": [
        [[1, 1, 0], [0, 1, 1], [0, 0, 0]],
        [[0, 0, 1], [0, 1, 1], [0, 1, 0]],
    ],
    "J": [
        [[1, 0, 0], [1, 1, 1], [0, 0, 0]],
        [[0, 1, 1], [0, 1, 0], [0, 1, 0]],
        [[0, 0, 0], [1, 1, 1], [0, 0, 1]],
        [[0, 1, 0], [0, 1, 0], [1, 1, 0]],
    ],
    "L": [
        [[0, 0, 1], [1, 1, 1], [0, 0, 0]],
        [[0, 1, 0], [0, 1, 0], [0, 1, 1]],
        [[0, 0, 0], [1, 1, 1], [1, 0, 0]],
        [[1, 1, 0], [0, 1, 0], [0, 1, 0]],
    ],
}


LINE_SCORES = {0: 0, 1: 100, 2: 300, 3: 500, 4: 800}


class Piece:
    def __init__(self, shape_name):
        self.name = shape_name
        self.rotations = SHAPES[shape_name]
        self.rotation = 0
        self.shape = self.rotations[self.rotation]
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = -1

    def rotate(self, direction=1):
        self.rotation = (self.rotation + direction) % len(self.rotations)
        self.shape = self.rotations[self.rotation]

    def cells(self, offset_x=0, offset_y=0):
        for row_idx, row in enumerate(self.shape):
            for col_idx, value in enumerate(row):
                if value:
                    yield self.x + col_idx + offset_x, self.y + row_idx + offset_y


class TetrisGame:
    def __init__(self):
        self.board = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.game_over = False
        self.bag = []
        self.current = self._new_piece()
        self.next_piece = self._new_piece()

    def _refill_bag(self):
        names = list(SHAPES.keys())
        random.shuffle(names)
        self.bag.extend(names)

    def _new_piece(self):
        if not self.bag:
            self._refill_bag()
        return Piece(self.bag.pop())

    def is_valid_position(self, piece, dx=0, dy=0):
        for x, y in piece.cells(dx, dy):
            if x < 0 or x >= COLS:
                return False
            if y >= ROWS:
                return False
            if y >= 0 and self.board[y][x] is not None:
                return False
        return True

    def lock_piece(self):
        for x, y in self.current.cells():
            if y < 0:
                self.game_over = True
                return
            self.board[y][x] = self.current.name

        cleared = self.clear_lines()
        self.lines += cleared
        self.score += LINE_SCORES[cleared] * self.level
        self.level = 1 + self.lines // 10

        self.current = self.next_piece
        self.next_piece = self._new_piece()

        if not self.is_valid_position(self.current):
            self.game_over = True

    def clear_lines(self):
        new_board = [row for row in self.board if any(cell is None for cell in row)]
        lines_cleared = ROWS - len(new_board)
        for _ in range(lines_cleared):
            new_board.insert(0, [None for _ in range(COLS)])
        self.board = new_board
        return lines_cleared

    def move(self, dx, dy):
        if self.is_valid_position(self.current, dx=dx, dy=dy):
            self.current.x += dx
            self.current.y += dy
            return True
        if dy > 0:
            self.lock_piece()
        return False

    def rotate(self):
        original_rotation = self.current.rotation
        self.current.rotate(1)

        for kick in [0, -1, 1, -2, 2]:
            if self.is_valid_position(self.current, dx=kick, dy=0):
                self.current.x += kick
                return

        self.current.rotation = original_rotation
        self.current.shape = self.current.rotations[original_rotation]

    def hard_drop(self):
        distance = 0
        while self.move(0, 1):
            distance += 1
        self.score += distance * 2

    def ghost_y_offset(self):
        offset = 0
        while self.is_valid_position(self.current, dy=offset + 1):
            offset += 1
        return offset

    def reset(self):
        self.__init__()


def draw_cell(surface, x, y, color, outline=True):
    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(surface, color, rect)
    if outline:
        pygame.draw.rect(surface, (10, 10, 15), rect, 1)


def draw_board(screen, game):
    board_surface = pygame.Surface((COLS * CELL_SIZE, ROWS * CELL_SIZE))
    board_surface.fill(COLORS["bg"])

    for y in range(ROWS):
        for x in range(COLS):
            pygame.draw.rect(
                board_surface,
                COLORS["grid"],
                pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                1,
            )
            cell = game.board[y][x]
            if cell is not None:
                draw_cell(board_surface, x, y, COLORS[cell])

    ghost_offset = game.ghost_y_offset()
    for x, y in game.current.cells(offset_y=ghost_offset):
        if y >= 0:
            draw_cell(board_surface, x, y, COLORS["ghost"], outline=False)

    for x, y in game.current.cells():
        if y >= 0:
            draw_cell(board_surface, x, y, COLORS[game.current.name])

    screen.blit(board_surface, (0, 0))


def draw_panel(screen, game, font, small_font):
    panel_x = COLS * CELL_SIZE
    panel_rect = pygame.Rect(panel_x, 0, PANEL_WIDTH, HEIGHT)
    pygame.draw.rect(screen, COLORS["panel"], panel_rect)

    title = font.render("TETRIS", True, COLORS["text"])
    score = small_font.render(f"Score: {game.score}", True, COLORS["text"])
    lines = small_font.render(f"Lines: {game.lines}", True, COLORS["text"])
    level = small_font.render(f"Level: {game.level}", True, COLORS["text"])

    screen.blit(title, (panel_x + 20, 20))
    screen.blit(score, (panel_x + 20, 90))
    screen.blit(lines, (panel_x + 20, 120))
    screen.blit(level, (panel_x + 20, 150))

    next_text = small_font.render("Next", True, COLORS["text"])
    screen.blit(next_text, (panel_x + 20, 210))

    preview_origin_x = panel_x + 40
    preview_origin_y = 250
    for row_idx, row in enumerate(game.next_piece.shape):
        for col_idx, value in enumerate(row):
            if value:
                px = preview_origin_x + col_idx * CELL_SIZE
                py = preview_origin_y + row_idx * CELL_SIZE
                rect = pygame.Rect(px, py, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, COLORS[game.next_piece.name], rect)
                pygame.draw.rect(screen, (10, 10, 15), rect, 1)

    controls = [
        "Controls",
        "Left/Right: Move",
        "Down: Soft drop",
        "Up: Rotate",
        "Space: Hard drop",
        "R: Restart",
        "Esc: Quit",
    ]
    y = HEIGHT - 180
    for line in controls:
        text = small_font.render(line, True, COLORS["text"])
        screen.blit(text, (panel_x + 20, y))
        y += 24


def update_fall_speed(game):
    interval = max(70, FALL_INTERVAL_MS - (game.level - 1) * 45)
    pygame.time.set_timer(FALL_EVENT, interval)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Python Tetris")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 38, bold=True)
    small_font = pygame.font.SysFont("consolas", 22)

    game = TetrisGame()
    update_fall_speed(game)

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == FALL_EVENT and not game.game_over:
                game.move(0, 1)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_r:
                    game.reset()
                    update_fall_speed(game)
                    continue

                if game.game_over:
                    continue

                if event.key == pygame.K_LEFT:
                    game.move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    game.move(1, 0)
                elif event.key == pygame.K_DOWN:
                    if game.move(0, 1):
                        game.score += 1
                elif event.key == pygame.K_UP:
                    game.rotate()
                elif event.key == pygame.K_SPACE:
                    game.hard_drop()

        update_fall_speed(game)

        screen.fill(COLORS["bg"])
        draw_board(screen, game)
        draw_panel(screen, game, font, small_font)

        if game.game_over:
            overlay = pygame.Surface((COLS * CELL_SIZE, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            game_over_text = font.render("GAME OVER", True, (255, 120, 120))
            restart_text = small_font.render("Press R to restart", True, COLORS["text"])
            text_rect = game_over_text.get_rect(center=(COLS * CELL_SIZE // 2, HEIGHT // 2 - 20))
            restart_rect = restart_text.get_rect(center=(COLS * CELL_SIZE // 2, HEIGHT // 2 + 30))
            screen.blit(game_over_text, text_rect)
            screen.blit(restart_text, restart_rect)

        pygame.display.flip()


if __name__ == "__main__":
    main()