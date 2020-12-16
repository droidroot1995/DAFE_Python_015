import sys
import random
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QWidget, QPushButton, QColorDialog


from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QInputDialog,  QApplication

from logic import Logic


class Tube(QWidget):
    def __init__(self, cols=60, rows=40):
        super().__init__()

        self.cell = 15
        self.cols = max(5, cols)
        self.rows = max(5, rows)

        self.width = self.cols * self.cell
        self.height = self.rows * self.cell

        self.clrs = ['background-color: purple',
                     'background-color: lightblue']
        self.life = []
        self.tube = []
        self.fill()

    def fill(self):
        self.tube = [[QPushButton() for _ in range(self.cols)] for _ in range(self.rows)]
        for y in range(self.rows):
            for x in range(self.cols):
                self.tube[y][x] = self.field_cell(x, y, alive=(x, y) in self.life)

    def field_cell(self, x, y, alive=False):
        cll = QPushButton(self)
        cll.move(x*self.cell, y*self.cell)
        cll.resize(self.cell, self.cell)
        cll.setStyleSheet(self.clrs[alive])
        cll.clicked.connect(self.click)
        return cll

    def click(self):
        sender = self.sender()
        x, y = map(lambda i: i // self.cell, sender.geometry().getRect()[:2])

        self.life.append((x, y)) if (x, y) not in self.life \
            else self.life.pop(self.life.index((x, y)))
        sender.setStyleSheet(self.clrs[(x, y) in self.life])


class System(Tube):
    def __init__(self, c=60, r=40):
        super().__init__(c, r)

        self.btn_size = (100, 50)
        self.btn_clr = 'background-color: #0077ff'
        self.setWindowTitle('Game of Life')

        self.last_btn = 0
        self.timer = QTimer()
        self.init_ui()

    def init_ui(self):
        step = QPushButton('STEP', self)
        step.move(self.width, self.btn_size[1]*0)
        step.resize(QSize(*self.btn_size))
        step.setStyleSheet(self.btn_clr)
        step.clicked.connect(self.step)

        stop = QPushButton('STOP', self)
        stop.move(self.width, self.btn_size[1]*1)
        stop.resize(QSize(*self.btn_size))
        stop.setStyleSheet(self.btn_clr)
        stop.clicked.connect(self.stop)
        self.last_btn = stop

        auto = QPushButton('AUTO', self)
        auto.move(self.width, self.btn_size[1]*1)
        auto.resize(QSize(*self.btn_size))
        auto.setStyleSheet(self.btn_clr)
        auto.clicked.connect(self.auto)

        self.timer.timeout.connect(self.step)

        clean = QPushButton('CLEAN', self)
        clean.move(self.width, self.btn_size[1] * 2)
        clean.resize(QSize(*self.btn_size))
        clean.setStyleSheet(self.btn_clr)
        clean.clicked.connect(self.clean)

        rand = QPushButton('RAND', self)
        rand.move(self.width, self.btn_size[1] * 3)
        rand.resize(QSize(*self.btn_size))
        rand.setStyleSheet(self.btn_clr)
        rand.clicked.connect(self.rand)

        l_color = QPushButton('COLOR LIVE', self)
        l_color.move(self.width, self.btn_size[1] * 4)
        l_color.resize(QSize(*self.btn_size))
        l_color.setStyleSheet(self.btn_clr)
        l_color.clicked.connect(self.color)

        d_color = QPushButton('COLOR DEAD', self)
        d_color.move(self.width, self.btn_size[1] * 5)
        d_color.resize(QSize(*self.btn_size))
        d_color.setStyleSheet(self.btn_clr)
        d_color.clicked.connect(self.color)

        new_size = QPushButton('SIZE', self)
        new_size.move(self.width, self.btn_size[1] * 6)
        new_size.resize(QSize(*self.btn_size))
        new_size.setStyleSheet(self.btn_clr)
        new_size.clicked.connect(self.new_size)

        ext = QPushButton('EXIT', self)
        ext.move(self.width, self.btn_size[1] * 7)
        ext.resize(QSize(*self.btn_size))
        ext.setStyleSheet(self.btn_clr)
        ext.clicked.connect(self.close)

        self.show()

    def step(self):
        lg = Logic(self.cols, self.rows)
        self.life = lg.get_life(lg.new_step(self.life))
        self.change_clr()

    def change_clr(self):
        for y in range(self.rows):
            for x in range(self.cols):
                # self.field_cell(x, y, alive=(x, y) in self.life)
                self.tube[y][x].setStyleSheet(self.clrs[(x, y) in self.life])

    def stop(self):
        btn = self.sender()
        btn.hide()
        self.last_btn.show()
        self.last_btn = btn
        self.timer.stop()

    def auto(self):
        btn = self.sender()
        btn.hide()
        self.last_btn.show()
        self.last_btn = btn
        self.timer.start(100)

    def clean(self):
        self.life = []
        self.change_clr()

    def rand(self):
        self.life = [random.randrange(2) * (x, y) for y in range(self.rows)
                     for x in range(self.cols)]
        self.life = list(filter(lambda x: x != (), self.life))
        self.change_clr()

    def color(self):
        clr = QColorDialog.getColor()
        i = (self.sender().geometry().getRect()[1] == self.btn_size[1] * 4)
        if clr.isValid():
            self.clrs[i] = 'background-color: ' + clr.name()
        self.change_clr()

    def new_size(self):
        cols, ok1 = QInputDialog.getText(self, 'Columns', 'Input Columns (<90)')
        rows, ok2 = QInputDialog.getText(self, 'Rows', 'Input Rows (<90)')
        cols, rows = map(lambda x: x.strip(), (cols, rows))
        if cols.isdigit() and rows.isdigit() and int(cols) < 90 and int(rows) < 90 and ok1 and ok2:
            self.hide()
            self.__init__(int(cols), int(rows))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # a = Tube()
    b = System()
    sys.exit(app.exec_())
