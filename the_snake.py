from random import choice, randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE


# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 10

start_x = GRID_WIDTH // 2
start_y = GRID_HEIGHT // 2


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

pygame.display.set_caption('Змейка')

clock = pygame.time.Clock()


class GameObject():
    """Базовый класс для всех игровых объектов.
    Содержит общие для всех объектов атрибуты: позицию на игровом поле
    и цвет отрисовки. От этого класса наследуются Snake, Apple, Barrier
    и другие игровые сущности.
    """

    def __init__(self, position=None, body_color=None):
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Отрисовывает объект."""
        pass


class Apple(GameObject):
    """Класс обычного яблока.
    При съедании увеличивает длину змейки.
    """

    def __init__(self):
        super().__init__(None, None)
        self.position = None
        self.body_color = APPLE_COLOR

    def randomize_position(self, stones, snake_positions):
        """Перемещает яблоко в случайную свободную клетку."""
        while True:
            col = randint(0, GRID_WIDTH - 1)
            row = randint(0, GRID_HEIGHT - 1)
            self.position = (col, row)
            if is_cell_free(col, row, stones, snake_positions):
                self.position = (col, row)
                return

    def draw(self):
        """Отрисовывает яблоко на экране."""
        x = self.position[0] * GRID_SIZE
        y = self.position[1] * GRID_SIZE
        rect = pygame.Rect((x, y), (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class PoisonosApple(Apple):
    """Класс ядовитого яблока.
    Появляется периодически, при
    съедании уменьшает длину змейки.
    """

    def __init__(self):
        super().__init__()
        self.position = None
        self.body_color = (255, 0, 255)
        self.pison_timer = 0
        self.poison_interval = randint(10, 50)
        self.poison_duration = randint(30, 60)
        self.is_visible = False
        self.timer = self.poison_interval

    def update(self, stones, snake_position):
        """Обновляет состояние ядовитого яблока.
        Перемещает ядовитое яблоко в случайную свободную клетку.
        """
        self.timer += 1
        if not self.is_visible:
            if self.timer >= self.poison_interval:
                self.is_visible = True
                self.timer = 0
                self.randomize_position(stones, snake_position)
        else:
            if (
                self.timer >= self.poison_duration
                or self.position == snake_position[0]
            ):
                self.is_visible = False
                self.timer = 0

    def draw(self):
        """Отрисовывает ядовитое яблоко, если оно видимо."""
        if not self.is_visible:
            return
        x = self.position[0] * GRID_SIZE
        y = self.position[1] * GRID_SIZE
        rect = pygame.Rect((x, y), (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Barrier(GameObject):
    """Класс препятствий на игровом поле."""

    def __init__(self):
        super().__init__(None, None)
        self.randomize_position()
        self.color = (128, 128, 128)
        self.hight = 40

    def randomize_position(self):
        """Устанавливает препятствие в случайную свободную клетку."""
        col = randint(0, GRID_WIDTH - 1)
        row = randint(0, GRID_HEIGHT - 1)
        self.position = (col, row)

    def draw(self):
        """Отрисовывает препятствие на экране."""
        x = self.position[0] * GRID_SIZE
        y = self.position[1] * GRID_SIZE
        rect = pygame.Rect((x, y), (GRID_SIZE, self.hight))
        pygame.draw.rect(screen, self.color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс змейки.
    Управляет телом, движением,
    поеданием яблок и столкнивениями.
    """

    def __init__(self):
        super().__init__(None, None)
        self.positions = [(start_x, start_y)]
        self.body_color = SNAKE_COLOR
        self.length = 2
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        directions = [UP, DOWN, LEFT, RIGHT]
        self.positions = [(start_x, start_y)]
        self.body_color = SNAKE_COLOR
        self.length = 2
        self.direction = choice(directions)
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def move(self):
        """Перемещает змейку на одну клетку в текущем направлении."""
        now_head_position = self.get_head_position()
        new_x = (now_head_position[0] + self.direction[0]) % GRID_WIDTH
        new_y = (now_head_position[1] + self.direction[1]) % GRID_HEIGHT
        new_head_position = (new_x, new_y)
        self.positions.insert(0, new_head_position)
        self.last = self.positions[-1]
        if len(self.positions) > self.length:
            self.positions.pop()

    def update_direction(self):
        """Применяет отложенное направление движения."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def eat_apple(self, apple, poison_apple, stones, snake_positions):
        """Обрабатывает поедание яблок."""
        if apple.position == self.positions[0]:
            self.length += 1
            apple.randomize_position(stones, snake_positions)
        elif (
            poison_apple.is_visible
            and poison_apple.position == self.positions[0]
        ):
            self.length -= 1
            self.positions.pop()
        if self.length <= 0:
            self.reset()

    def crush_snake(self):
        """Проверяет столкновение головы змейки с её телом."""
        for piece in range(1, len(self.positions)):
            if self.positions[0] == self.positions[piece]:
                self.reset()
                break

    def crush_stone(self, stones):
        """Проверяет столкновение головы змейки с препятствиями."""
        head_x, head_y = self.positions[0]
        for stone in stones:
            stone_x, stone_y = stone.position
            if head_x == stone_x and stone_y <= head_y <= stone_y + 1:
                self.reset()
                break

    def draw(self):
        """Отрисовывает змейку на экране.
        Рисует все сегменты тела, голову и затирает хвост цветом фона.
        """
        for position in self.positions[:-1]:
            x = position[0] * GRID_SIZE
            y = position[1] * GRID_SIZE
            rect = pygame.Rect((x, y), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        head_x = self.positions[0][0] * GRID_SIZE
        head_y = self.positions[0][1] * GRID_SIZE
        head_rect = pygame.Rect((head_x, head_y), (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        if self.last:
            last_x = self.last[0] * GRID_SIZE
            last_y = self.last[1] * GRID_SIZE
            last_rect = pygame.Rect((last_x, last_y), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)


def is_cell_free(x, y, stones, snake_positions):
    """Проверяет, свободна ли клетка на игровом поле."""
    for stone in stones:
        if stone.position == (x, y):
            return False
    return (x, y) not in snake_positions


def handle_keys(game_object):
    """Функция обработки действий пользователя."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Запускает основной игровой цикл."""
    pygame.init()
    snake = Snake()
    apple = Apple()
    poison_apple = PoisonosApple()
    stone1 = Barrier()
    stone2 = Barrier()
    stone3 = Barrier()
    stone4 = Barrier()
    stone5 = Barrier()
    stones = [stone1, stone2, stone3, stone4, stone5]
    apple.randomize_position(stones, snake.positions)
    while True:
        clock.tick(SPEED)
        screen.fill(BOARD_BACKGROUND_COLOR)
        handle_keys(snake)
        snake.move()
        snake.update_direction()
        snake.eat_apple(apple, poison_apple, stones, snake.positions)
        poison_apple.update(stones, snake.positions)
        snake.crush_snake()
        snake.crush_stone(stones)

        snake.draw()
        apple.draw()
        poison_apple.draw()
        for stone in stones:
            stone.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
