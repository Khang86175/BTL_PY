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

    Cả 2 Board cùng trỏ tới 1 SharedSequence. Board thứ i spawn khối thứ k
    của mình bằng cách đọc khối ở vị trí (base + k) trong chuỗi. Vì cùng
    đọc 1 seq nên thứ tự khối giống hệt nhau dù 2 bên chơi nhanh/chậm
    khác nhau. Bên trong dùng kiểu 7-bag: xáo từng túi đủ 7 loại khối rồi
    mới xáo túi tiếp theo (không bị ra 1 loại liên tục như random thuần).
    """

    def __init__(self, seed=None):
        # Seed gốc: dùng để sinh seed riêng cho từng túi (bag).
        # Seed None (chơi thật) thì lấy ngẫu nhiên, để mỗi ván khác nhau.
        self.seed = random.randrange(1 << 30) if seed is None else seed
        # seq: các túi đã xáo, dài dần theo thời gian.
        self.seq = []
        # cursor: đánh dấu mốc "đã cấp phát tới đâu" của chuỗi, CHỈ TIẾN.
        # Board bắt đầu ván mới sẽ lấy mốc base = cursor hiện tại, nên
        # khối của ván trước không bị dùng lại.
        self.cursor = 0

    def _ensure(self, i):
        # Đảm bảo seq đã có ít nhất i+1 phần tử (xáo thêm túi nếu thiếu).
        while len(self.seq) <= i:
            self._fill_bag(len(self.seq) // 7)

    def _fill_bag(self, bag_index):
        # Sinh 1 túi 7 khối mới. Dùng rng tạo từ (seed gốc, số túi) nên
        # túi thứ k luôn giống nhau dù bên nào gọi trước.
        rng = random.Random(f"{self.seed}:{bag_index}")
        bag = list(SHAPES.keys())
        rng.shuffle(bag)
        self.seq.extend(bag)

    def kind_at(self, i):
        # Xem khối ở vị trí i mà KHÔNG tiêu thụ nó (dùng để xem trước).
        self._ensure(i)
        return self.seq[i]

    def consume_to(self, i):
        # Tiêu thụ khối ở vị trí i: đảm bảo đã xáo tới đó rồi đẩy con trỏ
        # chung lên i+1 (nếu con trỏ đang thấp hơn). Trả về khối đó.
        self._ensure(i)
        if self.cursor <= i:
            self.cursor = i + 1
        return self.seq[i]
