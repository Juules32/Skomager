
#TO-DO
# 1. Mouse interaction✔
# 1.a how to calculate how far back cue is pulled when mousedown ✔

# 3. Holes
# 4. Rules
# 5. Animation/art



#removes "Hello from the pygame community..." from terminal
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame, sys, os, math, numpy as np
from pygame.locals import *

#Get the absolute path so .exe files work
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
    running_mode = 'Frozen/executable'
else:
    try:
        app_full_path = os.path.realpath(__file__)
        base_path = os.path.dirname(app_full_path)
        running_mode = "Non-interactive (e.g. 'python main.py')"
    except NameError:
        base_path = os.getcwd()
        running_mode = 'Interactive'

print ("{:<20} {:<20}".format('Running mode:', running_mode))
print ("{:<20} {:<20}".format('Application path:', base_path))

#use this when assigning path
def path(relative_path): return os.path.join(base_path, relative_path)

#constants
FRAMERATE: int = 60
SCALE_FACTOR = 3
BALL_SIZE = 5 #standard størrelse er omkring 6 cm i diameter
WHITE = (255, 255, 255)
RED = (150, 0, 0)
CLOTH_COLOR = (80, 160, 80)
TABLE_COLOR = (139,50,29)
RESISTANCE_FACTOR = 0.03
PADDING_WIDTH = 17
TABLE_POS = (50, 50)
CLOTH_POS = (PADDING_WIDTH, PADDING_WIDTH)
CLOTH_SIZE = (300, 300/2)
TABLE_SIZE = (CLOTH_SIZE[0]+2*PADDING_WIDTH, CLOTH_SIZE[1]+2*PADDING_WIDTH)
MAX_SPEED = 15

#initializations
pygame.init()
pygame.display.set_caption("Skomager")
mainClock = pygame.time.Clock()
font = pygame.font.Font('freesansbold.ttf', 32)
window = pygame.display.set_mode((TABLE_SIZE[0]*SCALE_FACTOR + 150, TABLE_SIZE[1]*SCALE_FACTOR + 150), pygame.RESIZABLE)
table = pygame.Surface(TABLE_SIZE)
cloth = pygame.Surface(CLOTH_SIZE)
cue = pygame.transform.flip(pygame.image.load(path('Assets/Billiard-Cue.png')), True, False)

#ball class
class Ball:
    def __init__(self, pos, isRed: bool = False):
        self.x = pos[0]
        self.y = pos[1]
        self.isRed: bool = isRed
        self.color = RED if isRed else WHITE
        self.lastBounceX = self.x
        self.lastBounceY = self.y
        self.v = 0
        self.deg = 0
        
        self.path_rect = None
    
    def get_vx(self):
        return math.cos(self.deg)*self.v
    
    def get_vy(self):
        return math.sin(self.deg)*self.v

    def dist_to(self, ball2):
        return math.sqrt((self.x - ball2.x)**2 + (self.y - ball2.y)**2)
    
    def is_overlapping_with(self, ball2):
        return True if self.dist_to(ball2) < 2*BALL_SIZE else False
    
    def draw(self):
        pygame.draw.circle(table, self.color, (self.x, self.y), BALL_SIZE)

    def animate(self):
        #Halts if speed is below a certain point
        if abs(self.v) < 0.1:
            self.v = 0
        #Otherwise, gradually slows down
        else:
            self.v = self.v - RESISTANCE_FACTOR*math.sqrt(self.v)
        #Increments position by speed
        self.x += self.get_vx()
        self.y += self.get_vy()
        
        #checks wall collision
        if self.x - BALL_SIZE <= CLOTH_POS[0] and self.get_vx() < 0:
            self.deg = self.deg + 2*(1.5*math.pi-self.deg)
            
        elif self.x + BALL_SIZE >= CLOTH_SIZE[0]+PADDING_WIDTH and self.get_vx() > 0:
            self.deg = self.deg - 2*(self.deg - 1.5*math.pi)

            
        if self.y - BALL_SIZE <= CLOTH_POS[1] and self.get_vy() < 0:
            self.deg = self.deg + 2*(1*math.pi-self.deg)

            
        elif self.y + BALL_SIZE >= CLOTH_SIZE[1]+PADDING_WIDTH and self.get_vy() > 0:
            self.deg = self.deg - 2*(self.deg - math.pi)
    
    
    def hits(ball1, ball2):
        #saves original positions in case something goes wrong
        original_ball1_x = ball1.x
        original_ball1_y = ball1.y
        original_ball2_x = ball2.x
        original_ball2_y = ball2.y
        
        #slowly rolls back ball positions to adjust for overlap
        c = 0
        while ball1.is_overlapping_with(ball2):
            ball1.x -= ball1.get_vx()*0.01
            ball1.y -= ball1.get_vy()*0.01
            ball2.x -= ball2.get_vx()*0.01
            ball2.y -= ball2.get_vy()*0.01
            c += 1
            if c >= 1000:
                print("Collision failed!")
                ball1.x = original_ball1_x
                ball1.y = original_ball1_y
                ball2.x = original_ball2_x
                ball2.y = original_ball2_y
                return
            
        #degree between the balls
        deg = math.atan2(ball1.y-ball2.y, ball1.x-ball2.x)
        
        cdeg = math.cos(deg)
        sdeg = math.sin(deg)
        
        #positions stored as numpy arrays
        v1 = np.array([ball1.get_vx(), ball1.get_vy()])
        v2 = np.array([ball2.get_vx(), ball2.get_vy()])
        
        #rotation to apply to find new angle
        rot = np.array([
            [cdeg, sdeg],
            [-sdeg, cdeg]
        ])
        
        #rotated vectors with matrix multiplication
        rv1 = np.dot(rot, v1)
        rv2 = np.dot(rot, v2)
        
        #new directions (not rotated back)
        p1 = np.array([rv2[0], rv1[1]])
        p2 = np.array([rv1[0], rv2[1]])
        
        #rotation to apply to get original angle
        rot_back = np.array([
            [cdeg, -sdeg],
            [sdeg, cdeg]
        ])
        
        #new vectors
        nv1 = np.dot(rot_back, p1)
        nv2 = np.dot(rot_back, p2)

        ball1.v = math.sqrt(nv1[0]**2 + nv1[1]**2)
        ball2.v = math.sqrt(nv2[0]**2 + nv2[1]**2)
        
        ball1.deg = math.atan2(nv1[1], nv1[0])
        ball2.deg = math.atan2(nv2[1], nv2[0])
        
class CueBall(Ball):
    def __init__(self, pos, isRed: bool = False):
        super().__init__(pos, isRed)
        self.potential_speed = 0
        self.shooting_angle = 0
        
    def shoot(self):
        self.v = self.potential_speed
        self.deg = self.shooting_angle
        print("Shot cue ball!")
        
cue_ball = CueBall((100, 100), True)

balls = []
moving_balls = []

#resets the board
def reset():
    global balls, moving_balls
    cue_ball.v = 0
    balls = [cue_ball, Ball([50, 110]), Ball([150, 100])]
    moving_balls = []
    


#updates which balls are moving
def update_moving_balls():
    global moving_balls
    moving_balls = []
    for ball in balls:
        if ball.v:
            moving_balls.append(ball)

def draw_background():
    table.fill(TABLE_COLOR)
    cloth.fill(CLOTH_COLOR)
    table.blit(cloth, CLOTH_POS)

#updates ball positions
def draw_balls():
    
    
    for ball in balls:
        ball.draw()
    
#draw cue and rotate according to mouse position
def draw_cue(mx, my, x_off, y_off):
    deg = math.atan2(-(cue_ball.y-y_off), cue_ball.x-x_off)
    cdeg = math.cos(deg)
    sdeg = math.sin(deg)
    
    dx = mx-x_off
    dy = my-y_off
    
    
    #rotated x value
    rx = cdeg*dx+sdeg*-dy
    
    #limits shooting speed
    if rx > MAX_SPEED*2: rx = MAX_SPEED*2
    if rx < 0: rx = 0
    
    #x and y values rotated back
    rbx = cdeg*rx
    rby = sdeg*rx
    
    cue_ball.potential_speed = rx*0.5
    cue_ball.shooting_angle = -deg + math.pi
    
    cue_copy = pygame.transform.rotate(cue, deg*180/math.pi)
    w, h = cue_copy.get_size()
    length = math.sqrt(cue.get_size()[0]**2 + cue.get_size()[1]**2)
    
    x_offset = (math.cos(deg)*length/2+rbx)
    y_offset = (math.sin(deg)*length/2+rby)
    
    table.blit(cue_copy, ((cue_ball.x - w/2) + x_offset, (cue_ball.y - h/2) - y_offset))

reset()
shooting = False

#game loop
while True:
    #updates mouse coordinates
    mx = (pygame.mouse.get_pos()[0]-TABLE_POS[0])/SCALE_FACTOR
    my = (pygame.mouse.get_pos()[1]-TABLE_POS[1])/SCALE_FACTOR
    
    
    if not shooting:
        x_off = mx
        y_off = my
    
    #event handling
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_r:
                reset()
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            x_off = mx
            y_off = my
            shooting = True
        if event.type == pygame.MOUSEBUTTONUP:
            shooting = False
            if cue_ball.potential_speed > 0:
                cue_ball.shoot()
    
    #physics
    for ball1 in moving_balls:
        ball1.animate()
        for ball2 in balls:
            if ball1 is not ball2 and ball1.is_overlapping_with(ball2):
                ball1.hits(ball2)
    update_moving_balls()
    
    #visuals
    draw_background()
    draw_balls()
    if not moving_balls:
        draw_cue(mx, my, x_off, y_off)
    
        
    window.fill((0, 50, 0))
    window.blit(pygame.transform.scale_by(table, SCALE_FACTOR), TABLE_POS)
    text = font.render(f"{mx}, {my}", True, (0,0,100))
    window.blit(text, (0, 0))
    pygame.display.update()
    mainClock.tick(FRAMERATE)