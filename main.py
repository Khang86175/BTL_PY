"""main.py: vong lap game chinh.
Trang thai: MENU chon che do -> MENU chon do kho -> PLAYING (1P hoac 2P).
Menu: W/S hoac Up/Down di chuyen, Space/Enter chon, ESC quay lui.
Game 1P: A/D (giu de di lien tuc), giu S roi nhanh, W xoay,
Space roi ngay. P pause, R choi lai khi thua, ESC ve menu.
Game 2P: P1 dung A/S/D/W/Space, P2 dung mui ten + Enter.
2 board doc chung 1 chuoi khoi (SharedSequence) nen khoi 2 ben
giong het nhau. Ai het cho truoc (game over) thi thua, hien ket qua
va cho R choi van moi.
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
# difficulty_2p: nho do kho da chon de R co the choi lai cung do kho.
difficulty_2p = "easy"

# Bo phim cua tung nguoi choi 2P: P1 = WASD + Space, P2 = mui ten + Enter.
P2P_KEYS = [
    {"left": pygame.K_a, "right": pygame.K_d, "rotate": pygame.K_w,
     "soft": pygame.K_s, "hard": pygame.K_SPACE},
    {"left": pygame.K_LEFT, "right": pygame.K_RIGHT, "rotate": pygame.K_UP,
     "soft": pygame.K_DOWN, "hard": pygame.K_RETURN},
]
# Dong ho giu phim A/D cua tung nguoi choi (kieu DAS cua Tetris):
# [hold_left, repeat_left, hold_right, repeat_right] cho moi nguoi.
hold_timers = [[0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]]


def reset_hold_timers(idx=0):
    # Reset dong ho giu phim khi doi trang thai de khong bi troi phim.
    hold_timers[idx][:] = [0.0, 0.0, 0.0, 0.0]


def move_hold(b, keys, keyset, timers, dt):
    # Giu A/D (hoac mui ten) di lien tuc kieu DAS: frame dau di ngay 1 o,
    # giu qua MOVE_DAS thi cu moi MOVE_INTERVAL di them 1 o. Giu ca 2
    # phim cung luc thi dung yen. timers = [hl, rl, hr, rr].
    left = keys[keyset["left"]]
    right = keys[keyset["right"]]
    if left and not right:
        if timers[0] == 0.0:
            b.try_move(-1)  # moi nhan xuong thi di ngay, khong cho
        timers[0] += dt
        timers[2] = 0.0
        timers[3] = 0.0
        if timers[0] >= settings.MOVE_DAS:
            timers[1] += dt
            while timers[1] >= settings.MOVE_INTERVAL:
                timers[1] -= settings.MOVE_INTERVAL
                b.try_move(-1)
    elif right and not left:
        if timers[2] == 0.0:
            b.try_move(1)
        timers[2] += dt
        timers[0] = 0.0
        timers[1] = 0.0
        if timers[2] >= settings.MOVE_DAS:
            timers[3] += dt
            while timers[3] >= settings.MOVE_INTERVAL:
                timers[3] -= settings.MOVE_INTERVAL
                b.try_move(1)
    else:
        timers[:] = [0.0, 0.0, 0.0, 0.0]


def start_1p(difficulty):
    # Bat dau van 1P moi voi do kho da chon o menu.
    global board, state, paused
    pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
    pygame.display.set_caption("Tetris 1P")
    board = Board(difficulty=difficulty)
    paused = False
    reset_hold_timers(0)
    state = "playing"


def start_2p(difficulty):
    # Bat dau van 2P: cua so rong gap doi, 2 board doc chung 1 SharedSequence
    # nen 2 ben nhan dung cung thu tu khoi (chinh la yeu cau cong bang).
    global boards_2p, shared, state, paused, difficulty_2p
    pygame.display.set_mode((settings.WIDTH_2P, settings.HEIGHT))
    pygame.display.set_caption("Tetris 2P")
    difficulty_2p = difficulty
    shared = SharedSequence()
    boards_2p = [Board(difficulty=difficulty, shared=shared),
                 Board(difficulty=difficulty, shared=shared)]
    paused = False
    reset_hold_timers(0)
    reset_hold_timers(1)
    state = "playing_2p"


def draw_board(b, origin_x, label, show_help=False):
    # Ve 1 board tai vi tri origin_x + nhan ten nguoi choi goc phai panel.
    b.draw(screen, origin_x, font, small_font)
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


def draw_2p_overlay():
    # Phu ket qua khi CA 2 ben deu thua: lam mo ca 2 board roi hien
    # ket qua (ai diem cao hon thi thang, bang diem thi hoa) + diem
    # 2 ben + nhac R choi lai.
    shade = pygame.Surface((settings.WIDTH_2P, settings.HEIGHT))
    shade.set_alpha(180)
    shade.fill(settings.BLACK)
    screen.blit(shade, (0, 0))
    cx = settings.WIDTH_2P // 2
    # So sanh diem 2 ben khi da het tran.
    score1, score2 = boards_2p[0].score, boards_2p[1].score
    if score1 > score2:
        title = "P1 THANG!"
    elif score2 > score1:
        title = "P2 THANG!"
    else:
        title = "HOA!"
    t1 = font.render(title, True, settings.WHITE)
    screen.blit(t1, (cx - t1.get_width() // 2, 200))
    s1 = small_font.render(f"P1: {score1} diem", True, settings.WHITE)
    s2 = small_font.render(f"P2: {score2} diem", True, settings.WHITE)
    screen.blit(s1, (cx - s1.get_width() // 2, 250))
    screen.blit(s2, (cx - s2.get_width() // 2, 275))
    r1 = small_font.render("R: choi lai  |  ESC: ve menu", True, settings.WHITE)
    screen.blit(r1, (cx - r1.get_width() // 2, 320))


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
                    reset_hold_timers(0)
                    state = "menu"
                elif event.key == pygame.K_p:
                    paused = not paused  # bat/tat pause
                    reset_hold_timers(0)
                elif board.game_over and event.key == pygame.K_r:
                    board.reset()  # thua -> R de choi van moi
                    paused = False
                    reset_hold_timers(0)
                elif not paused and not board.game_over:
                    # A/D KHONG xu ly o day ma o phan giu phim ben duoi,
                    # de giu phim la khoi tu di lien tuc (khoi bam nhieu lan).
                    if event.key == pygame.K_w:
                        board.try_rotate()
                    elif event.key == pygame.K_SPACE:
                        board.hard_drop()
            elif state == "playing_2p":
                # Tran chi ket thuc khi CA 2 ben deu thua. Ben nao con
                # choi duoc thi tiep tuc roi den khi het cho.
                match_over = all(b.game_over for b in boards_2p)
                if event.key == pygame.K_ESCAPE:
                    pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
                    menu.reset()
                    paused = False
                    reset_hold_timers(0)
                    reset_hold_timers(1)
                    state = "menu"
                elif event.key == pygame.K_p and not match_over:
                    paused = not paused
                    reset_hold_timers(0)
                    reset_hold_timers(1)
                elif match_over and event.key == pygame.K_r:
                    # Rematch: van moi cung do kho, van dung chuoi chung.
                    start_2p(difficulty_2p)
                elif not paused and not match_over:
                    # Xoay / roi ngay theo bo phim rieng tung nguoi choi.
                    # A/D cua P1 (va mui ten trai/phai cua P2) xu ly o phan
                    # giu phim ben duoi de di duoc lien tuc. Ben nao da thua
                    # thi bo qua phim cua ben do.
                    for i, b in enumerate(boards_2p):
                        if b.game_over:
                            continue
                        ks = P2P_KEYS[i]
                        if event.key == ks["rotate"]:
                            b.try_rotate()
                        elif event.key == ks["hard"]:
                            b.hard_drop()

    # 2. Giua cac frame: giu phim di lien tuc + roi nhanh (khac KEYDOWN 1 lan).
    keys = pygame.key.get_pressed()  # trang thai giu phim tai frame nay
    if state == "playing":
        if not paused and not board.game_over:
            move_hold(board, keys, P2P_KEYS[0], hold_timers[0], dt)
            # Giu S thi soft_drop_held=True -> roi sieu nhanh.
            board.update(dt, soft_drop_held=keys[P2P_KEYS[0]["soft"]])
    elif state == "playing_2p" and not paused and not all(b.game_over for b in boards_2p):
        # Moi ben co bo phim + dong ho + soft-drop rieng, nhung cung dt
        # nen toc do roi giong nhau. Ben nao da thua thi khong update nua,
        # ben con lai choi tiep.
        for i, b in enumerate(boards_2p):
            if b.game_over:
                continue
            move_hold(b, keys, P2P_KEYS[i], hold_timers[i], dt)
            b.update(dt, soft_drop_held=keys[P2P_KEYS[i]["soft"]])

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
        if all(b.game_over for b in boards_2p):
            draw_2p_overlay()  # ca 2 ben deu thua -> hien ket qua + nhac R
        elif paused:
            screen.blit(font.render("PAUSE - P", True, settings.WHITE),
                        (settings.WIDTH_2P // 2 - 70, 280))

    pygame.display.flip()  # day khung hinh moi len man hinh

pygame.quit()
