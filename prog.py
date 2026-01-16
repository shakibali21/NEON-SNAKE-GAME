import pygame, random, math

# ------------------ INIT ------------------
pygame.init()

# ------------------ SETTINGS ------------------
WIDTH, HEIGHT = 800, 500
BLOCK = 25                  # Larger blocks = Easier to see/hit
FPS = 60                    # Keep high FPS for smooth particles/glow
INITIAL_MOVE_DELAY = 150    # Milliseconds between moves (Higher = Slower)
LEVEL_UP_EVERY = 5
# ------------------ COLORS ------------------
WHITE = (255, 255, 255)
RED = (255, 45, 85)         # Neon Red
BG_TOP = (10, 10, 30)
BG_BOTTOM = (2, 2, 10)
EYE_WHITE = (230, 230, 230)
EYE_BLACK = (0, 0, 0)

# ------------------ SKINS ------------------
SKINS = [
    {"body": (20,110,60), "head": (10,80,40), "border": (0,50,25), "glow": (0,255,120), "name": "Venom Green"},
    {"body": (0,150,200), "head": (0,100,150), "border": (0,60,100), "glow": (0,255,255), "name": "Cyber Blue"},
    {"body": (200,50,50), "head": (150,0,0), "border": (100,0,0), "glow": (255,100,100), "name": "Magma Red"},
]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Snake: Smooth & Easy")
clock = pygame.time.Clock()
font = pygame.font.SysFont("calibri", 24, bold=True)
title_font = pygame.font.SysFont("calibri", 50, bold=True)

# ------------------ PARTICLES ------------------
class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.dx = random.uniform(-2, 2)
        self.dy = random.uniform(-2, 2)
        self.life = 255
        self.color = color

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 5  # Slow fade out

    def draw(self, surf):
        if self.life > 0:
            # Draw with alpha transparency
            s = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, self.life), (2, 2), 2)
            surf.blit(s, (int(self.x), int(self.y)))

# ------------------ VISUALS ------------------
def draw_bg():
    """Draws the deep space gradient."""
    for y in range(0, HEIGHT, 2): # Skip pixels for performance
        t = y/HEIGHT
        r = int(BG_TOP[0]+(BG_BOTTOM[0]-BG_TOP[0])*t)
        g = int(BG_TOP[1]+(BG_BOTTOM[1]-BG_TOP[1])*t)
        b = int(BG_TOP[2]+(BG_BOTTOM[2]-BG_TOP[2])*t)
        pygame.draw.line(screen, (r,g,b), (0,y), (WIDTH,y))

def glass_panel(x, y, w, h):
    """Modern transparent UI."""
    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(panel, (255, 255, 255, 20), (0, 0, w, h), border_radius=12)
    pygame.draw.rect(panel, (255, 255, 255, 60), (0, 0, w, h), 1, border_radius=12)
    screen.blit(panel, (x, y))

def draw_snake(snake, dx, dy, tick, skin, visual_x, visual_y):
    """
    Draws the snake using your specific icon style.
    visual_x/y are the smooth LERP coordinates for the head.
    """
    for i, (gx, gy) in enumerate(snake):
        # Determine render position
        # If it's the head, use the smooth visual coordinates
        if i == len(snake) - 1:
            rx, ry = visual_x, visual_y
        else:
            rx, ry = gx, gy

        # Shadow
        pygame.draw.ellipse(screen, (0, 0, 0, 80), (rx + 4, ry + BLOCK - 4, BLOCK - 8, 6))

        if i == len(snake) - 1: # HEAD
            # 1. Glow Aura (Pulse)
            pulse = math.sin(tick * 0.1) * 4
            glow_surf = pygame.Surface((BLOCK+30, BLOCK+30), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*skin["glow"], 40), (BLOCK//2+15, BLOCK//2+15), BLOCK//2 + 8 + pulse)
            screen.blit(glow_surf, (rx-15, ry-15))

            # 2. Main Head Shape
            pygame.draw.rect(screen, skin["head"], (rx, ry, BLOCK, BLOCK), border_radius=8)
            
            # 3. Eyes (Direction Aware)
            eye_radius = 4
            pupil_radius = 2
            # Default positions
            left_eye = (rx + 6, ry + 6)
            right_eye = (rx + BLOCK - 6, ry + 6)
            
            if dx > 0: # Right
                left_eye, right_eye = (rx + BLOCK - 8, ry + 6), (rx + BLOCK - 8, ry + BLOCK - 6)
            elif dx < 0: # Left
                left_eye, right_eye = (rx + 8, ry + 6), (rx + 8, ry + BLOCK - 6)
            elif dy > 0: # Down
                left_eye, right_eye = (rx + 6, ry + BLOCK - 8), (rx + BLOCK - 6, ry + BLOCK - 8)
            elif dy < 0: # Up
                left_eye, right_eye = (rx + 6, ry + 8), (rx + BLOCK - 6, ry + 8)

            pygame.draw.circle(screen, EYE_WHITE, left_eye, eye_radius)
            pygame.draw.circle(screen, EYE_BLACK, left_eye, pupil_radius)
            pygame.draw.circle(screen, EYE_WHITE, right_eye, eye_radius)
            pygame.draw.circle(screen, EYE_BLACK, right_eye, pupil_radius)

            # 4. Flickering Tongue
            if tick % 40 < 15:
                tongue_start = (rx + BLOCK // 2, ry + BLOCK // 2)
                tongue_end = tongue_start
                if dx > 0: tongue_end = (rx + BLOCK + 5, ry + BLOCK // 2)
                elif dx < 0: tongue_end = (rx - 5, ry + BLOCK // 2)
                elif dy > 0: tongue_end = (rx + BLOCK // 2, ry + BLOCK + 5)
                elif dy < 0: tongue_end = (rx + BLOCK // 2, ry - 5)
                pygame.draw.line(screen, RED, tongue_start, tongue_end, 2)

        else:
            # BODY segments
            pygame.draw.rect(screen, skin["body"], (rx, ry, BLOCK, BLOCK), border_radius=5)
            pygame.draw.rect(screen, skin["border"], (rx, ry, BLOCK, BLOCK), 1, border_radius=5)

# ------------------ GAME LOOP ------------------
def game(skin):
    # Logical Grid Position
    grid_x = (WIDTH // 2 // BLOCK) * BLOCK
    grid_y = (HEIGHT // 2 // BLOCK) * BLOCK
    
    # Visual Position (for smoothness)
    visual_x, visual_y = grid_x, grid_y
    
    dx, dy = BLOCK, 0
    next_dx, next_dy = BLOCK, 0 # Input buffer
    
    snake = [[grid_x, grid_y], [grid_x-BLOCK, grid_y], [grid_x-BLOCK*2, grid_y]] # Start with body
    snake.reverse() # Head is last
    
    score = 0
    level = 1
    move_delay = INITIAL_MOVE_DELAY
    last_move_time = pygame.time.get_ticks()
    
    food = [random.randrange(BLOCK, WIDTH-BLOCK, BLOCK), random.randrange(BLOCK, HEIGHT-BLOCK, BLOCK)]
    particles = []
    tick = 0
    shake = 0
    
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        dt = clock.tick(FPS) # Keeps loop running at 60 FPS
        tick += 1

        # 1. INPUT HANDLING (Buffered)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_LEFT and dx == 0: next_dx, next_dy = -BLOCK, 0
                elif e.key == pygame.K_RIGHT and dx == 0: next_dx, next_dy = BLOCK, 0
                elif e.key == pygame.K_UP and dy == 0: next_dx, next_dy = 0, -BLOCK
                elif e.key == pygame.K_DOWN and dy == 0: next_dx, next_dy = 0, BLOCK

        # 2. LOGIC UPDATE (Gated by Time)
        if current_time - last_move_time > move_delay:
            # Apply buffered input
            dx, dy = next_dx, next_dy
            
            # Move Logic Grid
            grid_x += dx
            grid_y += dy
            
            # Wall Collision
            if grid_x < 0 or grid_x >= WIDTH or grid_y < 0 or grid_y >= HEIGHT:
                running = False
            
            # Self Collision
            if [grid_x, grid_y] in snake:
                running = False
            
            snake.append([grid_x, grid_y])
            
            # Eat Food
            if grid_x == food[0] and grid_y == food[1]:
                score += 1
                shake = 10 # Screen shake effect
                food = [random.randrange(BLOCK, WIDTH-BLOCK, BLOCK), random.randrange(BLOCK, HEIGHT-BLOCK, BLOCK)]
                
                # Burst particles
                for _ in range(12): 
                    particles.append(Particle(grid_x + BLOCK//2, grid_y + BLOCK//2, skin["glow"]))
                
                # Level Up (Make it slightly faster, but still manageable)
                if score % LEVEL_UP_EVERY == 0:
                    level += 1
                    move_delay = max(50, move_delay - 10) # Don't get faster than 50ms
            else:
                snake.pop(0) # Remove tail if didn't eat
            
            last_move_time = current_time

        # 3. VISUAL INTERPOLATION (LERP)
        # Smoothly slide visual head towards logical grid head
        # Factor 0.2 gives it a nice weight without being sluggish
        visual_x += (grid_x - visual_x) * 0.2
        visual_y += (grid_y - visual_y) * 0.2

        # 4. RENDER
        
        # Screen Shake Logic
        render_offset = (0,0)
        if shake > 0:
            shake -= 1
            render_offset = (random.randint(-4, 4), random.randint(-4, 4))
        
        # Draw to a temp surface if shaking, otherwise direct
        screen.fill(BG_BOTTOM)
        draw_bg()
        
        if shake > 0:
            temp_surf = screen.copy()
            screen.blit(temp_surf, render_offset)

        # Draw Particles
        for p in particles[:]:
            p.update()
            p.draw(screen)
            if p.life <= 0: particles.remove(p)

        # Draw Food (Breathing effect)
        pulse = math.sin(tick * 0.05) * 3
        food_rect = (food[0] - pulse, food[1] - pulse, BLOCK + pulse*2, BLOCK + pulse*2)
        pygame.draw.rect(screen, RED, food_rect, border_radius=8)
        
        # Draw Snake
        draw_snake(snake, dx, dy, tick, skin, visual_x, visual_y)

        # Draw HUD
        glass_panel(20, 20, 250, 50)
        score_text = font.render(f"SCORE: {score}  LVL: {level}", True, WHITE)
        screen.blit(score_text, (35, 32))

        pygame.display.flip()

def main_menu():
    idx = 0
    while True:
        draw_bg()
        title = title_font.render("NEON SNAKE", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))
        
        glass_panel(WIDTH//2 - 150, 220, 300, 160)
        
        skin_name = font.render(f"< {SKINS[idx]['name']} >", True, SKINS[idx]["glow"])
        screen.blit(skin_name, (WIDTH//2 - skin_name.get_width()//2, 260))
        
        start_txt = font.render("PRESS ENTER", True, WHITE)
        screen.blit(start_txt, (WIDTH//2 - start_txt.get_width()//2, 320))

        pygame.display.flip()
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); return
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN: game(SKINS[idx])
                if e.key == pygame.K_RIGHT: idx = (idx + 1) % len(SKINS)
                if e.key == pygame.K_LEFT: idx = (idx - 1) % len(SKINS)

if __name__ == "__main__":
    main_menu()