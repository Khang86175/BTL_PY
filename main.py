"""main.py: vong lap game chinh.
Trang thai: MENU chon che do -> MENU chon do kho -> PLAYING (1P).
Menu: W/S hoac Up/Down di chuyen, Space/Enter chon, ESC quay lui.
Game 1P: A/D (giu de di lien tuc), giu S roi nhanh, W xoay,
Space roi ngay. P pause, R choi lai khi thua, ESC ve menu.
"""
import pygame
import settings
from game import Board
from menu import Menu

# --- Khoi tao pygame: bat buoc truoc khi dung display/font ---
pygame.init()
# Cua so voi kich thuoc lay tu settings (board + panel).
screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
pygame.display.set_caption("Tetris 1P")
# clock de gioi han FPS + tinh dt (thoi gian moi frame).
clock = pygame.time.Clock()
# 2 co chu: font lon cho tieu de/diem, small_font cho huong dan.
font = pygame.font.SysFont("consolas", 24)
small_font = pygame.font.SysFont("consolas", 18)

menu = Menu()
# Board mac dinh, se tao lai dung do kho khi chon menu xong.
board = Board(difficulty="easy")
# state: "menu" (chon che do/do kho), "playing" (choi 1P),
# "wip_2p" (man hinh cho che do 2P se lam o Ngay 5-6).
state = "menu"
paused = False  # co tam dung, bat/tat bang phim P

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
    board = Board(difficulty=difficulty)
    paused = False
    reset_hold_timers()
    state = "playing"


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
                    if action == "need_2p":
                        # Che do 2P se lam o Ngay 5-6, hien man hinh cho.
                        state = "wip_2p"
                    elif action == "start_1p":
                        start_1p(data)
                    # "goto_diff" thi menu tu chuyen stage, khong can lam gi.
                elif event.key == pygame.K_ESCAPE:
                    menu.back()  # tu man hinh do kho lui ve man hinh che do
            elif state == "wip_2p":
                # Man hinh cho 2P: phim nao cung ve lai menu che do.
                if event.key in (pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN):
                    menu.reset()
                    state = "menu"
            elif state == "playing":
                if event.key == pygame.K_ESCAPE:
                    # Ve menu de doi che do/do kho, dong ho giu phim reset theo.
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

    # 3. Ve theo trang thai hien tai.
    if state == "menu":
        menu.draw(screen, font, small_font)
    elif state == "wip_2p":
        # Man hinh cho tam thoi, se thay bang game 2P that o Ngay 5-6.
        screen.fill(settings.BLACK)
        cx = settings.WIDTH // 2
        t1 = font.render("Che do 2 nguoi choi", True, settings.WHITE)
        t2 = small_font.render("dang phat trien (Ngay 5-6)", True, settings.WHITE)
        t3 = small_font.render("Nhan ESC de quay lai", True, settings.WHITE)
        screen.blit(t1, (cx - t1.get_width() // 2, 220))
        screen.blit(t2, (cx - t2.get_width() // 2, 260))
        screen.blit(t3, (cx - t3.get_width() // 2, 300))
    else:
        screen.fill(settings.BLACK)
        board.draw(screen, 0, font, small_font)
        # Dong huong dan phim o goc panel.
        screen.blit(small_font.render("A/D move  S hold  W rot", True, settings.WHITE), (310, 400))
        screen.blit(small_font.render("Space drop  P pause", True, settings.WHITE), (310, 425))
        screen.blit(small_font.render("ESC menu", True, settings.WHITE), (310, 450))
        # Chu phu khi pause hoac thua.
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

    pygame.display.flip()  # day khung hinh moi len man hinh

pygame.quit()
