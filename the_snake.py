"""Игра «Змейка» на Pygame.

Змейка движется по игровому полю, собирает яблоки и растёт.
Столкновение с собой сбрасывает игру. Сквозь стены змейка проходит.
"""

from random import randint

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

# Цвет границы ячейки:
BORDER_COLOR = (93, 216, 228)

# Цвет яблока:
APPLE_COLOR = (255, 0, 0)

# Цвет змейки:
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов.

    Содержит общие атрибуты игровых объектов: позицию на игровом поле
    и цвет. Определяет заготовку метода draw для отрисовки объекта.
    """

    def __init__(self, position=None, body_color=None):
        """Инициализирует базовые атрибуты игрового объекта.

        Args:
            position: координаты объекта (кортеж x, y). Если не заданы,
                используется центральная точка экрана.
            body_color: цвет объекта в формате RGB.
        """
        if position is None:
            position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Отрисовывает объект на игровом поле.

        Абстрактный метод, предназначен для переопределения
        в дочерних классах.
        """
        pass


class Apple(GameObject):
    """Класс яблока — игрового объекта, который собирает змейка.

    Наследуется от GameObject. Яблоко занимает одну ячейку игрового
    поля, его позиция выбирается случайно и меняется после того,
    как змейка его съест.
    """

    def __init__(self):
        """Инициализирует яблоко: задаёт цвет и случайную позицию."""
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position()

    def randomize_position(self):
        """Устанавливает случайную позицию яблока на игровом поле.

        Координаты выбираются так, чтобы яблоко оказалось в пределах
        поля: от 0 до (GRID_WIDTH - 1) * GRID_SIZE по горизонтали
        и от 0 до (GRID_HEIGHT - 1) * GRID_SIZE по вертикали.
        """
        self.position = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
        )

    def draw(self):
        """Отрисовывает яблоко на игровом поле."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс змейки — основного игрового объекта."""

    def __init__(self):
        """Инициализирует змейку в начальном состоянии."""
        super().__init__(body_color=SNAKE_COLOR)
        self.reset()

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None
        screen.fill(BOARD_BACKGROUND_COLOR)

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def update_direction(self):
        """Применяет отложенное направление движения."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Перемещает змейку на одну ячейку в текущем направлении."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Отрисовывает змейку на игровом поле, затирая след."""
        for position in self.positions[:-1]:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки.
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание следа — последнего удалённого сегмента.
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)
            self.last = None


def handle_keys(game_object):
    """Обрабатывает действия пользователя.

    Читает события Pygame: при закрытии окна завершает игру,
    при нажатии стрелок задаёт отложенное направление движения
    змейки. Разворот на 180 градусов запрещён.

    Args:
        game_object: объект змейки, для которого обрабатывается ввод.
    """
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
    # Инициализация PyGame.
    pygame.init()

    # Создание экземпляров классов.
    snake = Snake()
    apple = Apple()

    while True:
        clock.tick(SPEED)

        # Обработка действий пользователя.
        handle_keys(snake)

        # Обновление направления и позиции змейки.
        snake.update_direction()
        snake.move()

        # Проверка, съела ли змейка яблоко.
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position()

        # Проверка столкновения змейки с собой.
        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()

        # Отрисовка объектов.
        snake.draw()
        apple.draw()

        # Обновление экрана.
        pygame.display.update()


if __name__ == '__main__':
    main()
    