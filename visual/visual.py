# noinspection PyUnresolvedReferences
import pathmagic
from sys import argv, exit
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from logic.puzzle_maker import make_puzzle
from logic.error_checker import check_puzzle
from logic.solver import solve_puzzle
from utilities.iterable import Iterable


class Window(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.paint_widget = None
        self._puzzle_file = None
        self._puzzle = None
        self._solutions = None
        self._next_solution_button = None

        self.initialize_window()
        self.initialize_menu()
        self.show()

    def initialize_window(self):
        self.setWindowTitle('Cross sums')
        self.setFixedSize(300, 200)

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(palette)

        self.paint_widget = PaintWidget(self, self._puzzle)
        self.paint_widget.move(0, 21)
        self.paint_widget.resize(self.width(), self.height())

    # noinspection PyUnresolvedReferences
    def initialize_menu(self):
        menu = self.menuBar()
        menu.setNativeMenuBar(False)
        file_menu = menu.addMenu('File')

        loader = QAction('Load puzzle', self)
        loader.triggered.connect(self.load_puzzle_dialog)
        loader.setShortcut('Ctrl+O')

        exit_button = QAction('Exit', self)
        exit_button.triggered.connect(self.close)

        next_solution_button = QAction('Next solution', self)
        next_solution_button.setShortcut('Ctrl+N')
        next_solution_button.triggered.connect(self.yield_next_solution)
        next_solution_button.setEnabled(False)
        self._next_solution_button = next_solution_button

        file_menu.addAction(loader)
        file_menu.addAction(next_solution_button)
        file_menu.addAction(exit_button)

    def load_puzzle_dialog(self):
        dialog = QFileDialog(self)
        options = dialog.Options()
        options |= dialog.DontUseNativeDialog
        file_name = (dialog.getOpenFileName
                     (caption="Load puzzle", directory="../",
                      filter="All Files (*);;Text files(*.txt)",
                      options=options)[0])
        if not file_name:
            return
        try:
            self._puzzle_file = file_name
            self.initialize_puzzle()
            self.draw_puzzle()
            self._solutions = None
            self._next_solution_button.setEnabled(True)
        except Exception as exception:
            self.yell_message(str(exception))

    def initialize_puzzle(self):
        with open(self._puzzle_file, encoding='utf-8') as file:
            self._puzzle = make_puzzle(file)
            check_puzzle(self._puzzle)

    def yield_next_solution(self):
        def generator():
            puzzle = self._puzzle.copy()
            solutions = []
            counter = 0
            first_cycle = True
            while True:
                for solution in solve_puzzle(puzzle):
                    if counter < 250 and first_cycle:
                        solutions.append(solution)
                    yield solution
                    counter += 1
                if counter < 250:
                    while True:
                        yield from solutions
                first_cycle = False

        if self._solutions is None:
            self._solutions = generator()

        try:
            self._puzzle = next(self._solutions)
        except RuntimeError as exception:
            self.yell_message(str(exception))
        self.draw_puzzle()

    def yell_message(self, message: str):
        error_message = QMessageBox(self)
        error_message.setIcon(QMessageBox.Critical)
        error_message.setText(message)
        error_message.setWindowTitle('Failure')
        error_message.show()

    def draw_puzzle(self):
        self.paint_widget.puzzle = self._puzzle
        self.paint_widget.update()
        width, height = (Iterable(Iterable(self._puzzle)
                                  .max(lambda pair: pair[dimension])
                                  for dimension in range(2))
                         .to_tuple(lambda number: number + 1))
        self.setFixedSize(QSize(height * 50 + 1, width * 50 + 22))
        self.paint_widget.resize(self.width(), self.height())


def draw(pen_color, brush_color):
    def decorator(func):
        def wrapped(self, *args):
            painter = self.painter
            painter.setPen(pen_color)
            painter.setBrush(brush_color)
            figure = func(self, *args)
            painter.drawPolygon(*figure)
        return wrapped
    return decorator


class PaintWidget(QWidget):
    def __init__(self, parent, puzzle: dict = None, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
        self.puzzle = puzzle
        self.painter = None

    @draw(Qt.transparent, Qt.black)
    def fill_hint(self, point: QPoint, horizontal: bool):
        return (Iterable(((0, 0), (1, 1), (horizontal, not horizontal)))
                .map(lambda pair: QPoint(*pair))
                .map(lambda addition: point + addition)
                .map(lambda result: result * 50))

    @draw(Qt.black, Qt.transparent)
    def lead_round_square(self, point: QPoint):
        return (Iterable(((0, 0), (0, 1), (1, 1), (1, 0)))
                .map(lambda pair: QPoint(*pair))
                .map(lambda addition: point + addition)
                .map(lambda result: result * 50))

    @draw(Qt.black, Qt.transparent)
    def draw_diagonal(self, point: QPoint):
        return (Iterable(((0, 0), (1, 1)))
                .map(lambda pair: QPoint(*pair))
                .map(lambda addition: point + addition)
                .map(lambda result: result * 50))

    def draw_text(self, rectangle: QRect, alignment, text: str):
        painter = self.painter
        painter.setPen(Qt.black)
        painter.setBrush(Qt.transparent)

        painter.drawText(rectangle, alignment, text)

    def draw_token(self, key):
        token = self.puzzle.get(key)
        transposed = tuple(reversed(key))

        if token is None:
            (Iterable(range(2))
             .to_tuple(lambda bearings: self.fill_hint(QPoint(*transposed),
                                                       bearings)))
        elif isinstance(token, int):
            self.draw_text(QRect(QPoint(*transposed) * 50,
                                 QSize(50, 50)),
                           Qt.AlignCenter | Qt.AlignVCenter, str(token))
        elif isinstance(token, tuple):
            for orientation in range(2):
                component = token[orientation]
                self.draw_diagonal(QPoint(*transposed))
                if component is None:
                    self.fill_hint(QPoint(*transposed), bool(orientation))
                else:
                    (self.draw_text
                     (QRect(QPoint(*transposed) * 50, QSize(50, 50)),
                      Qt.AlignLeft | Qt.AlignBottom if not orientation
                      else Qt.AlignRight | Qt.AlignTop, str(component)))
        elif isinstance(token, set):
            pass

    def paintEvent(self, *args):
        if self.puzzle is None:
            return

        self.painter = QPainter()
        self.painter.begin(self)
        painter = self.painter

        painter.setFont(QFont('Consolas', 12))

        for key in self.puzzle:
            self.lead_round_square(QPoint(*reversed(key)))
            self.draw_token(key)

        painter.end()


if __name__ == '__main__':
    app = QApplication(argv)
    window = Window()
    exit(app.exec_())
