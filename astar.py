import pygame
import math 
from queue import PriorityQueue

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH,WIDTH))
pygame.display.set_caption("A* Path Finding Algorithm")
pygame.font.init()

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows
    
    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == RED
    
    def is_open(self):
        return self.color == GREEN
    
    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE
    
    def is_end(self):
        return self.color == TURQUOISE
    
    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = ORANGE
    
    def make_closed(self):
        self.color = RED
    
    def make_open(self):
        self.color = GREEN
    
    def make_barrier(self):
        self.color = BLACK
    
    def make_end(self):
        self.color = TURQUOISE
    
    def make_path(self):
        self.color = PURPLE
    
    def draw(self,win):
        pygame.draw.rect(win,self.color,(self.x, self.y, self.width, self.width))

    def update_neighbors(self,grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): #Down
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): #Up
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): #Left
            self.neighbors.append(grid[self.row][self.col - 1])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): #Right
            self.neighbors.append(grid[self.row][self.col + 1])


    def __lt__(self, other):
        return False

class button():
    def __init__(self, color, x, y, width, height, text=''):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self,win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 0)

        if self.text != '':
            font = pygame.font.SysFont('times', 20)
            text = font.render(self.text, 1, (0,0,0))
            win.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))

    def mouseHover(self, pos):
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
        return False

# L-distance calculation
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

# Euclid distance calculation
def euclid(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    

# rebuilds the shortest path after algorithm
def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()

# a star distance finding algorithm
def a_star_algorithm(draw, grid, start, end, show_draw, distance):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {} # Keeps track of previous nodes
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0 
    f_score = {node: float("inf") for row in grid for node in row}
    if distance:
        f_score[start] = euclid(start.get_pos(), end.get_pos()) #euclid distance
    else:
        f_score[start] = h(start.get_pos(), end.get_pos()) #L-distance value
    

    open_set_hash = {start} # back up data storage

    while not open_set.empty():
        # Escape function
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        current = open_set.get()[2]
        open_set_hash.remove(current)

        # end the loop when the current tile is equal to cordinate position of the end tile
        if current == end:
             reconstruct_path(came_from, end, draw)
             end.make_end()
             start.make_start()
             return True
        # Determiens neighbor scores
        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()
        # draw the algorithm in real-time if people want to see it
        if show_draw == True:   
            draw()

        if current != start:
            current.make_closed()

    draw()
    return False

# creates the  visual grid
def make_grid(rows,width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    return grid

# Draws a grid pattern
def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, ( j * gap, 0 ), (j * gap, width))

def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for node in row:
            node.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()

def drawMenu(win):
    win.fill(WHITE)
    font = pygame.font.SysFont('times', 20)
    text = font.render('Press space bar to start and c to go back to menu',1, (0,0,0))
    textRect = text.get_rect()
    textRect.center = (400,200)
    win.blit(text, textRect)
    euclidButton.draw(win)
    lButton.draw(win)
    astarButton.draw(win)
    otherButton.draw(win)
    startButton.draw(win)
    
    

# returns which square was clicked
def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y,x = pos

    row = y // gap
    col = x // gap

    return row, col

startButton = button(TURQUOISE, 275, 600, 250, 100, 'Start')
euclidButton = button(BLUE, 100, 300, 250, 100, 'Euclidian Distance')
lButton = button(BLUE, 450, 300, 250, 100, 'L-Distance')
astarButton = button(BLUE, 100, 450, 250, 100, 'A* Distance algorithm')
otherButton = button(BLUE, 450, 450, 250, 100, 'Other Distance Algorithm')

def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)

    start = None
    end = None

    euclid = False
    aStar = True
    show_draw = False

    menu = True
    run = False
    started = False 

    

    while menu:
        drawMenu(win)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu = False
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()

                if startButton.mouseHover(pos):
                    menu = False
                    run = True
                    euclidButton.color = BLUE
                    lButton.color = BLUE
                    astarButton.color = BLUE
                    otherButton.color = BLUE
                elif euclidButton.mouseHover(pos):
                    euclid = True
                    euclidButton.color = RED
                    lButton.color = BLUE
                elif lButton.mouseHover(pos):
                    euclid = False
                    lButton.color = RED
                    euclidButton.color = BLUE
                elif astarButton.mouseHover(pos):
                    aStar = True
                    astarButton.color = RED
                    otherButton.color = BLUE
                elif otherButton.mouseHover(pos):
                    aStar = False
                    otherButton.color = RED
                    astarButton.color = BLUE
    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if started:
                continue

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                if not start and node != end:
                    start = node
                    start.make_start()
                    
                    
                elif not end and node != start:
                    end = node
                    end.make_end()
                    
                
                elif node != end and node != start:
                    node.make_barrier()
                   
                
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                node.reset()
                if node == start:
                    start = None
                elif node == end:
                    end = None

            if event.type == pygame.KEYDOWN:
    
                if event.key == pygame.K_n:
                    show_draw = True
                if event.key == pygame.K_SPACE and not started:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)         
                    
                    a_star_algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end, show_draw, euclid)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    euclid = False
                    aStar = True
                    show_draw = False
                    menu = True
                    run = False
                    main(WIN, WIDTH)
                    
        
    pygame.quit()

main(WIN, WIDTH)