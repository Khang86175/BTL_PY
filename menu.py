# menu.py: man hinh chinh chon che do choi + do kho.
# Trang thai di tu "mode" (chon 1P/2P) sang "diff" (chon De/TB/Kho).
# Dung tieng Viet khong dau vi font pygame co ban thieu chu co dau.
import pygame
import settings

# Lua chon che do: chi so 0 = 1 nguoi, 1 = 2 nguoi.
MODE_OPTIONS = ["1 Người chơi", "2 Người chơi"]
# Lua chon do kho: (key truyen cho Board, chu hien thi + toc do bat dau).
DIFF_OPTIONS = [
    ("easy", "Dễ (Speed 1)"),
    ("medium", "Trung bình (Speed 2)"),
    ("hard", "Khó (Speed 3)"),
]


class Menu:
    def __init__(self):
        # stage: "mode" chon che do truoc, "diff" chon do kho sau.
        self.stage = "mode"
        self.mode_index = 0
        self.diff_index = 0
        # players: chon xong o stage "mode" (1 hoac 2), de confirm() biet
        # tra ve lenh bat dau che do nao.
        self.players = 1

    def reset(self):
        # Ve lai tu dau (khi bam ESC tu game ve menu).
        self.stage = "mode"
        self.mode_index = 0
        self.diff_index = 0
        self.players = 1

    def move(self, direction):
        # direction: -1 len, +1 xuong. Vong tron (qua cuoi ve dau).
        if self.stage == "mode":
            self.mode_index = (self.mode_index + direction) % len(MODE_OPTIONS)
        else:
            self.diff_index = (self.diff_index + direction) % len(DIFF_OPTIONS)

    def confirm(self):
        # Tra ve tuple (hanh dong, du lieu) de main.py quyet dinh chuyen trang thai:
        # - ("goto_diff", None): chon che do xong, sang man hinh do kho.
        # - ("start_1p", key) / ("start_2p", key): chon do kho xong,
        #   key la "easy"/"medium"/"hard".
        if self.stage == "mode":
            # Nho lai chon 1 hay 2 nguoi (index 0 = 1P, 1 = 2P).
            self.players = self.mode_index + 1
            self.stage = "diff"
            return ("goto_diff", None)
        key = DIFF_OPTIONS[self.diff_index][0]
        if self.players == 2:
            return ("start_2p", key)
        return ("start_1p", key)

    def back(self):
        # ESC: tu man hinh do kho quay ve man hinh che do. Tra ve True neu lui duoc.
        if self.stage == "diff":
            self.stage = "mode"
            return True
        return False

    def draw(self, screen, font, small_font):
        # Ve tieu de + danh sach lua chon cua stage hien tai, dong ">" la muc dang chon.
        screen.fill(settings.BLACK)
        cx = settings.WIDTH // 2
        title = font.render("TETRIS", True, settings.WHITE)
        screen.blit(title, (cx - title.get_width() // 2, 100))
        if self.stage == "mode":
            sub = small_font.render("Chọn chế độ chơi", True, settings.WHITE)
            screen.blit(sub, (cx - sub.get_width() // 2, 150))
            options = MODE_OPTIONS
            index = self.mode_index
        else:
            sub = small_font.render("Chọn độ khó", True, settings.WHITE)
            screen.blit(sub, (cx - sub.get_width() // 2, 150))
            options = [label for _, label in DIFF_OPTIONS]
            index = self.diff_index
        for i, text in enumerate(options):
            prefix = "> " if i == index else "  "
            img = font.render(prefix + text, True, settings.WHITE)
            screen.blit(img, (cx - img.get_width() // 2, 220 + i * 50))
        hint1 = small_font.render("W/S hoặc Up/Down: chọn", True, settings.WHITE)
        hint2 = small_font.render("Space/Enter: OK | ESC: lùi", True, settings.WHITE)
        screen.blit(hint1, (cx - hint1.get_width() // 2, 500))
        screen.blit(hint2, (cx - hint2.get_width() // 2, 530))
