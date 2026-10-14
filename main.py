"""main.py: vòng lặp game chính (chế độ 1P).
Phím P1: A/D trái-phải, giữ S rơi nhanh, W xoay, Space rơi ngay.
P pause, R chơi lại khi thua.
"""
import pygame
import settings
from game import Board

# --- Khởi tạo pygame: bắt buộc trước khi dùng display/font ---
pygame.init()
# Tạo cửa sổ với kích thước lấy từ settings (board + panel).
screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
pygame.display.set_caption("Tetris 1P - Day 1")
# clock để giới hạn FPS + tính dt (thời gian mỗi frame).
clock = pygame.time.Clock()
# 2 cỡ chữ: font lớn cho next/score, small_font cho hướng dẫn.
font = pygame.font.SysFont("consolas", 24)
small_font = pygame.font.SysFont("consolas", 18)

# Ngày 1 mặc định easy (speed 1). Ngày 3 sẽ có menu chọn độ khó.
board = Board(difficulty="easy")
paused = False  # cờ tạm dừng, bật/tắt bằng phím P

# Đồng hồ giữ phím A/D để đi liên tục (kiểu DAS của Tetris).
# move_hold: giữ phím được bao lâu; move_repeat: đếm tới INTERVAL để đi tiếp 1 ô.
hold_a = 0.0
repeat_a = 0.0
hold_d = 0.0
repeat_d = 0.0

# --- Vòng lặp game: lặp tới khi đóng cửa sổ ---
running = True
while running:
    # dt: số giây từ frame trước, Board.update(dt) dùng để tính rơi.
    dt = clock.tick(settings.FPS) / 1000.0

    # 1. Xử lý sự kiện (nhấn phím 1 lần). Giữ phím S xử lý ở bước 2.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused  # bật/tắt pause
                # Dừng pause thì reset đồng hồ giữ phím để không bị trôi.
                hold_a = 0.0
                repeat_a = 0.0
                hold_d = 0.0
                repeat_d = 0.0
            elif board.game_over and event.key == pygame.K_r:
                board.reset()  # thua -> R để chơi ván mới
                paused = False
                hold_a = 0.0
                repeat_a = 0.0
                hold_d = 0.0
                repeat_d = 0.0
            elif not paused and not board.game_over:
                # A/D KHÔNG xử lý ở đây nữa mà ở phần giữ phím bên dưới,
                # để giữ phím là khối tự đi liên tục (khỏi bấm nhiều lần).
                if event.key == pygame.K_w:
                    board.try_rotate()
                elif event.key == pygame.K_SPACE:
                    board.hard_drop()

    # 2. Giữ phím: A/D đi liên tục, S rơi nhanh (khác KEYDOWN chỉ bắn 1 lần).
    keys = pygame.key.get_pressed()  # trạng thái giữ phím tại frame này
    if not paused and not board.game_over:
        # Giữ A/D đi liên tục: frame đầu đi ngay 1 ô, giữ quá MOVE_DAS
        # thì cứ mỗi MOVE_INTERVAL đi thêm 1 ô. Giữ cả 2 phím thì đứng yên.
        left = keys[pygame.K_a]
        right = keys[pygame.K_d]
        if left and not right:
            if hold_a == 0.0:
                board.try_move(-1)  # mới nhấn xuống thì đi ngay, không chờ
            hold_a += dt
            hold_d = 0.0
            repeat_d = 0.0
            if hold_a >= settings.MOVE_DAS:
                repeat_a += dt
                while repeat_a >= settings.MOVE_INTERVAL:
                    repeat_a -= settings.MOVE_INTERVAL
                    board.try_move(-1)
        elif right and not left:
            if hold_d == 0.0:
                board.try_move(1)
            hold_d += dt
            hold_a = 0.0
            repeat_a = 0.0
            if hold_d >= settings.MOVE_DAS:
                repeat_d += dt
                while repeat_d >= settings.MOVE_INTERVAL:
                    repeat_d -= settings.MOVE_INTERVAL
                    board.try_move(1)
        else:
            # Thả hết phím hoặc giữ cả 2 phím: reset đồng hồ, đứng yên.
            hold_a = 0.0
            repeat_a = 0.0
            hold_d = 0.0
            repeat_d = 0.0
        # Giữ S thì soft_drop_held=True -> rơi siêu nhanh.
        board.update(dt, soft_drop_held=keys[pygame.K_s])

    # 3. Vẽ: xóa màn hình -> vẽ board/panel -> vẽ chữ phủ -> hiện lên.
    screen.fill(settings.BLACK)
    board.draw(screen, 0, font, small_font)
    # Dòng hướng dẫn phím ở góc panel.
    screen.blit(small_font.render("A/D move  S hold  W rot", True, settings.WHITE), (310, 400))
    screen.blit(small_font.render("Space drop  P pause", True, settings.WHITE), (310, 425))
    # Chữ phủ khi pause hoặc thua.
    if paused and not board.game_over:
        screen.blit(font.render("PAUSE - P", True, settings.WHITE), (80, 280))
    if board.game_over:
        screen.blit(font.render("GAME OVER - R", True, settings.WHITE), (40, 280))

    pygame.display.flip()  # đẩy khung hình mới lên màn hình

pygame.quit()
