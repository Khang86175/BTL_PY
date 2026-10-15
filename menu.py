# menu.py: man hinh chinh chon che do choi + do kho.
# Trang thai di tu "mode" (chon 1P/2P) sang "diff" (chon De/TB/Kho).
# Dung tieng Viet khong dau vi font pygame co ban thieu chu co dau.
import pygame
import settings

# Lua chon che do: chi so 0 = 1 nguoi, 1 = 2 nguoi.
MODE_OPTIONS = ["1 Nguoi choi", "2 Nguoi choi"]
# Lua chon do kho: (key truyen cho Board, chu hien thi + toc do bat dau).
DIFF_OPTIONS = [
    ("easy", "De (Speed 1)"),
    ("medium", "Trung binh (Speed 2)"),
    ("hard", "Kho (Speed 3)"),
]


class Menu:
    def __init__(self):
        # stage: "mode" chon che do truoc, "diff" chon do kho sau.
        self.stage = "mode"
        self.mode_index = 0
        self.diff_index = 0

    def reset(self):
        # Ve lai tu dau (khi bam ESC tu game ve menu).
        self.stage = "mode"
        self.mode_index = 0
        self.diff_index = 0

    def move(self, direction):
        # direction: -1 len, +1 xuong. Vong tron (qua cuoi ve dau).
        if self.stage == "mode":
            self.mode_index = (self.mode_index + direction) % len(MODE_OPTIONS)
        else:
            self.diff_index = (self.diff_index + direction) % len(DIFF_OPTIONS)

    def confirm(self):
        # Tra ve tuple (hanh dong, du lieu) de main.py quyet dinh chuyen trang thai:
        # - ("need_2p", None): chon 2 nguoi (lam o Ngay 5-6).
        # - ("goto_diff", None): chon 1 nguoi, sang man hinh do kho.
        # - ("start_1p", key): chon do kho xong, key la "easy"/"medium"/"hard".
        if self.stage == "mode":
            if self.mode_index == 1:
                return ("need_2p", None)
            self.stage = "diff"
            return ("goto_diff", None)
        return ("start_1p", DIFF_OPTIONS[self.diff_index][0])

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
            sub = small_font.render("Chon che do choi", True, settings.WHITE)
            screen.blit(sub, (cx - sub.get_width() // 2, 150))
            options = MODE_OPTIONS
            index = self.mode_index
        else:
            sub = small_font.render("Chon do kho", True, settings.WHITE)
            screen.blit(sub, (cx - sub.get_width() // 2, 150))
            options = [label for _, label in DIFF_OPTIONS]
            index = self.diff_index
        for i, text in enumerate(options):
            prefix = "> " if i == index else "  "
            img = font.render(prefix + text, True, settings.WHITE)
            screen.blit(img, (cx - img.get_width() // 2, 220 + i * 50))
        hint = small_font.render("W/S hoac Up/Down: chon | Space/Enter: OK | ESC: lui", True, settings.WHITE)
        screen.blit(hint, (cx - hint.get_width() // 2, 500))
