from itertools import chain


class Logic:
    def __init__(self, w=100, h=100):
        self.cols = w
        self.rows = h
        # self.check()

    def get_neighbors(self, crds):
        x, y = crds
        neighbors = [((x + i) % self.cols, (y + j) % self.rows)
                     for i in range(-1, 2)
                     for j in range(-1, 2)
                     if not i == j == 0]
        return neighbors

    def calc_alive_neigbors(self, crds, alive):
        return len(list(filter(lambda x: x in alive,
                               self.get_neighbors(crds))))

    def is_alive_cell(self, crds, alive):
        ngbs = self.calc_alive_neigbors(crds, alive)
        return ngbs == 3 or (ngbs == 2 and crds in alive)

    def new_step(self, alive):
        board = chain(*map(self.get_neighbors, alive))

        new_board = [crds
                     for crds in board
                     if self.is_alive_cell(crds, alive)]
        return list(set(new_board))

    def get_correct_cell(self, crds):
        x, y = crds[0] % self.cols, crds[1] % self.rows
        return x, y

    def get_life(self, alive):
        return list(map(lambda crds: self.get_correct_cell(crds), alive))

    def get_board(self, alive):
        return [[1 if (i, j) in alive else 0
                 for j in range(self.cols)] for i in range(self.rows)]

    def print_board(self, board):
        for line in board:
            print(line)
        print()

    def check(self):
        board = [(1, 1), (2, 2), (3, 2), (1, 3), (2, 3)]
        self.print_board(self.get_board(board))
        for _ in range(30):
            board = self.get_life(self.new_step(board))
            self.print_board(self.get_board(board))


# l = Logic(7, 7)
