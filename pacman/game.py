from browser import document, timer
import math
import random

# Base settings (reference size)
BASE_WIDTH = 800
BASE_HEIGHT = 600
TILE_SIZE = 32

# Colors (RGB tuples)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
PINK = (255, 182, 193)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
BLUE = (0, 82, 155)
WHITE = (255, 255, 255)
YELLOW_TEXT = (255, 255, 0)

# Game variables
score = 0
high_score = 0
game_over = False
ready_timer = 60
extra_ghost_spawned = False
paused = False
WIDTH = BASE_WIDTH
HEIGHT = BASE_HEIGHT

canvas = document["gameCanvas"]
ctx = canvas.getContext("2d")
canvas.width = WIDTH
canvas.height = HEIGHT

# Maze (same as original)
maze = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

def get_random_spawn(exclude_positions, min_distance=100):
    while True:
        grid_x = random.randint(2, len(maze[0]) - 3)
        grid_y = random.randint(2, len(maze) - 3)
        x = grid_x * TILE_SIZE + TILE_SIZE // 2  # Center-aligned
        y = grid_y * TILE_SIZE + TILE_SIZE // 2  # Center-aligned
        if (maze[grid_y][grid_x] == 0 and 
            all(math.hypot(x - pos[0], y - pos[1]) > min_distance for pos in exclude_positions)):
            return x, y

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 4  # Unified speed with ghosts
        self.radius = 14
        self.target_x = x
        self.target_y = y

    def move(self, dx, dy):
        grid_x = int(self.x // TILE_SIZE)
        grid_y = int(self.y // TILE_SIZE)
        new_grid_x = grid_x + dx
        new_grid_y = grid_y + dy
        if 1 <= new_grid_x < len(maze[0]) - 1 and 1 <= new_grid_y < len(maze) - 1:
            new_target_x = new_grid_x * TILE_SIZE + TILE_SIZE // 2  # Center-aligned
            new_target_y = new_grid_y * TILE_SIZE + TILE_SIZE // 2  # Center-aligned
            if not self.collides(new_target_x, new_target_y):
                self.target_x = new_target_x
                self.target_y = new_target_y

    def update(self):
        if abs(self.x - self.target_x) > 1:
            if self.x < self.target_x:
                self.x = min(self.x + self.speed, self.target_x)
            elif self.x > self.target_x:
                self.x = max(self.x - self.speed, self.target_x)
        if abs(self.y - self.target_y) > 1:
            if self.y < self.target_y:
                self.y = min(self.y + self.speed, self.target_y)
            elif self.y > self.target_y:
                self.y = max(self.y - self.speed, self.target_y)

    def collides(self, x, y):
        grid_x = int(x // TILE_SIZE)
        grid_y = int(y // TILE_SIZE)
        if 0 <= grid_x < len(maze[0]) and 0 <= grid_y < len(maze):
            return maze[grid_y][grid_x] == 1
        return True

    def draw(self, caught=False):
        ctx.beginPath()
        ctx.arc(self.x, self.y, self.radius, 0, 2 * math.pi)
        ctx.fillStyle = f"rgb{YELLOW}"
        ctx.fill()
        ctx.closePath()
        eye_offset = self.radius // 3
        eye_radius = self.radius // 4
        ctx.beginPath()
        ctx.arc(self.x - eye_offset, self.y - eye_offset, eye_radius, 0, 2 * math.pi)
        ctx.fillStyle = f"rgb{BLACK}"
        ctx.fill()
        ctx.closePath()
        ctx.beginPath()
        ctx.arc(self.x + eye_offset, self.y - eye_offset, eye_radius, 0, 2 * math.pi)
        ctx.fill()
        ctx.closePath()
        if not caught:  # Smiling face when running
            ctx.beginPath()
            ctx.arc(self.x, self.y, self.radius * 0.8, math.pi / 6, 5 * math.pi / 6)
            ctx.lineTo(self.x, self.y)
            ctx.fillStyle = f"rgb{BLACK}"
            ctx.fill()
            ctx.closePath()
        else:  # Sad face when caught
            ctx.beginPath()
            ctx.arc(self.x, self.y - self.radius * 0.6, self.radius * 0.8, 7 * math.pi / 6, 11 * math.pi / 6)
            ctx.lineTo(self.x, self.y)
            ctx.fillStyle = f"rgb{BLACK}"
            ctx.fill()
            ctx.closePath()

class Ghost:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.speed = 3  # Unified speed with player
        self.color = color
        self.radius = TILE_SIZE // 2 - 2
        self.target_x = x
        self.target_y = y

    def move_towards(self, target_x, target_y, other_ghosts):
        grid_x = int(self.x // TILE_SIZE)
        grid_y = int(self.y // TILE_SIZE)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        valid_moves = []
        for dx, dy in directions:
            new_grid_x = grid_x + dx
            new_grid_y = grid_y + dy
            if 1 <= new_grid_x < len(maze[0]) - 1 and 1 <= new_grid_y < len(maze) - 1:
                new_x = new_grid_x * TILE_SIZE + TILE_SIZE // 2  # Center-aligned
                new_y = new_grid_y * TILE_SIZE + TILE_SIZE // 2  # Center-aligned
                if (not self.collides(new_x, new_y) and 
                    all(math.hypot(new_x - g.x, new_y - g.y) > self.radius + g.radius - 4 for g in other_ghosts if g != self)):
                    valid_moves.append((new_x, new_y))
        if valid_moves:
            best_move = min(valid_moves, key=lambda pos: math.hypot(target_x - pos[0], target_y - pos[1]))
            self.target_x, self.target_y = best_move
        else:
            for dx, dy in directions:
                new_grid_x = grid_x + dx
                new_grid_y = grid_y + dy
                if 1 <= new_grid_x < len(maze[0]) - 1 and 1 <= new_grid_y < len(maze) - 1:
                    new_x = new_grid_x * TILE_SIZE + TILE_SIZE // 2
                    new_y = new_grid_y * TILE_SIZE + TILE_SIZE // 2
                    if not self.collides(new_x, new_y):
                        self.target_x, self.target_y = new_x, new_y
                        break

    def update(self):
        if abs(self.x - self.target_x) > 1:
            if self.x < self.target_x:
                self.x = min(self.x + self.speed, self.target_x)
            elif self.x > self.target_x:
                self.x = max(self.x - self.speed, self.target_x)
        if abs(self.y - self.target_y) > 1:
            if self.y < self.target_y:
                self.y = min(self.y + self.speed, self.target_y)
            elif self.y > self.target_y:
                self.y = max(self.y - self.speed, self.target_y)

    def collides(self, x, y):
        grid_x = int(x // TILE_SIZE)
        grid_y = int(y // TILE_SIZE)
        if 0 <= grid_x < len(maze[0]) and 0 <= grid_y < len(maze):
            return maze[grid_y][grid_x] == 1
        return True

    def draw(self):
        ctx.beginPath()
        ctx.arc(self.x, self.y, self.radius, 0, 2 * math.pi)
        ctx.fillStyle = f"rgb{self.color}"
        ctx.fill()
        ctx.closePath()
        eye_offset = self.radius // 2
        pupil_offset = eye_offset // 2
        ctx.beginPath()
        ctx.arc(self.x - eye_offset, self.y - pupil_offset, eye_offset, 0, 2 * math.pi)
        ctx.fillStyle = f"rgb{WHITE}"
        ctx.fill()
        ctx.closePath()
        ctx.beginPath()
        ctx.arc(self.x + eye_offset, self.y - pupil_offset, eye_offset, 0, 2 * math.pi)
        ctx.fill()
        ctx.closePath()
        ctx.beginPath()
        ctx.arc(self.x - eye_offset + 2, self.y - pupil_offset, pupil_offset, 0, 2 * math.pi)
        ctx.fillStyle = f"rgb{BLACK}"
        ctx.fill()
        ctx.closePath()
        ctx.beginPath()
        ctx.arc(self.x + eye_offset + 2, self.y - pupil_offset, pupil_offset, 0, 2 * math.pi)
        ctx.fill()
        ctx.closePath()

def reset_game():
    global player, ghosts, dots, game_over, score, ready_timer, high_score, extra_ghost_spawned, paused
    ghost_spawns = [
        (11 * TILE_SIZE + TILE_SIZE // 2, 5 * TILE_SIZE + TILE_SIZE // 2),
        (13 * TILE_SIZE + TILE_SIZE // 2, 5 * TILE_SIZE + TILE_SIZE // 2),
        (11 * TILE_SIZE + TILE_SIZE // 2, 6 * TILE_SIZE + TILE_SIZE // 2),
        (13 * TILE_SIZE + TILE_SIZE // 2, 6 * TILE_SIZE + TILE_SIZE // 2),
    ]
    ghosts[:] = [Ghost(spawn_x, spawn_y, color) for (spawn_x, spawn_y), color in zip(ghost_spawns, [RED, PINK, CYAN, ORANGE])]
    ghost_positions = [(g.x, g.y) for g in ghosts]
    player_x, player_y = get_random_spawn(ghost_positions)
    player = Player(player_x, player_y)
    dots[:] = [(x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2) 
               for y in range(len(maze)) for x in range(len(maze[0])) if maze[y][x] == 0]
    game_over = False
    score = 0
    ready_timer = 60
    extra_ghost_spawned = False
    paused = False

player = Player(0, 0)
ghosts = []
dots = []

# Input handling (Keyboard only for now)
keys = {"left": False, "right": False, "up": False, "down": False}
def keydown(evt):
    global paused
    if evt.keyCode == 37:  # Left arrow
        keys["left"] = True
    elif evt.keyCode == 39:  # Right arrow
        keys["right"] = True
    elif evt.keyCode == 38:  # Up arrow
        keys["up"] = True
    elif evt.keyCode == 40:  # Down arrow
        keys["down"] = True
    elif evt.keyCode == 82 and game_over:  # 'R' key
        reset_game()
    elif evt.keyCode == 32 and not game_over:  # Spacebar
        paused = not paused

def keyup(evt):
    if evt.keyCode == 37:
        keys["left"] = False
    elif evt.keyCode == 39:
        keys["right"] = False
    elif evt.keyCode == 38:
        keys["up"] = False
    elif evt.keyCode == 40:
        keys["down"] = False

document.bind("keydown", keydown)
document.bind("keyup", keyup)

def game_loop():
    global game_over, ready_timer, score, high_score, extra_ghost_spawned
    if not game_over and ready_timer > 0:
        ready_timer -= 1
        if ready_timer == 0:
            game_over = False

    if not game_over and ready_timer <= 0 and not paused:
        if keys["left"]:
            player.move(-1, 0)
        if keys["right"]:
            player.move(1, 0)
        if keys["up"]:
            player.move(0, -1)
        if keys["down"]:
            player.move(0, 1)
        player.update()

        for ghost in ghosts:
            ghost.move_towards(player.x, player.y, ghosts)
            ghost.update()

        i = 0
        while i < len(dots):
            dot = dots[i]
            if math.hypot(player.x - dot[0], player.y - dot[1]) < player.radius:
                dots.pop(i)
                score += 1
                if score > high_score:
                    high_score = score
            else:
                i += 1

        if score >= 100 and not extra_ghost_spawned:
            ghost_positions = [(g.x, g.y) for g in ghosts]
            extra_x, extra_y = get_random_spawn(ghost_positions)
            ghosts.append(Ghost(extra_x, extra_y, PURPLE))
            extra_ghost_spawned = True

        for ghost in ghosts:
            if math.hypot(player.x - ghost.x, player.y - ghost.y) < player.radius + ghost.radius:
                game_over = True
                break

    ctx.clearRect(0, 0, WIDTH, HEIGHT)
    ctx.fillStyle = f"rgb{BLACK}"
    ctx.fillRect(0, 0, WIDTH, HEIGHT)
    for y in range(len(maze)):
        for x in range(len(maze[0])):
            if maze[y][x] == 1:
                ctx.fillStyle = f"rgb{BLUE}"
                ctx.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    for dot in dots:
        ctx.beginPath()
        ctx.arc(dot[0], dot[1], 4, 0, 2 * math.pi)
        ctx.fillStyle = f"rgb{WHITE}"
        ctx.fill()
        ctx.closePath()
    player.draw(game_over)
    for ghost in ghosts:
        ghost.draw()

    ctx.font = "24px Comic Sans MS"
    ctx.fillStyle = f"rgb{YELLOW_TEXT}"
    ctx.fillText(f"Score: {score:03d}", 10, 27)
    ctx.fillText(f"High: {high_score:03d}", 680, 27)

    if ready_timer > 0:
        ctx.font = "48px Comic Sans MS"
        ctx.fillText("Ready!", WIDTH // 2 - 60, HEIGHT // 2)

    if game_over:
        ctx.font = "48px Comic Sans MS"
        ctx.fillStyle = f"rgb{WHITE}"
        ctx.fillText("GAME OVER", WIDTH // 2 - 120, HEIGHT // 2)
        ctx.fillText("Press R to Restart", WIDTH // 2 - 180, HEIGHT // 2 + 60)

    if paused and not game_over:
        ctx.font = "48px Comic Sans MS"
        ctx.fillStyle = f"rgb{WHITE}"
        ctx.fillText("Paused", WIDTH // 2 - 80, HEIGHT // 2)
        ctx.fillText("Press SPACE to Resume", WIDTH // 2 - 220, HEIGHT // 2 + 60)

reset_game()
timer.set_interval(game_loop, 16)  # ~60 FPS