import pygame
import random

# Инициализация Pygame
pygame.init()

# Константы
SCREEN_WIDTH = 400  # +100 для панели счёта
SCREEN_HEIGHT = 600
GRID_SIZE = 30
COLUMNS = 10
ROWS = 20

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
COLORS = [
    (255, 0, 0),      # Красный
    (0, 255, 0),     # Зелёный
    (0, 0, 255),     # Синий
    (255, 255, 0),   # Жёлтый
    (255, 165, 0),   # Оранжевый
    (75, 0, 130),    # Фиолетовый
    (255, 192, 203) # Розовый
]

# Создание экрана
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 20)

# Фигуры (тетромино)
SHAPES = [
    [[1, 1, 1, 1]],                  # I
    [[1, 1], [1, 1]],              # O
    [[1, 1, 1], [0, 1, 0]],     # T
    [[1, 1, 1], [1, 0, 0]],     # L
    [[1, 1, 1], [0, 0, 1]],     # J
    [[0, 1, 1], [1, 1, 0]],     # S
    [[1, 1, 0], [0, 1, 1]]      # Z
]

class Piece:
    def __init__(self):
        self.shape = random.choice(SHAPES)
        self.color = random.choice(COLORS)
        self.x = COLUMNS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        rows = len(self.shape)
        cols = len(self.shape[0])
        rotated = [[0] * rows for _ in range(cols)]
        for r in range(rows):
            for c in range(cols):
                rotated[c][rows - 1 - r] = self.shape[r][c]
        return rotated

def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]
    for y in range(ROWS):
        for x in range(COLUMNS):
            if (x, y) in locked_positions:
                grid[y][x] = locked_positions[(x, y)]
    return grid

def draw_grid(surface, grid):
    for y in range(ROWS):
        for x in range(COLUMNS):
            pygame.draw.rect(surface, grid[y][x],
                           (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 0)
            pygame.draw.rect(surface, WHITE,
                           (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)


def draw_panel(surface, score, level, next_piece):
    # Панель справа (100 px)
    panel_x = COLUMNS * GRID_SIZE  # 300 px
    panel_width = 100
    pygame.draw.rect(surface, GRAY, (panel_x, 0, panel_width, SCREEN_HEIGHT))
    pygame.draw.rect(surface, WHITE, (panel_x, 0, panel_width, SCREEN_HEIGHT), 2)


    # Текст: Счёт
    score_text = font.render(f'Счёт:', True, WHITE)
    surface.blit(score_text, (panel_x + 10, 20))
    score_num = font.render(str(score), True, WHITE)
    surface.blit(score_num, (panel_x + 10, 50))


    # Текст: Уровень
    level_text = font.render(f'Уровень:', True, WHITE)
    surface.blit(level_text, (panel_x + 10, 100))
    level_num = font.render(str(level), True, WHITE)
    surface.blit(level_num, (panel_x + 10, 130))

    # Предпросмотр следующей фигуры
    next_text = font.render("Следующая:", True, WHITE)
    surface.blit(next_text, (panel_x + 10, 180))
    for i, row in enumerate(next_piece.shape):
        for j, cell in enumerate(row):
            if cell:
                pygame.draw.rect(surface, next_piece.color,
                               (panel_x + 20 + j * (GRID_SIZE // 2),
                                210 + i * (GRID_SIZE // 2), GRID_SIZE // 2, GRID_SIZE // 2), 0)
                pygame.draw.rect(surface, WHITE,
                               (panel_x + 20 + j * (GRID_SIZE // 2),
                                210 + i * (GRID_SIZE // 2), GRID_SIZE // 2, GRID_SIZE // 2), 1)

def valid_space(piece, grid):
    positions = convert_shape_format(piece)
    for pos in positions:
        x, y = pos
        if x < 0 or x >= COLUMNS or y >= ROWS:
            return False
        if y > 0 and grid[y][x] != BLACK:
            return False
    return True

def convert_shape_format(piece):
    positions = []
    shape = piece.shape
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                positions.append((piece.x + j, piece.y + i))
    return positions

def clear_lines(grid, locked):
    inc = 0  # количество удалённых строк
    # Проходим по строкам снизу вверх
    for i in range(len(grid) - 1, -1, -1):
        row = grid[i]
        # Проверяем, заполнена ли строка (все клетки не чёрные)
        if all(cell != BLACK for cell in row):
            inc += 1
            # Удаляем строку i, сдвигаем всё выше неё на одну клетку вниз
            for j in range(i, 0, -1):  # от i до 1
                for k in range(COLUMNS):
                    grid[j][k] = grid[j - 1][k]  # копируем строку j-1 в j
                    # Обновляем locked_positions
                    if (k, j - 1) in locked:
                        locked[(k, j)] = locked[(k, j - 1)]
                        del locked[(k, j - 1)]
                    else:
                        if (k, j) in locked:
                            del locked[(k, j)]
            # Очищаем верхнюю строку (индекс 0)
            for k in range(COLUMNS):
                grid[0][k] = BLACK
                if (k, 0) in locked:
                    del locked[(k, 0)]
            # После удаления строки проверяем ту же позицию снова (может быть новая полная строка)
            i += 1  # компенсируем уменьшение i в цикле
    return inc


def main():
    locked_positions = {}
    change_piece = False
    current_piece = Piece()
    next_piece = Piece()
    run = True
    fall_time = 0
    fall_speed = 0.35
    score = 0

    # Инициализируем level ДО цикла, чтобы он всегда существовал
    level = score // 500  # будет 0 при score=0

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        # Автоматическое падение фигуры
        if fall_time / 1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid):
                current_piece.y -= 1
                change_piece = True

        # Обработка событий клавиатуры
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1

                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1

                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1

                elif event.key == pygame.K_UP:
                    rotated_shape = current_piece.rotate()
                    old_shape = current_piece.shape
                    current_piece.shape = rotated_shape
                    if not valid_space(current_piece, grid):
                        current_piece.shape = old_shape  # возврат к старой форме

        # Отрисовка текущей фигуры на сетке
        piece_positions = convert_shape_format(current_piece)
        for pos in piece_positions:
            x, y = pos
            if y > -1:  # не рисуем выше верхней границы
                grid[y][x] = current_piece.color

        # Если пора сменить фигуру (достигла дна или уперлась в другую)
        if change_piece:
            for pos in piece_positions:
                x, y = pos
                locked_positions[(x, y)] = current_piece.color
            current_piece = next_piece
            next_piece = Piece()
            change_piece = False

            # Начисляем очки за удалённые линии
            cleared_lines = clear_lines(grid, locked_positions)
            score += cleared_lines * 100  # 100 очков за линию

            # Обновляем уровень и скорость
            level = score // 500
            fall_speed = max(0.1, 0.35 - level * 0.05)  # минимум 0.1 сек

        # Проверяем, не проиграна ли игра (блоки достигли верха)
        if any((x, 0) in locked_positions for x in range(COLUMNS)):
            run = False

        # Отрисовка всего на экран
        screen.fill(BLACK)
        draw_grid(screen, grid)  # игровое поле
        draw_panel(screen, score, level, next_piece)  # панель статистики
        pygame.display.update()

    # Экран "GAME OVER"
    screen.fill(BLACK)
    game_over_text = font.render("GAME OVER", True, WHITE)
    score_text = font.render(f"Счёт: {score}", True, WHITE)
    level_text = font.render(f"Уровень: {level}", True, WHITE)

    # Центрируем тексты
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 10))
    screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))

    pygame.display.update()
    pygame.time.delay(3000)  # пауза 3 секунды перед закрытием

    pygame.quit()

# Запуск игры
if __name__ == "__main__":
    main()
