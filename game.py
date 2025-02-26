from browser import document, timer, window
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
BLUE = (0, 82, 155)
WHITE = (255, 255, 255)
YELLOW_TEXT = (255, 255, 0)  # Added YELLOW_TEXT definition

# Game variables
WIDTH = BASE_WIDTH
HEIGHT = BASE_HEIGHT
scale_factor = 1.0

canvas = document["gameCanvas"]
ctx = canvas.getContext("2d")

# Dynamic scaling with integer enforcement
def update_canvas_size():
    global WIDTH, HEIGHT, scale_factor
    raw_width = window.innerWidth or BASE_WIDTH
    raw_height = window.innerHeight or BASE_HEIGHT
    WIDTH = int(raw_width)
    HEIGHT = int(raw_height)
    aspect_ratio = BASE_WIDTH / BASE_HEIGHT
    window_aspect = WIDTH / HEIGHT
    if window_aspect > aspect_ratio:  # Wider than 4:3
        HEIGHT = int(window.innerHeight or BASE_HEIGHT)
        WIDTH = int(HEIGHT * aspect_ratio)
    else:  # Taller than 4:3
        WIDTH = int(window.innerWidth or BASE_WIDTH)
        HEIGHT = int(WIDTH / aspect_ratio)
    WIDTH = max(1, WIDTH)  # Prevent zero or negative
    HEIGHT = max(1, HEIGHT)
    canvas.width = WIDTH
    canvas.height = HEIGHT
    scale_factor = min(WIDTH / BASE_WIDTH, HEIGHT / BASE_HEIGHT) or 1.0
    scale_factor = int(scale_factor) if scale_factor.is_integer() else int(scale_factor + 0.5)

window.bind("resize", update_canvas_size)
update_canvas_size()

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

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 4 * scale_factor
        self.radius = 14 * scale_factor
        self.target_x = x
        self.target_y = y

    def move(self, dx, dy):
        grid_x = int(self.x // (TILE_SIZE * scale_factor))
        grid_y = int(self.y // (TILE_SIZE * scale_factor))
        new_grid_x = grid_x + dx
        new_grid_y = grid_y + dy
        if 1 <= new_grid_x < len(maze[0]) - 1 and 1 <= new_grid_y < len(maze) - 1:
            new_target_x = new_grid_x * TILE_SIZE * scale_factor + (TILE_SIZE * scale_factor) // 2
            new_target_y = new_grid_y * TILE_SIZE * scale_factor + (TILE_SIZE * scale_factor) // 2
            if not self.collides(new_target_x, new_target_y):
                self.target_x = new_target_x
                self.target_y = new_target_y

    def update(self):
        if abs(self.x - self.target_x) > scale_factor:
            self.x += self.speed if self.x < self.target_x else -self.speed
            self.x = min(max(self.x, self.target_x - self.speed), self.target_x + self.speed)
        if abs(self.y - self.target_y) > scale_factor:
            self.y += self.speed if self.y < self.target_y else -self.speed
            self.y = min(max(self.y, self.target_y - self.speed), self.target_y + self.speed)

    def collides(self, x, y):
        grid_x = int(x // (TILE_SIZE * scale_factor))
        grid_y = int(y // (TILE_SIZE * scale_factor))
        if 0 <= grid_x < len(maze[0]) and 0 <= grid_y < len(maze):
            return maze[grid_y][grid_x] == 1
        return True

    def draw(self):
        ctx.beginPath()
        ctx.arc(self.x, self.y, self.radius, 0, 2 * math.pi)
        ctx.fillStyle = "rgb" + str(YELLOW)
        ctx.fill()
        ctx.closePath()

class Ghost:
    def __init__(self, x, y, color=RED):
        self.x = x
        self.y = y
        self.speed = 4 * scale_factor
        self.color = color
        self.radius = 14 * scale_factor
        self.target_x = x
        self.target_y = y
        self.direction = None  # Track last direction for random movement

    def move_towards(self, target_x, target_y, other_ghosts):
        grid_x = int(self.x // (TILE_SIZE * scale_factor))
        grid_y = int(self.y // (TILE_SIZE * scale_factor))
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Left, Right, Up, Down
        valid_moves = []

        # Check all directions for valid moves
        for dx, dy in directions:
            new_grid_x = grid_x + dx
            new_grid_y = grid_y + dy
            if 1 <= new_grid_x < len(maze[0]) - 1 and 1 <= new_grid_y < len(maze) - 1:
                new_x = new_grid_x * TILE_SIZE * scale_factor + (TILE_SIZE * scale_factor) // 2
                new_y = new_grid_y * TILE_SIZE * scale_factor + (TILE_SIZE * scale_factor) // 2
                if (not self.collides(new_x, new_y) and 
                    all(math.hypot(new_x - g.x, new_y - g.y) > self.radius + g.radius - 4 * scale_factor for g in other_ghosts if g != self)):
                    valid_moves.append((new_x, new_y, dx, dy))

        if valid_moves:
            # Prioritize moving toward the player
            best_move = min(valid_moves, key=lambda pos: math.hypot(target_x - pos[0], target_y - pos[1]))
            self.target_x, self.target_y = best_move[0], best_move[1]
            self.direction = (best_move[2], best_move[3])  # Store direction
        else:
            # If no valid move toward player, move randomly in last direction or change if blocked
            if self.direction and random.random() < 0.7:  # 70% chance to continue last direction
                dx, dy = self.direction
                new_grid_x = grid_x + dx
                new_grid_y = grid_y + dy
                if (1 <= new_grid_x < len(maze[0]) - 1 and 1 <= new_grid_y < len(maze) - 1 and 
                    not self.collides(new_grid_x * TILE_SIZE * scale_factor + (TILE_SIZE * scale_factor) // 2,
                                     new_grid_y * TILE_SIZE * scale_factor + (TILE_SIZE * scale_factor) // 2)):
                    self.target_x = new_grid_x * TILE_SIZE * scale_factor + (TILE_SIZE * scale_factor) // 2
                    self.target_y = new_grid_y * TILE_SIZE * scale_factor + (TILE_SIZE * scale_factor) // 2
                else:
                    self.direction = random.choice(directions)  # Change direction if blocked
            else:
                self.direction = random.choice(directions)  # Random new direction
            dx, dy = self.direction
            new_grid_x = grid_x + dx
            new_grid_y = grid_y + dy
            if 1 <= new_grid_x < len(maze[0]) - 1 and 1 <= new_grid_y < len(maze) - 1:
                new_x = new_grid_x * TILE_SIZE * scale_factor + (TILE_SIZE * scale_factor) // 2
                new_y = new_grid_y * TILE_SIZE * scale_factor + (TILE_SIZE * scale_factor) // 2
                if not self.collides(new_x, new_y):
                    self.target_x, self.target_y = new_x, new_y

    def update(self):
        if abs(self.x - self.target_x) > scale_factor:
            self.x += self.speed if self.x < self.target_x else -self.speed
            self.x = min(max(self.x, self.target_x - self.speed), self.target_x + self.speed)
        if abs(self.y - self.target_y) > scale_factor:
            self.y += self.speed if self.y < self.target_y else -self.speed
            self.y = min(max(self.y, self.target_y - self.speed), self.target_y + self.speed)

    def collides(self, x, y):
        grid_x = int(x // (TILE_SIZE * scale_factor))
        grid_y = int(y // (TILE_SIZE * scale_factor))
        if 0 <= grid_x < len(maze[0]) and 0 <= grid_y < len(maze):
            return maze[grid_y][grid_x] == 1
        return True

    def draw(self):
        ctx.beginPath()
        ctx.arc(self.x, self.y, self.radius, 0, 2 * math.pi)
        ctx.fillStyle = "rgb" + str(self.color)
        ctx.fill()
        ctx.closePath()

def get_random_spawn(exclude_positions, min_distance=100):
    while True:
        grid_x = random.randint(2, len(maze[0]) - 3)
        grid_y = random.randint(2, len(maze) - 3)
        x = grid_x * TILE_SIZE * scale_factor + (TILE_SIZE * scale_factor) // 2
        y = grid_y * TILE_SIZE * scale_factor + (TILE_SIZE * scale_factor) // 2
        if (maze[grid_y][grid_x] == 0 and 
            all(math.hypot(x - pos[0], y - pos[1]) > min_distance * scale_factor for pos in exclude_positions)):
            return x, y

def reset_game():
    global player, ghosts, dots, game_over, score, ready_timer, high_score
    ghost_spawns = [
        (11 * TILE_SIZE * scale_factor + (TILE_SIZE * scale_factor) // 2, 5 * TILE_SIZE * scale_factor + (TILE_SIZE * scale_factor) // 2),
        (13 * TILE_SIZE * scale_factor + (TILE_SIZE * scale_factor) // 2, 5 * TILE_SIZE * scale_factor + (TILE_SIZE * scale_factor) // 2),
        (11 * TILE_SIZE * scale_factor + (TILE_SIZE * scale_factor) // 2, 6 * TILE_SIZE * scale_factor + (TILE_SIZE * scale_factor) // 2),
        (13 * TILE_SIZE * scale_factor + (TILE_SIZE * scale_factor) // 2, 6 * TILE_SIZE * scale_factor + (TILE_SIZE * scale_factor) // 2),
    ]
    ghosts[:] = [Ghost(spawn_x, spawn_y, color) for (spawn_x, spawn_y), color in zip(ghost_spawns, [RED, RED, RED, RED])]
    ghost_positions = [(g.x, g.y) for g in ghosts]
    player_x, player_y = get_random_spawn(ghost_positions)
    player = Player(player_x, player_y)
    dots[:] = [(x * TILE_SIZE * scale_factor + (TILE_SIZE * scale_factor) // 2, 
                y * TILE_SIZE * scale_factor + (TILE_SIZE * scale_factor) // 2) 
               for y in range(len(maze)) for x in range(len(maze[0])) if maze[y][x] == 0]
    game_over = False
    score = 0
    ready_timer = 60

player = Player(0, 0)
ghosts = []
dots = []

# Input handling (Keyboard only)
keys = {"left": False, "right": False, "up": False, "down": False}
def keydown(evt):
    evt.preventDefault()
    if evt.keyCode == 37:  # Left arrow
        keys["left"] = True
    elif evt.keyCode == 39:  # Right arrow
        keys["right"] = True
    elif evt.keyCode == 38:  # Up arrow
        keys["up"] = True
    elif evt.keyCode == 40:  # Down arrow
        keys["down"] = True

def keyup(evt):
    evt.preventDefault()
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
    ctx.clearRect(0, 0, WIDTH, HEIGHT)
    ctx.fillStyle = "rgb" + str(BLACK)
    ctx.fillRect(0, 0, WIDTH, HEIGHT)
    for y in range(len(maze)):
        for x in range(len(maze[0])):
            if maze[y][x] == 1:
                ctx.fillStyle = "rgb" + str(BLUE)
                ctx.fillRect(x * TILE_SIZE * scale_factor, y * TILE_SIZE * scale_factor, 
                            TILE_SIZE * scale_factor, TILE_SIZE * scale_factor)
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
        else:
            i += 1

    for ghost in ghosts:
        if math.hypot(player.x - ghost.x, player.y - ghost.y) < player.radius + ghost.radius:
            game_over = True
            break

    player.draw()
    for ghost in ghosts:
        ghost.draw()

    ctx.font = str(int(24 * scale_factor)) + "px Comic Sans MS"
    ctx.fillStyle = "rgb" + str(YELLOW_TEXT)
    ctx.fillText("Score: " + str(score).zfill(3), 10 * scale_factor, 27 * scale_factor)
    ctx.fillText("High: " + str(high_score).zfill(3), 680 * scale_factor, 27 * scale_factor)

    if ready_timer > 0:
        ctx.font = str(int(48 * scale_factor)) + "px Comic Sans MS"
        ctx.fillText("Ready!", WIDTH // 2 - 60 * scale_factor, HEIGHT // 2)

    if game_over:
        ctx.font = str(int(48 * scale_factor)) + "px Comic Sans MS"
        ctx.fillStyle = "rgb" + str(WHITE)
        ctx.fillText("GAME OVER", WIDTH // 2 - 120 * scale_factor, HEIGHT // 2)
        ctx.fillText("Press R to Restart", WIDTH // 2 - 180 * scale_factor, HEIGHT // 2 + 60 * scale_factor)

reset_game()
timer.set_interval(game_loop, 16)  # ~60 FPS