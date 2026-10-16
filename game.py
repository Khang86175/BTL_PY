"""game.py: class Board chứa toàn bộ logic của 1 bảng Tetris 10x20.
Mỗi người chơi có 1 Board riêng. Chế độ 2P chỉ là tạo 2 Board."""
import pygame
import settings
from pieces import Piece, SharedSequence

# Đổi speed_level (1/2/3) thành số giây rơi 1 ô (lấy từ settings).
SPEED_MAP = {1: settings.SPEED_1, 2: settings.SPEED_2, 3: settings.SPEED_3}


def load_highscore():
    # Đọc điểm cao từ file. File chưa có hoặc nội dung hỏng thì coi như 0.
    try:
        with open(settings.HIGHSCORE_FILE, "r", encoding="utf-8") as f:
            return max(0, int(f.read().strip() or 0))
    except (OSError, ValueError):
        return 0


def save_highscore(value):
    # Ghi điểm cao ra file. Lỗi ghi (ví dụ thư mục chỉ đọc) thì bỏ qua.
    try:
        with open(settings.HIGHSCORE_FILE, "w", encoding="utf-8") as f:
            f.write(str(int(value)))
    except OSError:
        pass


class Board:
    def __init__(self, difficulty="easy", shared=None):
        # difficulty: "easy" | "medium" | "hard", quyết định tốc độ ban đầu.
        # shared: SharedSequence dùng chung của 2 board (2P). Nếu là None
        # (chơi 1 mình) thì board tự tạo túi riêng.
        self.difficulty = difficulty
        self.shared = shared or SharedSequence()
        # Điểm cao đọc 1 lần khi tạo board, giữ lại qua nhiều ván (reset không xóa).
        self.high = load_highscore()
        self.reset()

    def reset(self):
        # Tạo lưới trống: BLACK nghĩa là ô chưa có gạch.
        self.grid = [[settings.BLACK for _ in range(settings.COLS)]
                     for _ in range(settings.ROWS)]
        self.score = 0       # tổng điểm
        self.lines = 0       # tổng số hàng đã xóa
        # Tốc độ bắt đầu và tốc độ tối đa theo độ khó đã chọn.
        self.speed_level = settings.DIFFICULTY_START[self.difficulty]
        self.max_speed = settings.DIFFICULTY_MAX[self.difficulty]
        self.fall_timer = 0.0  # đồng hồ đếm giờ rơi, cộng dồn dt mỗi frame
        self.lock_timer = 0.0  # đồng hồ đếm giờ khóa khi khối đang chạm đáy
        self.lock_resets = 0  # số lần đã gia hạn lock delay (tối đa LOCK_MAX_RESETS)
        self.game_over = False
        # spawn_count đếm đã ra bao nhiêu khối, dùng để hỏi SharedSequence.
        self.spawn_count = 0
        self.next_kind = self.shared.kind_at(self.spawn_count + 1)
        self._spawn()

    # ---- spawn / valid / lock ----
    def _spawn(self):
        # Lấy loại khối thứ spawn_count trong chuỗi chung rồi tạo Piece.
        kind = self.shared.kind_at(self.spawn_count)
        self.current = Piece(kind)
        # Căn giữa board theo bề rộng khối (I 4 ô -> x=3, O 2 ô -> x=4).
        self.current.x = (settings.COLS - len(self.current.shape[0])) // 2
        self.spawn_count += 1
        # Xem trước khối kế tiếp để vẽ ở khung "next".
        self.next_kind = self.shared.kind_at(self.spawn_count)
        self.fall_timer = 0.0
        self.lock_timer = 0.0
        self.lock_resets = 0
        # Nếu vừa spawn đã đè lên gạch cũ -> hết chỗ -> thua.
        if not self.valid(self.current.shape, self.current.x, self.current.y):
            self.game_over = True
            # Chốt điểm cao khi ván kết thúc rồi mới lưu file.
            if self.score > self.high:
                self.high = self.score
                save_highscore(self.high)

    def valid(self, shape, px, py):
        # Kiểm tra ma trận shape đặt ở (px, py) có hợp lệ không.
        # False khi: lọt ra biên trái/phải/đáy, hoặc đè lên ô đã khóa.
        # Cho phép y < 0 (khối mới nhú ở mép trên).
        for r, row in enumerate(shape):
            for c, v in enumerate(row):
                if not v:
                    continue
                x, y = px + c, py + r
                if x < 0 or x >= settings.COLS or y >= settings.ROWS:
                    return False
                if y >= 0 and self.grid[y][x] != settings.BLACK:
                    return False
        return True

    def lock(self):
        # Khóa khối đang rơi vào lưới: tô màu từng ô của nó lên grid.
        for (x, y) in self.current.cells():
            if y >= 0:
                self.grid[y][x] = self.current.color
        # Khóa xong thì kiểm tra ăn hàng ngay.
        self.clear_lines()

    def clear_lines(self):
        # Tìm các hàng kín full (không còn ô BLACK nào).
        full = [r for r in range(settings.ROWS)
                if all(self.grid[r][c] != settings.BLACK for c in range(settings.COLS))]
        n = len(full)
        if n == 0:
            return
        # Xóa hàng full: xóa dòng đó rồi chèn dòng trống lên đầu.
        for r in full:
            del self.grid[r]
            self.grid.insert(0, [settings.BLACK for _ in range(settings.COLS)])
        # Cộng điểm theo bảng LINE_SCORES, nhân với speed (chơi nhanh thưởng nhiều).
        self.score += settings.LINE_SCORES.get(n, 0) * self.speed_level
        self.lines += n
        # Vượt kỷ lục giữa ván thì cập nhật luôn để panel hiện kịp thời.
        if self.score > self.high:
            self.high = self.score
            save_highscore(self.high)
        self.maybe_speed_up()

    def maybe_speed_up(self):
        # Đủ điểm (SCORE_TO_SPEEDUP) mà chưa tới tốc độ tối đa thì lên 1 cấp.
        if self.score >= settings.SCORE_TO_SPEEDUP and self.speed_level < self.max_speed:
            self.speed_level += 1

    def _grounded(self):
        # True khi khối đang chạm đáy hoặc chạm nóc đống gạch (không xuống được nữa).
        return not self.valid(self.current.shape, self.current.x, self.current.y + 1)

    def _bump_lock_delay(self):
        # Gia hạn giờ khóa sau 1 lần đi/xoay thành công khi đang chạm đáy.
        # Hết lượt gia hạn thì thôi, tránh câu giờ vô hạn.
        if self._grounded() and self.lock_resets < settings.LOCK_MAX_RESETS:
            self.lock_timer = 0.0
            self.lock_resets += 1

    # ---- điều khiển ----
    def try_move(self, dx):
        # Dịch ngang dx (-1 trái, +1 phải) nếu vị trí mới hợp lệ.
        if not self.game_over and self.valid(self.current.shape,
                                             self.current.x + dx, self.current.y):
            self.current.x += dx
            self._bump_lock_delay()
            return True
        return False

    def try_rotate(self):
        # Xoay khối, có wall-kick: xoay xong thử giữ nguyên, dịch ±1, ±2,
        # cái nào hợp lệ thì lấy (±2 để cứu thanh I kẹt sát tường).
        if self.game_over:
            return False
        rotated = self.current.rotate()
        for dx in (0, -1, 1, -2, 2):
            if self.valid(rotated, self.current.x + dx, self.current.y):
                self.current.shape = rotated
                self.current.x += dx
                self._bump_lock_delay()
                return True
        return False

    def hard_drop(self):
        # Rơi ngay lập tức (phím Space / Enter): cho y xuống tới đáy
        # rồi khóa + spawn khối mới luôn.
        if self.game_over:
            return
        while self.valid(self.current.shape, self.current.x, self.current.y + 1):
            self.current.y += 1
        self.lock()
        if not self.game_over:
            self._spawn()

    def update(self, dt, soft_drop_held=False):
        # Gọi mỗi frame. dt là thời gian từ frame trước (giây).
        if self.game_over:
            return
        if self._grounded():
            # Đang chạm đáy: đếm giờ khóa thay vì rơi. Giữ S (soft-drop)
            # thì khóa ngay cho nhanh, khỏi chờ hết LOCK_DELAY.
            # Không tích fall_timer ở đây để nhả phím ra không bị rơi bù.
            self.fall_timer = 0.0
            if soft_drop_held:
                self.lock()
                if not self.game_over:
                    self._spawn()
                return
            self.lock_timer += dt
            if self.lock_timer >= settings.LOCK_DELAY:
                self.lock()
                if not self.game_over:
                    self._spawn()
            return
        # Đang lơ lửng: reset đồng hồ khóa, rơi theo tốc độ.
        # Giữ phím rơi nhanh (S) thì dùng SOFT_DROP_SPEED,
        # thả ra thì dùng tốc độ thường theo speed_level.
        self.lock_timer = 0.0
        self.lock_resets = 0
        self.fall_timer += dt
        interval = settings.SOFT_DROP_SPEED if soft_drop_held else SPEED_MAP[self.speed_level]
        if self.fall_timer >= interval:
            # Trừ interval (giữ phần dư) thay vì gán 0 để tốc độ rơi chuẩn,
            # không bị chậm dần khi FPS trồi sụt.
            self.fall_timer -= interval
            self.current.y += 1

    # ---- vẽ: board ở origin_x, panel Next/Score bên phải ----
    def draw(self, screen, origin_x, font, small_font):
        # origin_x để vẽ board thứ 2 dịch sang phải trong chế độ 2P.
        # Vẽ nền panel trước để chữ và khung "next" nổi lên trên.
        panel_x = origin_x + settings.COLS * settings.CELL
        pygame.draw.rect(screen, settings.PANEL_BG,
                         (panel_x, 0, settings.SIDEBAR, settings.HEIGHT))
        # Vẽ các ô đã khóa: mỗi ô là 1 hình vuông CELLxCELL + viền xám.
        for r in range(settings.ROWS):
            for c in range(settings.COLS):
                rect = pygame.Rect(origin_x + c * settings.CELL, r * settings.CELL,
                                   settings.CELL, settings.CELL)
                pygame.draw.rect(screen, self.grid[r][c], rect)
                pygame.draw.rect(screen, settings.GRID_LINE, rect, 1)
        # Vẽ khối đang rơi đè lên trên lưới.
        for (x, y) in self.current.cells():
            if y >= 0:
                rect = pygame.Rect(origin_x + x * settings.CELL, y * settings.CELL,
                                   settings.CELL, settings.CELL)
                pygame.draw.rect(screen, self.current.color, rect)
                pygame.draw.rect(screen, settings.WHITE, rect, 1)
        # Khung NEXT ở panel phải (giống ảnh mẫu): chữ "next" + ô vuông + hình xem trước.
        nx, ny, nw, nh = panel_x + 30, 30, 140, 140
        screen.blit(font.render("next", True, settings.WHITE), (nx + 45, 2))
        pygame.draw.rect(screen, settings.WHITE, (nx, ny, nw, nh), 2)
        self._draw_next_preview(screen, nx, ny, nw, nh)
        # Điểm SCORE, số hàng LINES, kỷ lục HI và tốc độ hiện tại dưới khung next.
        screen.blit(font.render("SCORE", True, settings.WHITE), (nx + 25, ny + nh + 30))
        screen.blit(font.render(str(self.score), True, settings.WHITE), (nx + 25, ny + nh + 60))
        screen.blit(small_font.render(f"LINES {self.lines}", True, settings.WHITE),
                    (nx + 25, ny + nh + 100))
        screen.blit(small_font.render(f"HI {self.high}", True, settings.WHITE),
                    (nx + 25, ny + nh + 125))
        screen.blit(small_font.render(f"Speed {self.speed_level}", True, settings.WHITE),
                    (nx + 25, ny + nh + 150))

    def _draw_next_preview(self, screen, nx, ny, nw, nh):
        # Vẽ khối kế tiếp vào giữa khung next, tự co cỡ ô (s) cho vừa khung.
        from pieces import SHAPES, COLORS
        shape = SHAPES[self.next_kind]
        color = COLORS[self.next_kind]
        rows, cols = len(shape), len(shape[0])
        s = min((nw - 20) // max(cols, 1), (nh - 20) // max(rows, 1))
        s = max(s, 8)
        w, h = cols * s, rows * s
        ox, oy = nx + (nw - w) // 2, ny + (nh - h) // 2
        for r in range(rows):
            for c in range(cols):
                if shape[r][c]:
                    rect = pygame.Rect(ox + c * s, oy + r * s, s, s)
                    pygame.draw.rect(screen, color, rect)
                    pygame.draw.rect(screen, settings.WHITE, rect, 1)
