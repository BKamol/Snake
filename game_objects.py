import random


class GameObject:
    """
    Все игровые объекты наследуются от этого класса.
    Объект представляет из себя список координат [x, y]
    Атрибуты:
    _coordinates: list - координаты объекта
    _size - размер или количество

    Атрибуты класса:
    CellSize - размер клетки в игровом поле
    BoardWidth - ширина игрового поля
    BoardHeight - высота игрового поля
    """
    CellSize = 20
    BoardWidth = 40
    BoardHeight = 30

    def __init__(self):
        self._coordinates = []
        self._size = 0

    @property
    def coordinates(self):
        return self._coordinates

    @coordinates.setter
    def coordinates(self, new_coords):
        self._coordinates = new_coords

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, new_size):
        self._size = new_size

    def add_random_item(self, avoid_object=None, amount=1):
        """
        Добавляет к объекту случайную пару координат.
        Параметры:
        avoid_object: GameObject - нова пара не будет пересекать объект
        amount: int - количество добавляемых случайных координат
        """
        for _ in range(amount):
            x = random.randint(2, self.BoardWidth - 2)
            y = random.randint(2, self.BoardHeight - 2)

            if avoid_object is not None:
                while [x, y] in avoid_object:
                    x = random.randint(2, self.BoardWidth - 2)
                    y = random.randint(2, self.BoardHeight - 2)

            self.size += 1
            self.coordinates.append([x, y])

    def __getitem__(self, index):
        return self.coordinates[index]

    def __setitem__(self, index, value):
        self.coordinates[index] = value

    def __iter__(self):
        yield from self.coordinates


class Apple(GameObject):
    pass


class Obstacle(GameObject):
    pass


class Snake(GameObject):
    """
    Класс для змеи.
    Голова змеи находится в конце списка.
    """
    def __init__(self, initial_size=3, initial_direction="down"):
        super().__init__()
        self.size = initial_size
        self._direction = initial_direction
        self.is_alive = True
        self._score = 0
        x = random.randint(2, self.BoardWidth-2)
        y = random.randint(2, self.BoardWidth-2)
        self.init_coordinates(x, y)

    def init_coordinates(self, x, y):
        if self._direction == 'down':
            self.coordinates = [[x, y+i] for i in range(self.size)]
        elif self._direction == 'up':
            self.coordinates = [[x, y-i] for i in range(self.size)]
        elif self._direction == 'right':
            self.coordinates = [[x+i, y] for i in range(self.size)]
        elif self._direction == 'left':
            self.coordinates = [[x-i, y] for i in range(self.size)]

    @property
    def score(self):
        return self._score

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, new_direction):
        """
        Меняет направление змеи
        """
        if new_direction == 'right' and self._direction != 'left':
            self._direction = 'right'
        elif new_direction == 'left' and self._direction != 'right':
            self._direction = 'left'
        elif new_direction == 'up' and self._direction != 'down':
            self._direction = 'up'
        elif new_direction == 'down' and self._direction != 'up':
            self._direction = 'down'
        self.move()

    def move(self, grow=False):
        """
        Двигает змею на 1 клекту в направлении _direction
        Параметры:
        grow: bool - добавляет к змее 1 клетку размера при значении True
        """
        x, y = self.coordinates[-1]
        if self.direction == 'right':
            x += 1
        elif self.direction == 'left':
            x -= 1
        elif self.direction == 'up':
            y -= 1
        else:
            y += 1

        if x < 0:
            x = self.BoardWidth
        elif x >= self.BoardWidth:
            x = 0

        if y < 0:
            y = self.BoardHeight
        elif y >= self.BoardHeight:
            y = 0

        if grow:
            self.size += 1
            self._score += 1
        else:
            self.coordinates.pop(0)
        self.coordinates.append([x, y])

    def get_head_coords(self):
        return self.coordinates[-1]

    def check_collision(self, object, remove=False):
        """
        Проверяет столкновение змеи c object
        Параметры:
        object: GameObject - объект, проверяемый на столкновение
        remove: bool - удалет клетку объекта object
        """
        for pos in object:
            if pos in self.coordinates:
                if remove:
                    object.coordinates.remove(pos)
                return True
        return False

    def check_self_collision(self):
        """
        Проверяет столкновение змеи с собой
        """
        for i in range(self.size-1):
            if self.coordinates[i] == self.coordinates[-1]:
                return True
        return False
