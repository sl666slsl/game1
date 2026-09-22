import pygame
import sys
import random

# --- 初始化 ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("一箭又一箭 - 软件工程作业")

# --- 颜色定义 ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (220, 220, 220)
BLUE = (50, 150, 255)
RED = (255, 50, 50)
GREEN = (50, 200, 50)

# --- 游戏常量 ---
GRID_SIZE = 55
GRID_COLS = 10
GRID_ROWS = 8
GRID_OFFSET_X = (WIDTH - GRID_COLS * GRID_SIZE) // 2
GRID_OFFSET_Y = 120

# --- 游戏状态 ---
STATE_START = 0
STATE_PLAYING = 1
STATE_WIN = 2    # 单关通关
STATE_LOSE = 3   # 失败
STATE_ALL_WIN = 4 # 全部通关

# --- 字体 ---
try:
    font_large = pygame.font.SysFont("simhei", 48)
    font_medium = pygame.font.SysFont("simhei", 28)
    font_small = pygame.font.SysFont("simhei", 20)
except:
    font_large = pygame.font.Font(None, 48)
    font_medium = pygame.font.Font(None, 28)
    font_small = pygame.font.Font(None, 20)

# --- 关卡数据 (行, 列, 方向) ---
LEVELS = [
    # 关卡 1: 非常简单
    [
        (0, 0, 'right'),
        (0, 1, 'right'),
        (0, 2, 'right'),
    ],
    # 关卡 2: 稍微复杂
    [
        (0, 0, 'down'),
        (1, 0, 'right'),
        (1, 1, 'right'),
        (1, 2, 'up'),
        (0, 2, 'right'),
    ],
    # 关卡 3: 新的设计，确保有解且直观
    [
        (0, 0, 'down'),    # 1. 先点它，下方空
        (1, 0, 'right'),   # 2. 再点它，右边空
        (1, 1, 'down'),    # 3. 再点它，下方空
        (2, 1, 'right'),   # 4. 再点它，右边空
        (2, 2, 'up'),      # 5. 再点它，上方空
        (0, 2, 'right'),   # 6. 最后点它，右边是边界
    ]
]

# --- 全局变量 ---
current_level_index = 0
board = []
mistakes = 0
max_mistakes = 3
state = STATE_START
shake_timer = 0
shake_pos = (0, 0)
flying_arrows = []

# --- 函数 ---

def build_board(level_data):
    b = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    for r, c, d in level_data:
        if 0 <= r < GRID_ROWS and 0 <= c < GRID_COLS:
            b[r][c] = d
    return b

def count_arrows(b):
    count = 0
    for row in b:
        for cell in row:
            if cell is not None:
                count += 1
    return count

def get_grid_pos(mx, my):
    if mx < GRID_OFFSET_X or mx >= GRID_OFFSET_X + GRID_COLS * GRID_SIZE:
        return None
    if my < GRID_OFFSET_Y or my >= GRID_OFFSET_Y + GRID_ROWS * GRID_SIZE:
        return None
    col = (mx - GRID_OFFSET_X) // GRID_SIZE
    row = (my - GRID_OFFSET_Y) // GRID_SIZE
    return (int(row), int(col))

def check_path(b, row, col, direction):
    """检查路径是否畅通，返回 True 表示可以飞出"""
    if direction == 'right':
        for c in range(col + 1, GRID_COLS):
            if b[row][c] is not None:
                return False
        return True
    elif direction == 'left':
        for c in range(col - 1, -1, -1):
            if b[row][c] is not None:
                return False
        return True
    elif direction == 'down':
        for r in range(row + 1, GRID_ROWS):
            if b[r][col] is not None:
                return False
        return True
    elif direction == 'up':
        for r in range(row - 1, -1, -1):
            if b[r][col] is not None:
                return False
        return True
    return False

def draw_arrow(surface, cx, cy, direction, color, size=20):
    if direction == 'up':
        points = [(cx, cy - size), (cx - size*0.7, cy + size*0.7), (cx + size*0.7, cy + size*0.7)]
    elif direction == 'down':
        points = [(cx, cy + size), (cx - size*0.7, cy - size*0.7), (cx + size*0.7, cy - size*0.7)]
    elif direction == 'left':
        points = [(cx - size, cy), (cx + size*0.7, cy - size*0.7), (cx + size*0.7, cy + size*0.7)]
    elif direction == 'right':
        points = [(cx + size, cy), (cx - size*0.7, cy - size*0.7), (cx - size*0.7, cy + size*0.7)]
    else:
        return
    pygame.draw.polygon(surface, color, points)
    pygame.draw.polygon(surface, BLACK, points, 2)

def reset_level():
    """重置当前关卡"""
    global board, mistakes, shake_timer, flying_arrows
    board = build_board(LEVELS[current_level_index])
    mistakes = 0
    shake_timer = 0
    flying_arrows = []

def start_game():
    """从第一关开始"""
    global current_level_index, state
    current_level_index = 0
    reset_level()
    state = STATE_PLAYING

def next_level():
    """进入下一关"""
    global current_level_index, state
    current_level_index += 1
    if current_level_index >= len(LEVELS):
        # 所有关卡通关
        current_level_index = 0
        state = STATE_ALL_WIN
    else:
        reset_level()
        state = STATE_PLAYING

# --- 主循环 ---
clock = pygame.time.Clock()
running = True
reset_level()

while running:
    # 1. 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            
            # 开始界面
            if state == STATE_START:
                start_game()
            
            # 单关通关界面（点击进入下一关）
            elif state == STATE_WIN:
                next_level()
            
            # 全部通关界面（点击重新开始）
            elif state == STATE_ALL_WIN:
                start_game()
            
            # 失败界面
            elif state == STATE_LOSE:
                start_game()
            
            # 游戏中
            elif state == STATE_PLAYING:
                # 检查是否点击了右上角“重新开始”按钮
                if 650 <= mx <= 770 and 20 <= my <= 60:
                    reset_level()
                    continue
                
                # 检查网格点击
                pos = get_grid_pos(mx, my)
                if pos:
                    r, c = pos
                    direction = board[r][c]
                    if direction is not None:
                        if check_path(board, r, c, direction):
                            # 飞出
                            board[r][c] = None
                            dx, dy = 0, 0
                            if direction == 'right': dx = 10
                            elif direction == 'left': dx = -10
                            elif direction == 'down': dy = 10
                            elif direction == 'up': dy = -10
                            
                            start_x = GRID_OFFSET_X + c * GRID_SIZE + GRID_SIZE // 2
                            start_y = GRID_OFFSET_Y + r * GRID_SIZE + GRID_SIZE // 2
                            flying_arrows.append([start_x, start_y, dx, dy, BLUE])
                            
                            # 判断当前关卡是否清空
                            if count_arrows(board) == 0:
                                state = STATE_WIN
                        else:
                            # 碰撞
                            mistakes += 1
                            shake_timer = 15
                            if mistakes >= max_mistakes:
                                state = STATE_LOSE

    # 2. 更新逻辑
    if shake_timer > 0:
        shake_timer -= 1
        shake_pos = (random.randint(-4, 4), random.randint(-4, 4))
    else:
        shake_pos = (0, 0)
    
    for arrow in flying_arrows[:]:
        arrow[0] += arrow[2]
        arrow[1] += arrow[3]
        if arrow[0] < -50 or arrow[0] > WIDTH + 50 or arrow[1] < -50 or arrow[1] > HEIGHT + 50:
            flying_arrows.remove(arrow)

    # 3. 绘制
    screen.fill(GRAY)
    
    if state == STATE_START:
        title = font_large.render("一箭又一箭", True, BLACK)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 200))
        tip = font_medium.render("点击屏幕开始游戏", True, BLUE)
        screen.blit(tip, (WIDTH//2 - tip.get_width()//2, 300))
        tip2 = font_small.render("规则：点击箭头使其飞出，前方有阻挡则失误+1，失误3次失败", True, BLACK)
        screen.blit(tip2, (WIDTH//2 - tip2.get_width()//2, 400))

    elif state == STATE_WIN:
        win_text = font_large.render("恭喜通关本关！", True, GREEN)
        screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, 230))
        tip = font_medium.render("点击屏幕进入下一关", True, BLACK)
        screen.blit(tip, (WIDTH//2 - tip.get_width()//2, 330))
        # 显示当前是第几关
        level_info = font_small.render(f"当前关卡: {current_level_index + 1} / {len(LEVELS)}", True, BLACK)
        screen.blit(level_info, (WIDTH//2 - level_info.get_width()//2, 390))

    elif state == STATE_ALL_WIN:
        all_win_text = font_large.render("全部通关！", True, GREEN)
        screen.blit(all_win_text, (WIDTH//2 - all_win_text.get_width()//2, 230))
        tip = font_medium.render("点击屏幕重新开始游戏", True, BLACK)
        screen.blit(tip, (WIDTH//2 - tip.get_width()//2, 330))

    elif state == STATE_LOSE:
        lose_text = font_large.render("游戏失败", True, RED)
        screen.blit(lose_text, (WIDTH//2 - lose_text.get_width()//2, 250))
        tip = font_medium.render("点击屏幕重新开始", True, BLACK)
        screen.blit(tip, (WIDTH//2 - tip.get_width()//2, 350))

    elif state == STATE_PLAYING:
        # 顶部信息
        level_text = font_medium.render(f"关卡: {current_level_index + 1}/{len(LEVELS)}", True, BLACK)
        screen.blit(level_text, (30, 30))
        
        arrow_count = count_arrows(board)
        arrow_text = font_medium.render(f"剩余箭头: {arrow_count}", True, BLACK)
        screen.blit(arrow_text, (250, 30))
        
        mistake_text = font_medium.render(f"失误: {mistakes}/{max_mistakes}", True, RED if mistakes > 0 else BLACK)
        screen.blit(mistake_text, (450, 30))
        
        # 重新开始按钮
        pygame.draw.rect(screen, WHITE, (650, 20, 120, 40), border_radius=8)
        pygame.draw.rect(screen, BLACK, (650, 20, 120, 40), 2, border_radius=8)
        restart_text = font_small.render("重新开始", True, BLACK)
        screen.blit(restart_text, (650 + 60 - restart_text.get_width()//2, 20 + 20 - restart_text.get_height()//2))

        # 网格
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                rect = pygame.Rect(GRID_OFFSET_X + c * GRID_SIZE, GRID_OFFSET_Y + r * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(screen, WHITE, rect)
                pygame.draw.rect(screen, BLACK, rect, 1)

        # 箭头
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                direction = board[r][c]
                if direction is not None:
                    cx = GRID_OFFSET_X + c * GRID_SIZE + GRID_SIZE // 2
                    cy = GRID_OFFSET_Y + r * GRID_SIZE + GRID_SIZE // 2
                    color = BLUE
                    if shake_timer > 0:
                        cx += shake_pos[0]
                        cy += shake_pos[1]
                        color = RED
                    draw_arrow(screen, cx, cy, direction, color)

        # 飞行动画
        for arrow in flying_arrows:
            cx, cy, dx, dy, color = arrow
            if dx > 0: d = 'right'
            elif dx < 0: d = 'left'
            elif dy > 0: d = 'down'
            else: d = 'up'
            draw_arrow(screen, int(cx), int(cy), d, color, size=18)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()