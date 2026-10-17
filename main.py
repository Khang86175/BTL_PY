"""main.py: vong lap game chinh.
Trang thai: MENU chon che do -> MENU chon do kho -> PLAYING (1P hoac 2P).
Menu: W/S hoac Up/Down di chuyen, Space/Enter chon, ESC quay lui.
Game 1P: A/D (giu de di lien tuc), giu S roi nhanh, W xoay,
Space roi ngay. P pause, R choi lai khi thua, ESC ve menu.
Game 2P (khung Ngay 5): 2 board doc chung 1 chuoi khoi nen roi y het nhau;
dieu khien rieng tung nguoi se lam o Ngay 6.
"""
import pygame
import settings
from game import Board
from menu import Menu
from pieces import SharedSequence

# --- Khoi tao pygame: bat buoc truoc khi dung display/font ---
pygame.init()
# Cua so 1P (500x600). Che do 2P se doi kich thuoc cua so luc bat dau.
screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
pygame.display.set_caption("Tetris 1P")
clock = pygame.time.Clock()  # gioi han FPS + tinh dt (thoi gian moi frame)
# 2 co chu: font lon cho tieu de/diem, small_font cho huong dan.
font = pygame.font.SysFont("consolas", 24)
small_font = pygame.font.SysFont("consolas", 18)

menu = Menu()
# Board mac dinh, se tao lai dung do kho khi chon menu xong.
board = Board(difficulty="easy")
# state: "menu" (chon che do/do kho), "playing" (dang choi 1P),
# "playing_2p" (che do 2 nguoi).
state = "menu"
paused = False  # co tam dung, bat/tat bang phim P
# boards_2p + shared de che do 2P dung: 2 board doc chung 1 chuoi khoi
# nen thu tu khoi 2 ben giong het nhau (cong bang).
boards_2p = []
shared = None

# Dong ho giu phim A/D de di lien tuc (kieu DAS cua Tetris).
# hold_*: giu phim duoc bao lau; repeat_*: dem toi INTERVAL de di tiep 1 o.
hold_a = 0.0
repeat_a = 0.0
hold_d = 0.0
repeat_d = 0.0


def reset_hold_timers():
    # Reset dong ho giu phim khi doi trang thai de khong bi troi phim.
    global hold_a, repeat_a, hold_d, repeat_d
    hold_a = 0.0
    repeat_a = 0.0
    hold_d = 0.0
    repeat_d = 0.0


def start_1p(difficulty):
    # Bat dau van 1P moi voi do kho da chon o menu.
    global board, state, paused
    pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
    pygame.display.set_caption("Tetris 1P")
    board = Board(difficulty=difficulty)
    paused = False
    reset_hold_timers()
    state = "playing"


def start_2p(difficulty):
    # Bat dau van 2P: cua so rong gap doi, 2 board doc chung 1 SharedSequence
    # nen 2 ben nhan dung cung thu tu khoi (chinh la yeu cau cong bang).
    global boards_2p, shared, state, paused
    pygame.display.set_mode((settings.WIDTH_2P, settings.HEIGHT))
    pygame.display.set_caption("Tetris 2P")
    shared = SharedSequence()
    boards_2p = [Board(difficulty=difficulty, shared=shared),
                 Board(difficulty=difficulty, shared=shared)]
    paused = False
    reset_hold_timers()
    state = "playing_2p"


def draw_board(board, origin_x, label, show_help=False):
    # Ve 1 board tai vi tri origin_x + nhan ten nguoi choi goc phai panel.
    board.draw(screen, origin_x, font, small_font)
    panel_x = origin_x + settings.COLS * settings.CELL
    img = small_font.render(label, True, settings.WHITE)
    screen.blit(img, (panel_x + settings.SIDEBAR - 10 - img.get_width(), 2))
    if show_help:
        # Dong huong dan phim o goc panel (chi hien khi 1P).
        screen.blit(small_font.render("A/D move  S hold  W rot", True, settings.WHITE),
                    (origin_x + 310, 400))
        screen.blit(small_font.render("Space drop  P pause", True, settings.WHITE),
                    (origin_x + 310, 425))
        screen.blit(small_font.render("ESC menu", True, settings.WHITE),
                    (origin_x + 310, 450))


# --- Vong lap game: lap toi khi dong cua so ---
running = True
while running:
    # dt: so giay tu frame truoc, Board.update(dt) dung de tinh roi.
    dt = clock.tick(settings.FPS) / 1000.0

    # 1. Xu ly su kien theo tung trang thai.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if state == "menu":
                # Dieu huong menu: W/S hoac mui ten len/xuong.
                if event.key in (pygame.K_w, pygame.K_UP):
                    menu.move(-1)
                elif event.key in (pygame.K_s, pygame.K_DOWN):
                    menu.move(1)
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    action, data = menu.confirm()
                    if action == "start_1p":
                        start_1p(data)
                    elif action == "start_2p":
                        start_2p(data)
                    # "goto_diff" thi menu tu chuyen stage, khong can lam gi.
                elif event.key == pygame.K_ESCAPE:
                    menu.back()  # tu man hinh do kho lui ve man hinh che do
            elif state == "playing":
                if event.key == pygame.K_ESCAPE:
                    # Ve menu de doi che do/do kho, dong ho giu phim reset theo.
                    pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
                    menu.reset()
                    paused = False
                    reset_hold_timers()
                    state = "menu"
                elif event.key == pygame.K_p:
                    paused = not paused  # bat/tat pause
                    reset_hold_timers()
                elif board.game_over and event.key == pygame.K_r:
                    board.reset()  # thua -> R de choi van moi
                    paused = False
                    reset_hold_timers()
                elif not paused and not board.game_over:
                    # A/D KHONG xu ly o day ma o phan giu phim ben duoi,
                    # de giu phim la khoi tu di lien tuc (khoi bam nhieu lan).
                    if event.key == pygame.K_w:
                        board.try_rotate()
                    elif event.key == pygame.K_SPACE:
                        board.hard_drop()
            elif state == "playing_2p":
                # Ngay 5: chi la khung, 2 board roi y het nhau de kiem tra
                # chuoi khoi chung. Phim rieng cho tung nguoi lam o Ngay 6.
                if event.key == pygame.K_ESCAPE:
                    pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
                    menu.reset()
                    paused = False
                    reset_hold_timers()
                    state = "menu"
                elif event.key == pygame.K_p:
                    paused = not paused

    # 2. Giua cac frame: A/D di lien tuc, S roi nhanh (khac KEYDOWN chi ban 1 lan).
    if state == "playing":
        keys = pygame.key.get_pressed()  # trang thai giu phim tai frame nay
        if not paused and not board.game_over:
            # Giu A/D di lien tuc: frame dau di ngay 1 o, giu qua MOVE_DAS
            # thi cu moi MOVE_INTERVAL di them 1 o. Giu ca 2 phim thi dung yen.
            left = keys[pygame.K_a]
            right = keys[pygame.K_d]
            if left and not right:
                if hold_a == 0.0:
                    board.try_move(-1)  # moi nhan xuong thi di ngay, khong cho
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
                # Tha het phim hoac giu ca 2 phim: reset dong ho, dung yen.
                reset_hold_timers()
            # Giu S thi soft_drop_held=True -> roi sieu nhanh.
            board.update(dt, soft_drop_held=keys[pygame.K_s])
    elif state == "playing_2p":
        # Ca 2 board cung chay update voi cung dt -> toc do roi giong nhau,
        # va vi doc chung chuoi khoi nen khoi dang roi cung giong nhau.
        if not paused:
            for b in boards_2p:
                b.update(dt)

    # 3. Ve theo trang thai hien tai.
    if state == "menu":
        menu.draw(screen, font, small_font)
    elif state == "playing":
        screen.fill(settings.BLACK)
        draw_board(board, 0, "P1", show_help=True)
        if paused and not board.game_over:
            screen.blit(font.render("PAUSE - P", True, settings.WHITE), (80, 280))
        if board.game_over:
            # Man hinh thua: lam mo board roi hien diem van nay + ky luc.
            shade = pygame.Surface((settings.COLS * settings.CELL, settings.HEIGHT))
            shade.set_alpha(180)
            shade.fill(settings.BLACK)
            screen.blit(shade, (0, 0))
            screen.blit(font.render("GAME OVER", True, settings.WHITE), (55, 220))
            screen.blit(small_font.render(f"Score: {board.score}", True, settings.WHITE), (90, 260))
            screen.blit(small_font.render(f"Best: {board.high}", True, settings.WHITE), (90, 285))
            screen.blit(small_font.render("Nhan R choi lai", True, settings.WHITE), (60, 310))
    else:
        # Che do 2P: ve 2 board canh nhau, vach phan cach giua 2 nguoi choi.
        screen.fill(settings.BLACK)
        split = settings.PLAYER_WIDTH
        pygame.draw.line(screen, settings.GRID_LINE, (split, 0), (split, settings.HEIGHT), 2)
        draw_board(boards_2p[0], 0, "P1")
        draw_board(boards_2p[1], split, "P2")
        if paused:
            screen.blit(font.render("PAUSE - P", True, settings.WHITE), (settings.WIDTH_2P // 2 - 70, 280))

    pygame.display.flip()  # day khung hinh moi len man hinh

pygame.quit()
