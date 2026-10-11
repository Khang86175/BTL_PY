"""Tetris skeleton Ngày 1-3: cửa sổ + lưới + spawn/vẽ khối + rơi cơ bản.
Chạy: pip install pygame && python main.py
Phím: Left/Right di chuyển, giữ Down soft-drop, Space hard-drop, Up xoay.
"""
import pygame
import settings
from pieces import new_piece

SOFT_DROP_SPEED = 0.05  # giây / ô khi giữ Down

pygame.init()
screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
pygame.display.set_caption("Tetris - Skeleton")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 20)

# grid lưu màu từng ô, BLACK = ô trống
grid = [[settings.BLACK for _ in range(settings.COLS)] for _ in range(settings.ROWS)]

current = new_piece()
fall_timer = 0.0


def valid(shape, px, py):
    for r, row in enumerate(shape):
        for c, v in enumerate(row):
            if not v:
                continue
            x, y = px + c, py + r
            if x < 0 or x >= settings.COLS or y >= settings.ROWS:
                return False
            if y >= 0 and grid[y][x] != settings.BLACK:
                return False
    return True


def lock(piece):
    for (x, y) in piece.cells():
        if y >= 0:
            grid[y][x] = piece.color
    # TODO Ngày 6: gọi clear_lines() ở đây


def spawn():
    global current, fall_timer
    current = new_piece()
    fall_timer = 0.0
    if not valid(current.shape, current.x, current.y):
        # TODO Ngày 8: màn hình Game Over đẹp hơn
        print("GAME OVER")
        # reset board để test tiếp
        for r in range(settings.ROWS):
            for c in range(settings.COLS):
                grid[r][c] = settings.BLACK
        current = new_piece()


def hard_drop():
    """Bay xuống ngay lập tức, lock và spawn khối mới."""
    global fall_timer
    while valid(current.shape, current.x, current.y + 1):
        current.y += 1
    lock(current)
    spawn()
    fall_timer = 0.0


def draw():
    screen.fill(settings.BLACK)
    # vẽ ô đã lock
    for r in range(settings.ROWS):
        for c in range(settings.COLS):
            rect = pygame.Rect(c * settings.CELL, r * settings.CELL,
                               settings.CELL, settings.CELL)
            pygame.draw.rect(screen, grid[r][c], rect)
            pygame.draw.rect(screen, settings.GRID_LINE, rect, 1)
    # vẽ khối đang rơi
    for (x, y) in current.cells():
        if y >= 0:
            rect = pygame.Rect(x * settings.CELL, y * settings.CELL,
                               settings.CELL, settings.CELL)
            pygame.draw.rect(screen, current.color, rect)
            pygame.draw.rect(screen, settings.WHITE, rect, 1)
    # panel bên
    txt = font.render(f"Kind: {current.kind}", True, settings.WHITE)
    screen.blit(txt, (settings.COLS * settings.CELL + 20, 20))
    txt2 = font.render("Down: soft-drop", True, settings.WHITE)
    screen.blit(txt2, (settings.COLS * settings.CELL + 20, 50))
    txt3 = font.render("Space: hard-drop", True, settings.WHITE)
    screen.blit(txt3, (settings.COLS * settings.CELL + 20, 80))
    # TODO Ngày 7: Score / Level / Next piece
    pygame.display.flip()


running = True
while running:
    dt = clock.tick(settings.FPS) / 1000.0
    fall_timer += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and valid(current.shape, current.x - 1, current.y):
                current.x -= 1
            elif event.key == pygame.K_RIGHT and valid(current.shape, current.x + 1, current.y):
                current.x += 1
            elif event.key == pygame.K_UP:
                rotated = current.rotate()
                # wall-kick đơn giản: thử x, x-1, x+1
                for dx in (0, -1, 1):
                    if valid(rotated, current.x + dx, current.y):
                        current.shape = rotated
                        current.x += dx
                        break
            elif event.key == pygame.K_SPACE:
                hard_drop()

    # giữ Down = soft-drop (rơi nhanh hơn), thả ra = tốc độ thường
    keys = pygame.key.get_pressed()
    speed = SOFT_DROP_SPEED if keys[pygame.K_DOWN] else settings.FALL_SPEED

    # rơi tự động
    if fall_timer >= speed:
        fall_timer = 0.0
        if valid(current.shape, current.x, current.y + 1):
            current.y += 1
        else:
            lock(current)
            spawn()

    draw()

pygame.quit()
