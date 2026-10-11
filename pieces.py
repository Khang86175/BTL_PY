import random

# Ma trận định nghĩa 7 khối Tetromino
SHAPES = {
    "I": [[1, 1, 1, 1]],
    "O": [[1, 1],
          [1, 1]],
    "T": [[0, 1, 0],
          [1, 1, 1]],
    "S": [[0, 1, 1],
          [1, 1, 0]],
    "Z": [[1, 1, 0],
          [0, 1, 1]],
    "J": [[1, 0, 0],
          [1, 1, 1]],
    "L": [[0, 0, 1],
          [1, 1, 1]],
}

COLORS = {
    "I": (0, 255, 255),      # cyan
    "O": (255, 255, 0),      # vàng
    "T": (160, 32, 240),     # tím
    "S": (0, 255, 0),        # xanh lá
    "Z": (255, 0, 0),        # đỏ
    "J": (0, 0, 255),        # xanh dương
    "L": (255, 165, 0),      # cam
}


class Piece:
    def __init__(self, kind=None):
        self.kind = kind or random.choice(list(SHAPES.keys()))
        # copy ma trận để xoay không ảnh hưởng SHAPES gốc
        self.shape = [row[:] for row in SHAPES[self.kind]]
        self.color = COLORS[self.kind]
        # spawn giữa board
        self.x = 3
        self.y = 0

    def rotate(self):
        """Xoay 90 độ clockwise, trả về shape mới (chưa check va chạm)."""
        return [list(row) for row in zip(*self.shape[::-1])]

    def cells(self):
        """Trả về list (x, y) các ô của khối trên board."""
        out = []
        for r, row in enumerate(self.shape):
            for c, v in enumerate(row):
                if v:
                    out.append((self.x + c, self.y + r))
        return out


def new_piece():
    return Piece()
