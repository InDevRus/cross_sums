import sys
from functools import wraps

from PyQt5 import QtWidgets, QtCore, QtGui

from logic.error_checker import check_puzzle
from logic.puzzle_maker import make_puzzle
from logic.solver import solve_puzzle
from utilities.iterable import Iterable

draw_scale = 35


class SolveThread(QtCore.QThread):
    completion_signal = QtCore.pyqtSignal(dict, int, int)
    failure_signal = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)
        self._generator = parent.solution_generator
        self.completion_signal.connect(parent.save_solution)
        self.failure_signal.connect(parent.process_failure)

    def run(self):
        try:
            self.completion_signal.emit(*next(self._generator))
        except RuntimeError as exception:
            self.failure_signal.emit(str(exception))


class CrossSumsWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.paint_widget = None
        self._puzzle_file = None
        self._puzzle = None
        self._next_solution_button = None
        self._load_puzzle_button = None
        self._status_label = None
        self._solution_number = self._total_solutions = 0
        self._solution_holding_limit = 50
        self.solution_generator = None
        self._solve_thread = None

        self.initialize_window()
        self.initialize_menu()
        self.initialize_status_bar()

        self.show()

    def initialize_window(self):
        self.setWindowTitle('Cross sums')
        self.setFixedSize(300, 200)

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QtCore.Qt.white)
        self.setPalette(palette)

        self.paint_widget = PaintWidget(self, self._puzzle)
        self.paint_widget.move(0, 21)
        self.paint_widget.resize(self.width(), self.height())

    def initialize_status_bar(self):
        status_bar = QtWidgets.QStatusBar(self)
        self.setStatusBar(status_bar)

        self._status_label = QtWidgets.QLabel()
        status_bar.addPermanentWidget(self._status_label)

    # noinspection PyUnresolvedReferences
    def initialize_menu(self):
        menu = self.menuBar()
        menu.setNativeMenuBar(False)

        file_menu = menu.addMenu('File')

        loader = QtWidgets.QAction('Load puzzle', self)
        loader.triggered.connect(self.load_puzzle_dialog)
        loader.setShortcut('Ctrl+O')
        self._load_puzzle_button = loader

        exit_button = QtWidgets.QAction('Exit', self)
        exit_button.triggered.connect(self.close)

        next_solution_button = QtWidgets.QAction('Next solution', self)
        next_solution_button.setShortcut('Ctrl+N')
        next_solution_button.triggered.connect(self.yield_next_solution)
        next_solution_button.setEnabled(False)
        self._next_solution_button = next_solution_button

        file_menu.addAction(loader)
        file_menu.addAction(next_solution_button)
        file_menu.addAction(exit_button)

    def load_puzzle_dialog(self):
        dialog = QtWidgets.QFileDialog(self)
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
            self._total_solutions = self._solution_number = 0
            self.draw_puzzle()
            self.initialize_generator()
            self._next_solution_button.setEnabled(True)
        except Exception as exception:
            self.yell_message(str(exception))

    def initialize_puzzle(self):
        with open(self._puzzle_file, encoding='utf-8') as file:
            self._puzzle = make_puzzle(file)
        check_puzzle(self._puzzle)

    def initialize_generator(self):
        def generator():
            def recount_numbers():
                nonlocal solution_number, total_solutions
                solution_number = solution_number
                total_solutions = max(total_solutions, solution_number)

            total_solutions = 0
            puzzle = self._puzzle.copy()
            solutions = []
            solution_number = 0
            first_cycle = True
            while True:
                for (solution_number,
                     solution) in enumerate(solve_puzzle(puzzle),
                                            start=1):
                    if (solution_number < self._solution_holding_limit
                       and first_cycle):
                        solutions.append(solution)
                    recount_numbers()
                    yield solution, solution_number, total_solutions
                if solution_number < self._solution_holding_limit:
                    while True:
                        for solution_number, solution in enumerate(solutions,
                                                                   start=1):
                            recount_numbers()
                            yield solution, solution_number, total_solutions
                first_cycle = False
        self.solution_generator = generator()

    def yield_next_solution(self):
        self.lock_actions()
        self._solve_thread = SolveThread(self)
        self._solve_thread.start()

    def lock_actions(self):
        self._load_puzzle_button.setEnabled(False)
        self._next_solution_button.setEnabled(False)

    def unlock_actions(self):
        self._load_puzzle_button.setEnabled(True)
        self._next_solution_button.setEnabled(True)

    def save_solution(self, solution: dict,
                      solution_number: int, total_solutions: int):
        self._puzzle = solution
        self._solution_number = solution_number
        self._total_solutions = total_solutions
        self.draw_puzzle()
        self.unlock_actions()

    def process_failure(self, message: str):
        self.yell_message(message)
        self.unlock_actions()

    def yell_message(self, message: str):
        error_message = QtWidgets.QMessageBox(self)
        error_message.setIcon(QtWidgets.QMessageBox.Critical)
        error_message.setText(message)
        error_message.setWindowTitle('Failure')
        error_message.show()

    def draw_puzzle(self):
        self.paint_widget.puzzle = self._puzzle
        self.paint_widget.update()
        width, height = (Iterable(Iterable(self._puzzle)
                                  .map(lambda pair: pair[dimension])
                                  .max()
                                  for dimension in range(2))
                         .to_tuple(lambda number: number + 1))
        self.setFixedSize(QtCore.QSize(height * draw_scale + 1,
                                       width * draw_scale + 2 + 20 + 20))
        self.paint_widget.resize(self.width(), self.height())

        message = 'Solution # {0}, total: {1}.'
        self.draw_status_bar(message.format(self._solution_number,
                                            self._total_solutions))

    def draw_status_bar(self, message):
        self._status_label.setText(message)


def draw(pen_color, brush_color):
    def decorator(func):
        @wraps(func)
        def wrapped(self, *args):
            painter = self.painter
            painter.setPen(pen_color)
            painter.setBrush(brush_color)
            figure = func(self, *args)
            painter.drawPolygon(*figure)
        return wrapped
    return decorator


class PaintWidget(QtWidgets.QWidget):
    def __init__(self, parent, puzzle: dict = None, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
        self.puzzle = puzzle
        self.painter = None

    @draw(QtCore.Qt.transparent, QtCore.Qt.black)
    def fill_hint(self, point: QtCore.QPoint, horizontal: bool):
        return (Iterable(((0, 0), (1, 1), (horizontal, not horizontal)))
                .map(lambda pair: QtCore.QPoint(*pair))
                .map(lambda addition: point + addition)
                .map(lambda result: result * draw_scale))

    @draw(QtCore.Qt.black, QtCore.Qt.transparent)
    def lead_round_square(self, point: QtCore.QPoint):
        return (Iterable(((0, 0), (0, 1), (1, 1), (1, 0)))
                .map(lambda pair: QtCore.QPoint(*pair))
                .map(lambda addition: point + addition)
                .map(lambda result: result * draw_scale))

    @draw(QtCore.Qt.black, QtCore.Qt.transparent)
    def draw_diagonal(self, point: QtCore.QPoint):
        return (Iterable(((0, 0), (1, 1)))
                .map(lambda pair: QtCore.QPoint(*pair))
                .map(lambda addition: point + addition)
                .map(lambda result: result * draw_scale))

    def draw_text(self, rectangle: QtCore.QRect, alignment, text: str):
        painter = self.painter
        painter.setPen(QtCore.Qt.black)
        painter.setBrush(QtCore.Qt.transparent)

        painter.drawText(rectangle, alignment, text)

    def draw_token(self, key):
        token = self.puzzle.get(key)
        transposed = tuple(reversed(key))

        if token is None:
            (Iterable(range(2))
             .to_tuple(lambda bearings:
                       self.fill_hint(QtCore.QPoint(*transposed),
                                      bearings)))
        elif isinstance(token, int):
            self.draw_text(
                QtCore.QRect(QtCore.QPoint(*transposed) * draw_scale,
                             QtCore.QSize(draw_scale, draw_scale)),
                QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter, str(token))
        elif isinstance(token, tuple):
            for orientation in range(2):
                component = token[orientation]
                self.draw_diagonal(QtCore.QPoint(*transposed))
                if component is None:
                    self.fill_hint(QtCore.QPoint(*transposed),
                                   bool(orientation))
                else:
                    (self.draw_text
                     (QtCore.QRect(QtCore.QPoint(*transposed) * draw_scale,
                                   QtCore.QSize(draw_scale, draw_scale)),
                      QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom
                      if not orientation
                      else QtCore.Qt.AlignRight | QtCore.Qt.AlignTop,
                      str(component)))
        elif isinstance(token, set):
            pass

    def paintEvent(self, *args):
        if self.puzzle is None:
            return

        self.painter = QtGui.QPainter()
        self.painter.begin(self)
        painter = self.painter

        painter.setFont(QtGui.QFont('Consolas', 12))

        for key in self.puzzle:
            self.lead_round_square(QtCore.QPoint(*reversed(key)))
            self.draw_token(key)

        painter.end()


def main():
    app = QtWidgets.QApplication(sys.argv)
    _ = CrossSumsWindow()
    sys.exit(app.exec_())
