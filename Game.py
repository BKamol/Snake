import sys
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPen, QBrush
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QMainWindow, \
                            QGraphicsView, QGraphicsScene, QMessageBox
from game_objects import Snake, Apple, Obstacle, GameObject


class Game(QMainWindow):
    """
    Окно для отображения поля игры и строки, показывающей очки
    """
    WIDTH = 800
    HEIGHT = 600

    def __init__(self, snake_size=3, snake_direction="down"):
        super().__init__()

        self.statusbar = self.statusBar()
        self.board = Board(self, snake_size, snake_direction)

        self.setCentralWidget(self.board)
        self.setWindowTitle('Snake')
        self.resize(self.WIDTH, self.HEIGHT)
        self.center()

        self.show()

    def center(self):
        """
        Центрирование окна
        """
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2),
                  int((screen.height() - size.height()) / 2))


class Board(QGraphicsView):
    """
    Игровое поле
    Атрибуты класса:
    msg2statusbar: pyqtSignal - сигнал, отправляемый статус бару родителя
    GameTimer: int - период обновления игры
    ObstacleTiemr: int - период появления препятствия
    """
    msg2statusbar = pyqtSignal(str)
    GameTimer = 40
    ObstacleTimer = 10000

    def __init__(self, parent, snake_size, snake_direction):
        super().__init__(parent)
        self.msg2statusbar.connect(parent.statusbar.showMessage)
        self.initBoard()

        self.snake_size = snake_size
        self.snake_direction = snake_direction
        self.initGame(snake_size, snake_direction)

    def initBoard(self):
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setGeometry(0, 0, Game.WIDTH, Game.HEIGHT)
        self.center()
        self.setSceneRect(0, 0, self.width(), self.height())
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def initGame(self, snake_size, snake_direction):
        self.snake = Snake(snake_size, snake_direction)
        self.apple = Apple()
        self.obstacle = Obstacle()
        self.game_timer = QTimer()
        self.obstacle_timer = QTimer()
        self.paused = False

        self.game_timer.timeout.connect(self.update_game)
        self.obstacle_timer.timeout.connect(self.generate_obstacle)
        self.game_timer.start(self.GameTimer)
        self.obstacle_timer.start(self.ObstacleTimer)
        self.apple.add_random_item(avoid_object=self.snake)
        self.msg2statusbar.emit(f"Score: {self.snake.score}")

    def update_game(self):
        """
        Каждые GameTimer времени обновляет состояние игры
        """
        self.draw_objects()
        self.snake.move()
        self.check_collisions()

    def draw_objects(self):
        """
        Рисует объекты на сцену
        """
        self.scene.clear()
        self._draw_object(self.snake, Qt.green)
        self._draw_object(self.apple, Qt.red)
        self._draw_object(self.obstacle, Qt.gray)

    def _draw_object(self, object, color=Qt.black):
        """
        Рисует один объект
        """
        pen = QPen(Qt.black)
        brush = QBrush(color)
        for x, y in object:
            self.scene.addRect(x*object.CellSize, y*object.CellSize,
                               object.CellSize, object.CellSize, pen, brush)

    def check_collisions(self):
        """
        Проверяет столкновение змеи и, при обнаружении, меняет состояние игры
        """
        if self.snake.check_self_collision() or \
           self.snake.check_collision(self.obstacle):
            self.msg2statusbar.emit(f"Game Over.\
                                     Your score: {self.snake.score}")
            self.show_popup()
            self.game_timer.stop()
            self.obstacle_timer.stop()
            self.snake.is_alive = False

        if self.snake.check_collision(self.apple, remove=True):
            self.apple.add_random_item(avoid_object=self.snake)
            self.snake.move(grow=True)
            self.msg2statusbar.emit(f"Score: {self.snake.score}")

    def generate_obstacle(self):
        """
        Добавляет клетку препятствия
        """
        self.obstacle.add_random_item(avoid_object=self.snake)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_P:
            self.pause()
            return
        elif self.paused:
            return

        if event.key() == Qt.Key_Up:
            self.snake.direction = 'up'
        elif event.key() == Qt.Key_Down:
            self.snake.direction = 'down'
        elif event.key() == Qt.Key_Left:
            self.snake.direction = 'left'
        elif event.key() == Qt.Key_Right:
            self.snake.direction = 'right'
        elif event.key() == Qt.Key_R:
            self.restart()

    def restart(self):
        """Рестарт игры"""
        self.initGame(self.snake_size, self.snake_direction)

    def pause(self):
        """
        Ставит игру на паузу, если она запущена
        Запускает игру, если она на паузе
        """
        if self.snake.is_alive:
            self.paused = not self.paused
            if self.paused:
                self.game_timer.stop()
                self.obstacle_timer.stop()
                self.msg2statusbar.emit("PAUSE")
            else:
                self.game_timer.start(self.GameTimer)
                self.obstacle_timer.start(self.ObstacleTimer)

    def resizeEvent(self, event):
        self.setSceneRect(0, 0, self.width(), self.height())
        self.resize_object_rects()
        super().resizeEvent(event)

    def resize_object_rects(self):
        """
        Обновляет размер игрового поля при обновлении размеров окна
        """
        GameObject.BoardHeight = self.height() // GameObject.CellSize
        GameObject.BoardWidth = self.width() // GameObject.CellSize

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2),
                  int((screen.height() - size.height()) / 2))

    def show_popup(self):
        """
        Показывает всплывающее окно при поражении
        """
        msg = QMessageBox()
        msg.setWindowTitle("Game Over")
        msg.setText(f"You have lost. Your score: {self.snake.score}.")
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


if __name__ == '__main__':
    app = QApplication([])
    snake_game = Game(snake_size=4, snake_direction="up")
    snake_game.show()
    sys.exit(app.exec_())
