# pieces.py: định nghĩa hình dạng + màu của 7 khối Tetromino.
import random

# Mỗi khối là 1 ma trận 0/1. Số 1 là ô có gạch, số 0 là ô trống.
# Ví dụ "T": hàng 1 có 1 ô giữa, hàng 2 có 3 ô liền nhau.
SHAPES = {
    "I": [[1, 1, 1, 1]],          # thanh dài 4 ô
    "O": [[1, 1],                 # hình vuông 2x2 (không cần xoay)
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

# Màu riêng cho từng loại khối, dùng khi vẽ lên màn hình.
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
    """1 khối đang rơi: gồm loại (kind), ma trận hình (shape),
    màu (color) và tọa độ góc trên-trái (x, y) trên lưới."""

    def __init__(self, kind=None):
        # Nếu không chỉ định loại thì bốc ngẫu nhiên 1 trong 7 khối.
        self.kind = kind or random.choice(list(SHAPES.keys()))
        # Copy ma trận để khi xoay không làm hỏng SHAPES gốc dùng chung.
        self.shape = [row[:] for row in SHAPES[self.kind]]
        self.color = COLORS[self.kind]
        # Spawn ở giữa board (cột 3), hàng đầu tiên (y = 0).
        self.x = 3
        self.y = 0

    def rotate(self):
        """Xoay ma trận 90 độ theo chiều kim đồng hồ.
        Trả về ma trận mới, chưa kiểm tra va chạm (Board sẽ check)."""
        return [list(row) for row in zip(*self.shape[::-1])]

    def cells(self):
        """Đổi ma trận + tọa độ (x, y) thành list các ô (x, y) trên lưới.
        Board dùng list này để vẽ và để khóa khối vào grid."""
        out = []
        for r, row in enumerate(self.shape):
            for c, v in enumerate(row):
                if v:  # chỉ lấy ô có gạch, bỏ ô trống (số 0)
                    out.append((self.x + c, self.y + r))
        return out


def new_piece():
    # Hàm tiện ích cũ: tạo khối ngẫu nhiên (giữ lại để tương thích).
    return Piece()


class SharedSequence:
    """Chuỗi khối dùng chung cho 2 người chơi để đảm bảo công bằng.

    Cách dùng: cả 2 Board cùng trỏ tới 1 SharedSequence. Mỗi board đếm
    số khối mình đã spawn (spawn_count) rồi hỏi kind_at(spawn_count).
    Vì cùng đọc 1 list nên thứ tự khối giống hệt nhau, dù 2 bên
    chơi nhanh/chậm khác nhau. Bên trong dùng kiểu 7-bag: xáo từng
    túi đủ 7 loại khối rồi mới xáo túi tiếp theo (không bị ra 1 loại
    liên tục như random thuần).
    """

    def __init__(self, seed=None):
        # rng riêng để có thể fix seed khi test (seed giống -> chuỗi giống).
        self.rng = random.Random(seed)
        # seq là list kết quả đã xáo, dài dần theo thời gian.
        self.seq = []

    def kind_at(self, i):
        # Đảm bảo list đủ dài tới vị trí i, thiếu thì xáo thêm túi mới.
        while len(self.seq) <= i:
            bag = list(SHAPES.keys())
            self.rng.shuffle(bag)
            self.seq.extend(bag)
        return self.seq[i]
