"""
    3D Game
"""
################ 3D Game ######################################################
import pygame
import math
################ Configuration ################################################
pygame.init()

BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
PURPLE = (128,0,255)
WHITE = (255,255,255)

SCREEN_WIDTH = 450
SCREEN_HEIGHT = 300
CENTER = (SCREEN_WIDTH//2,SCREEN_HEIGHT//2)
SCREEN = pygame.display.set_mode((SCREEN_WIDTH*2 + 30,SCREEN_HEIGHT + 100))
CLOCK = pygame.time.Clock()

VIEW_SURFACE = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
VIEW_RECT = pygame.Rect(10,50,SCREEN_WIDTH,SCREEN_HEIGHT)

PROJECTION_SURFACE = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
PROJECTION_RECT = pygame.Rect(SCREEN_WIDTH + 20,50,SCREEN_WIDTH,SCREEN_HEIGHT)

font_name = pygame.font.match_font('arial')
################ Helper Functions #############################################

def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def round_vector(point):
    return (int(point[0]),int(point[1]))

def translate(point,translation):
    (x,y) = point
    (dx,dy) = translation
    return (x + dx,y + dy)

def rotate_point(point,angle):
    (x,y) = point
    theta = math.radians(angle)
    rotated_x = x*math.cos(theta) + y*math.sin(theta)
    rotated_y = -x*math.sin(theta) + y*math.cos(theta)
    return (rotated_x,rotated_y)

def clip_line(line_a,line_b):
    ((x1,y1),(x2,y2)) = line_a
    ((x3,y3),(x4,y4)) = line_b

    num_a = (x1*y2 - y1*x2)
    num_b = (x3*y4 - y3*x4)
    den = (x1 - x2)*(y3 - y4) - (y1 - y2)*(x3 - x4)
    x = (num_a*(x3 - x4) - (x1 - x2)*num_b)/den
    y = (num_a*(y3 - y4) - (y1 - y2)*num_b)/den
    return (x,y)

def scale(point,factor_x,factor_y=None):
    if factor_y==None:
        factor_y = factor_x
    (x,y) = point
    return (x*factor_x,y*factor_y)

def dot_product(u,v):
    (u1,u2) = u
    (v1,v2) = v
    return u1*v1 + u2*v2

def importData(filename):
    #read file
    with open(filename,'r') as f:
        line = f.readline()
        while line:
            start = line.find('(')+1
            end = line.find(')')
            tag = line[0:start-1]
            if line[0]=='s':
                #sector
                # s(x,y,width,height,n,e,s,w)
                line = line[start:end].replace('\n','').split(',')
                l = [float(item) for item in line]
                pos = (32*l[0],32*(50-l[1]))
                size = (32*l[2],32*l[3])
                sides = (int(l[4]),int(l[5]),int(l[6]),int(l[7]))
                s = Sector(pos,size,sides)
                SECTORS.append(s)
                s.tag = tag
            elif line[0]=='p':
                #player
                # p(x,y,direction)
                line = line[start:end].replace('\n','').split(',')
                l = [float(item) for item in line]
                player = Player(32*l[0],32*(50-l[1]),l[2])
            line = f.readline()
    #find how sectors connect
    for obj in SECTORS:
        A = obj.pos_a
        B = obj.pos_b
        C = obj.pos_c
        D = obj.pos_d
        for obj2 in SECTORS:
            hasA = False
            hasB = False
            hasC = False
            hasD = False
            if obj==obj2:
                continue
            corners = obj2.getCorners()
            #do any corners match?
            for corner in corners:
                if A[0] == corner[0] and A[1] == corner[1]:
                    hasA = True
                    continue
                elif B[0] == corner[0] and B[1] == corner[1]:
                    hasB = True
                    continue
                elif C[0] == corner[0] and C[1] == corner[1]:
                    hasC = True
                    continue
                elif D[0] == corner[0] and D[1] == corner[1]:
                    hasD = True
                    continue
            if hasA and hasB:
                obj.connects_ab = obj2
                #print(f"{obj.tag} connects to {obj2.tag}")
                continue
            elif hasB and hasC:
                obj.connects_bc = obj2
                #print(f"{obj.tag} connects to {obj2.tag}")
                continue
            elif hasC and hasD:
                obj.connects_cd = obj2
                #print(f"{obj.tag} connects to {obj2.tag}")
                continue
            elif hasD and hasA:
                obj.connects_da = obj2
                #print(f"{obj.tag} connects to {obj2.tag}")
                continue
    return player

################ Classes ######################################################

class Player:
    def __init__(self,x,y,direction):
        self.radius = 16
        self.position = (x,y)
        self.direction = direction
        self.speed = 2
        self.camera_z = 30
        self.near_plane = ((-32,0),(32,0))
        self.energy = 0
        self.sector = None
        self.recalculateSector()

        self.original_image = pygame.Surface((32,32))
        pygame.draw.circle(self.original_image,RED,(16,16),self.radius)
        pygame.draw.line(self.original_image,BLACK,(16,16),(32,16))

    def recalculateSector(self):
        for s in SECTORS:
            if s.inSector(self.position):
                self.sector = s
                break
        #print(f"player is in {self.sector.tag}")

    def update(self):
        #take inputs
        keystate = pygame.key.get_pressed()

        if keystate[pygame.K_LEFT]:
            self.direction += 2
            if self.direction > 360:
                self.direction -= 360

        if keystate[pygame.K_RIGHT]:
            self.direction -= 2
            if self.direction < 0:
                self.direction += 360

        if keystate[pygame.K_UP]:
            dx =  self.speed*math.cos(math.radians(self.direction))
            dy = -self.speed*math.sin(math.radians(self.direction))
            self.move(dx,dy)

        if keystate[pygame.K_DOWN]:
            dx = -self.speed*math.cos(math.radians(self.direction))
            dy =  self.speed*math.sin(math.radians(self.direction))
            self.move(dx,dy)

        if keystate[pygame.K_SPACE] and self.camera_z==30:
            self.energy = 20

        self.camera_z += self.energy
        self.energy -= 1
        if self.camera_z <= 30:
            self.energy = 0
            self.camera_z = 30

        #apply transformations
        self.world_to_view_transform()

    def move(self,dx,dy):
        #check movement in x and y direction separately
        temp = [0,0]

        check = (self.radius*dx,0)
        could_move_to = translate(self.position,check)
        if not self.sector.hitWall(could_move_to):
            temp[0] = dx

        check = (0,self.radius*dy)
        could_move_to = translate(self.position,check)
        if not self.sector.hitWall(could_move_to):
            temp[1] = dy

        self.position = translate(self.position,temp)
        self.sector = self.sector.newSector(self.position)

    def world_to_view_transform(self):
        #apply world to view coordinate transformation
        #rotate then transate
        rotated_image = pygame.transform.rotate(self.original_image, 90)
        rotated_rect = rotated_image.get_rect()
        rotated_rect.center = CENTER
        #blit to view
        VIEW_SURFACE.blit(rotated_image,rotated_rect)
        #draw the near plane
        pygame.draw.line(VIEW_SURFACE,WHITE,translate(self.near_plane[0],CENTER),translate(self.near_plane[1],CENTER))

class Wall:
    def __init__(self,pos_a,pos_b):
        self.pos_a = pos_a
        self.pos_b = pos_b
        self.colour = GREEN
        self.z = 0
        self.height = 80

        #calculate normal
        dx = self.pos_b[0]-self.pos_a[0]
        dy = self.pos_b[1]-self.pos_a[1]
        if dx==0:
            #vertical wall
            self.normal = (dy/abs(dy),0)
        else:
            #horizontal wall
            self.normal = (0,-dx/abs(dx))

    def update(self):
        #backface test
        dx = player.position[0] - self.pos_a[0]
        dy = player.position[1] - self.pos_a[1]
        dir_to_cam = (dx,dy)

        if dot_product(dir_to_cam,self.normal)>0:
            self.world_to_view_transform()
            self.view_to_projection_transform()

    def world_to_view_transform(self):
        #find position relative to camera
        cam = (-player.position[0],-player.position[1])
        self.pos_a_view = translate(self.pos_a,cam)
        self.pos_b_view = translate(self.pos_b,cam)
        #rotate 90 degrees counter clockwise, then opposite camera motion
        opposite_cam = 90-player.direction
        self.pos_a_view = rotate_point(self.pos_a_view,opposite_cam)
        self.pos_b_view = rotate_point(self.pos_b_view,opposite_cam)
        """
        #get normal line to graph
        norm_start = ((self.pos_a_view[0]+self.pos_b_view[0])//2,(self.pos_a_view[1]+self.pos_b_view[1])//2)
        norm_start = translate(norm_start,CENTER)
        norm_components = rotate_point(scale(self.normal,10),opposite_cam)
        norm_end = translate(norm_start,norm_components)
        
        pygame.draw.line(VIEW_SURFACE,self.colour,
                            round_vector(translate(self.pos_a_view,CENTER)),
                            round_vector(translate(self.pos_b_view,CENTER)))
        pygame.draw.line(VIEW_SURFACE,self.colour,norm_start,norm_end)
        """

    def view_to_projection_transform(self):
        #Projection transformation
        #fetch the top-down coordinates
        (x_a,depth_a) = self.pos_a_view
        (x_b,depth_b) = self.pos_b_view

        if depth_a >= 0 and depth_b >= 0:
            return

        if depth_a >= 0:
            (x_a,depth_a) = clip_line(
                                        ((x_a,depth_a),(x_b,depth_b)),
                                        player.near_plane
                                    )

        if depth_b >= 0:
            (x_b,depth_b) = clip_line(
                                        ((x_a,depth_a),(x_b,depth_b)),
                                        player.near_plane
                                    )

        depth_a *= -1
        depth_a = max(depth_a,0.01)
        x_a = self.pos_a_view[0]/depth_a
        top_a = -(self.z+self.height-player.camera_z)/depth_a
        bottom_a = -(self.z-player.camera_z)/depth_a

        depth_b *= -1
        depth_b = max(depth_b,0.01)
        x_b = self.pos_b_view[0]/depth_b
        top_b = -(self.z+self.height-player.camera_z)/depth_b
        bottom_b = -(self.z-player.camera_z)/depth_b

        points = [
                    (x_a,top_a),
                    (x_b,top_b),
                    (x_b,bottom_b),
                    (x_a,bottom_a)
                ]

        for i in range(len(points)):
            points[i] = scale(points[i],SCREEN_WIDTH//2,SCREEN_HEIGHT//2)
            points[i] = translate(points[i],CENTER)

        pygame.draw.polygon(PROJECTION_SURFACE, self.colour, points,1)

    def getLine(self):
        return (self.pos_a,self.pos_b)

class Sector:
    def __init__(self,pos,size,sides):
        self.position = pos
        self.size = size
        self.colour = GREEN
        self.sides = sides
        self.tag = ""

        self.pos_a = self.position
        self.pos_b = (self.position[0],self.position[1]+self.size[1])
        self.pos_c = (self.position[0]+self.size[0],self.position[1]+self.size[1])
        self.pos_d = (self.position[0]+self.size[0],self.position[1])

        #meta-data
        self.walls = []
        self.connects_ab = None
        self.connects_bc = None
        self.connects_cd = None
        self.connects_da = None
        #construct walls
        if sides[0]:
            #north
            self.walls.append(Wall(self.pos_d,self.pos_a))
        if sides[1]:
            #east
            self.walls.append(Wall(self.pos_c,self.pos_d))
        if sides[2]:
            #south
            self.walls.append(Wall(self.pos_b,self.pos_c))
        if sides[3]:
            #west
            self.walls.append(Wall(self.pos_a,self.pos_b))

    def update(self):
        for w in self.walls:
            w.update()
        self.world_to_view_transform()

    def world_to_view_transform(self):
        #find position relative to camera
        cam = (-player.position[0],-player.position[1])
        self.pos_a_view = translate(self.pos_a,cam)
        self.pos_b_view = translate(self.pos_b,cam)
        self.pos_c_view = translate(self.pos_c,cam)
        self.pos_d_view = translate(self.pos_d,cam)
        #rotate 90 degrees counter clockwise, then opposite camera motion
        opposite_cam = 90-player.direction
        self.pos_a_view = rotate_point(self.pos_a_view,opposite_cam)
        self.pos_b_view = rotate_point(self.pos_b_view,opposite_cam)
        self.pos_c_view = rotate_point(self.pos_c_view,opposite_cam)
        self.pos_d_view = rotate_point(self.pos_d_view,opposite_cam)

        points = (
                    round_vector(translate(self.pos_a_view,CENTER)),
                    round_vector(translate(self.pos_b_view,CENTER)),
                    round_vector(translate(self.pos_c_view,CENTER)),
                    round_vector(translate(self.pos_d_view,CENTER))
                )

        if player.sector == self:
            self.colour = RED
        else:
            self.colour = GREEN
        pygame.draw.polygon(VIEW_SURFACE, self.colour, points,1)

    def getCorners(self):
        return (
                    self.pos_a,
                    self.pos_b,
                    self.pos_c,
                    self.pos_d
                )

    def inSector(self,pos):
        if pos[0] < self.pos_a[0]:
            return False
        if pos[0] > self.pos_c[0]:
            return False
        if pos[1] < self.pos_a[1]:
            return False
        if pos[1] > self.pos_c[1]:
            return False
        return True

    def newSector(self,pos):
        #west
        if pos[0] < self.pos_a[0]:
            return self.connects_ab
        #east
        if pos[0] > self.pos_c[0]:
            return self.connects_cd
        #north
        if pos[1] < self.pos_a[1]:
            return self.connects_da
        #south
        if pos[1] > self.pos_c[1]:
            return self.connects_bc
        return self

    def hitWall(self,pos):
        #west
        if pos[0] < self.pos_a[0] and self.sides[3]:
            return True
        #east
        if pos[0] > self.pos_c[0] and self.sides[1]:
            return True
        #north
        if pos[1] < self.pos_a[1] and self.sides[0]:
            return True
        #south
        if pos[1] > self.pos_c[1] and self.sides[2]:
            return True
        return False

################ Game Objects #################################################
SECTORS = []
player = importData('level2.txt')
################ Game Loop ####################################################
running = True
while running:
    ################ Reset Surfaces ###########################################
    VIEW_SURFACE.fill(BLACK)
    PROJECTION_SURFACE.fill(BLACK)
    SCREEN.fill(BLACK)
    ################ Handle Events ############################################
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running = False
    ################ Update ###################################################
    for s in SECTORS:
        s.update()
    player.update()
    ################ Render ###################################################
    SCREEN.blit(VIEW_SURFACE,VIEW_RECT)
    SCREEN.blit(PROJECTION_SURFACE,PROJECTION_RECT)

    pygame.draw.rect(SCREEN,WHITE,VIEW_RECT,1)
    draw_text(SCREEN,"View Coordinates",16,60,20)
    pygame.draw.rect(SCREEN,WHITE,PROJECTION_RECT,1)
    draw_text(SCREEN,"Projection Coordinates",16,SCREEN_WIDTH+100,20)
    ################ Clock etc ################################################
    CLOCK.tick(60)
    fps = CLOCK.get_fps()
    pygame.display.set_caption("Running at "+str(int(fps))+" fps")
    pygame.display.update()

################ Shutdown #####################################################
pygame.quit()