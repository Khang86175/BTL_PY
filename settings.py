# settings.py: mọi con số cấu hình game nằm ở đây.
# Muốn đổi kích thước, tốc độ, điểm thì chỉ sửa file này.

# Kích thước lưới chơi chuẩn Tetris: rộng 10 ô, cao 20 ô.
COLS = 10
ROWS = 20
# CELL là độ lớn 1 ô tính bằng pixel (30px -> board 300x600).
CELL = 30

# SIDEBAR là panel bên phải chứa khung "next" và điểm (rộng 200px).
SIDEBAR = 200
# Mỗi người chơi chiếm 1 "cột" = board + panel. Chế độ 2P dùng 2 cột.
PLAYER_WIDTH = COLS * CELL + SIDEBAR
# Kích thước cửa sổ 1P = 1 cột. main.py dùng 2 số này để tạo màn hình 1P.
WIDTH = PLAYER_WIDTH
HEIGHT = ROWS * CELL
# Cửa sổ 2P rộng gấp đôi (2 board cạnh nhau).
WIDTH_2P = PLAYER_WIDTH * 2
# FPS: số khung hình mỗi giây, clock.tick(FPS) giữ game chạy mượt.
FPS = 60

# 3 tốc độ rơi (giây / 1 ô): số càng nhỏ rơi càng nhanh.
# Speed 1 chậm nhất cho chế độ Dễ, Speed 3 nhanh nhất cho chế độ Khó.
SPEED_1 = 0.5
SPEED_2 = 0.3
SPEED_3 = 0.15
# Khi giữ phím S (soft-drop) thì rơi siêu nhanh, bất kể đang speed mấy.
SOFT_DROP_SPEED = 0.05

# Giữ A/D để đi liên tục: nhấn xuống đi ngay 1 ô, giữ quá MOVE_DAS
# (0.18s) thì tự lặp mỗi MOVE_INTERVAL (0.06s). Thả ra là dừng.
MOVE_DAS = 0.18
MOVE_INTERVAL = 0.06

# Lock delay: khối chạm đáy thì đợi LOCK_DELAY giây mới khóa (thay vì dính ngay),
# để người chơi kịp trượt/xoay cứu vào phút chót. Mỗi lần đi/xoay thành công
# khi đang chạm đáy được gia hạn giờ, tối đa LOCK_MAX_RESETS lần.
LOCK_DELAY = 0.5
LOCK_MAX_RESETS = 15

# Ngưỡng điểm để lên tốc: Dễ 1->2, Trung bình 2->3 (xem DIFFICULTY_MAX).
SCORE_TO_SPEEDUP = 1500

# Độ khó: tốc độ bắt đầu và tốc độ tối đa cho phép.
# Dễ bắt đầu speed 1 và chỉ lên tối đa speed 2.
DIFFICULTY_START = {"easy": 1, "medium": 2, "hard": 3}
DIFFICULTY_MAX = {"easy": 2, "medium": 3, "hard": 3}

# Điểm ăn theo số hàng xóa cùng lúc, rồi nhân với speed_level hiện tại.
# Ví dụ xóa 4 hàng (Tetris) ở speed 2 được 800*2 = 1600 điểm.
LINE_SCORES = {1: 100, 2: 200, 3: 350, 4: 500}

# File lưu điểm cao nhất, để thoát game mở lại vẫn còn.
HIGHSCORE_FILE = "highscore.txt"

# Bảng màu (R, G, B). BLACK nghĩa là ô trống, GRID_LINE là viền lưới.
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (40, 40, 40)
GRID_LINE = (60, 60, 60)
PANEL_BG = (20, 20, 20)
