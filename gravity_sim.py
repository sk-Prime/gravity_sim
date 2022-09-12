import pygame
import math
from random import randint

pygame.init()

class Config:
    def __init__(self):
        self.screen_w=720
        self.screen_h = 1440
        
        self.fps = 200
        self.bg = (20,30,40)
        
        self.G = 5 * 10**-4 #gravitional constant in this simulation
        
        
        self.font_size=15
        self.button_bg =(255,255,255)
        self.button_w = 80
        self.button_h = 50
        self.button_y = 1300 #buttons position.
        self.button_space = 10
        self.button_border = 1
        #randomly generated sun and planet size will be within this pixel range
        self.star_size_range = (150,200) 
        self.planet_size_range=(25,50)
        
        self.planet_velocity = True
        self.planet_starting_velocity = 1.5 #y direction velocity of a planet
        self.draw_line = False
        
        self.kill = True #kill a sprite if it is outside of
        self.kill_distance = 2000 #this range
        self.kill_d_factor=4 #calc kill_distance from given screen size
        
        self.draw_path = False #draw sprites movement path
        self.path_sample_size = 50 #number of sample, length of the path
        self.path_sample_sec = 25 #times in a second
        self.path_color = (255,255,255)
        self.path_color_sprite = True #path color from sprite
        
    def set_screen_info(self,x,y):
        """Calculate parameters using given screen width and height"""
        self.font_size = x//40
        self.screen_w = x
        self.screen_h = y
        
        self.button_w = x//10
        self.button_h = x/14
        self.button_space = x//80
        self.button_y = y-self.button_h-(self.button_h/3)
        
        self.star_size_range = (x//9, x//6)
        self.planet_size_range = (x//35, x//14)
        self.planet_starting_velocity = x/500
        self.kill_distance = (x*self.kill_d_factor + y*self.kill_d_factor)//2
        
conf = Config()

class Sprite:
    def __init__(self):
        self.screen = None
        self.name = None
        self.alive=True
        
        #True = Affect other objects but hold own's position
        self.static = False 
        
        self.sprite = None
        self.size = None
        self.radius = None
        self.mass= None
        
        self.position = 0,0
        self.velocity_x = 0
        self.velocity_y = 0
        self.path_points = []
        self.path_p_n = 0
        
        self.clock = pygame.time.Clock()
        self.t_passed = 0
        self.path_color = conf.path_color
    @classmethod
    def from_circle(cls,screen,a,dense_f=1,pos=(0,0),color=None,name=None):
        if not color: color = [randint(0,255) for _ in range(3)]
        surface = pygame.Surface((a,)*2)
        pygame.draw.circle(surface,color,(a/2,a/2),a/2)
        surface.set_colorkey((0))
        
        temp_cls=cls()
        temp_cls.screen=screen
        temp_cls.sprite=surface
        temp_cls.radius=a/2
        temp_cls.size = a
        #area multiplied by density factor is the mass of a circle
        temp_cls.mass = int(round(math.pi * a**2,0)*dense_f)
        temp_cls.position=pos[0]-a//2,pos[1]-a//2 #center of a given pos
        temp_cls.name = name
        if conf.path_color_sprite:
            temp_cls.path_color = color
        return temp_cls
        
    def set_pos(self,x,y):
        #centering position
        self.position = x - self.size//2,y - self.size//2
        
    def get_center(self):
        #get center from position
        x,y = self.position
        size_half = self.size/2
        return x+size_half,y+size_half
        
    def move(self,sprites,i):
        if self.alive and not self.static:
            px,py = self.position
            #if kill and outside of given kill_distance, making it dead
            if conf.kill and (abs(px)>conf.kill_distance or abs(py)>conf.kill_distance):
                self.alive = False
            x,y = self.get_center() #self center
            for n,sprite in enumerate(sprites):
                if n!=i:
                    #gravitational point is on center of two sprites
                    sx,sy = sprite.get_center()
                    a,b = sx-x,sy-y
                    #distance between two object
                    c = (a**2 + b**2)**.5 
                    #to prevent c becoming zero
                    #better version is simulating rigid body to prevent
                    #pass through another body. 
                    if c>self.radius: #TODO 
                        unit_a, unit_b = a/c, b/c
                        force = ((conf.G * sprite.mass)/c**2) #calculating force
                        #modifying and storing velocity. Storing because it will work as inertia.
                        self.velocity_x+=(force*unit_a)
                        self.velocity_y+=(force*unit_b)
                        #changing postion according to velocity
                        self.position= px+self.velocity_x,py+self.velocity_y
                        if conf.draw_line: #an attempt to convert force into color (red)
                            if n>i or sprite.name=="star":
                                pygame.draw.line(self.screen,(min(0.0019*force**-1,255),0,255),(sx,sy),(x,y))
                        if conf.draw_path:
                            self.t_passed += self.clock.tick()/1000
                            if self.t_passed > 1/conf.path_sample_sec:
                                self.add_path_points((x,y))
                                self.t_passed = 0
                                
    def add_path_points(self,point):
        if self.path_p_n<=conf.path_sample_size:
            self.path_p_n +=1
        if self.path_p_n>conf.path_sample_size:
            self.path_points.pop(0)
        self.path_points.append(point)
        
    def render(self):
        self.screen.blit(self.sprite,self.position)
        if conf.draw_path and self.path_p_n>2:
            pygame.draw.lines(self.screen, self.path_color,0,self.path_points)
        elif not conf.draw_path and self.path_p_n:
            self.path_p_n =0
            self.path_points = []
class Button():
    def __init__(self,screen,size,name):
        self.screen= screen
        self.x,self.y,self.w,self.h = size
        self.name = name
        self.font = pygame.font.SysFont("arial",conf.font_size)
        self.srf = self.make_button()
        
    def make_button(self):
        button_srf = pygame.Surface((self.w,self.h))
        button_srf.set_colorkey((0))
        pygame.draw.rect(button_srf,conf.button_bg,(0,0,self.w,self.h),width=conf.button_border)
        text = self.font.render(self.name,0,conf.button_bg)
        tx,ty = text.get_size()
        text_x = self.w/2 - tx/2
        text_y = self.h/2 - ty/2
        button_srf.blit(text,(text_x,text_y))
        return button_srf
        
    def clicked(self,x,y):
        if self.x<x<self.x+self.w and self.y<y<self.y+self.h:
            return True
        return False
        
    def render(self):
        self.screen.blit(self.srf,(self.x,self.y))
        
class Game():
    def __init__(self,screen):
        self.screen = screen
        self.sprites = [] #all sprites
        #dead sprites need to be deleted  from all sprites
        self.dead_sprites = [] 
        
        self.create = True #create mode or move mode
        self.planet = False #Planet mode or star mode
        self.selected = None #selected sprite in move mode
        self.last_selected = None #to change property(static) or delete
        #last selected static state. Grabing a sprite always make it static
        #After releasing the grab, make the static state as it was before
        #star remain static after grab, planet remain non static after grab
        self.sel_state = None 
        
        self.grab_btn = Button(screen,self.button_pos(0),"Grab")
        self.create_btn = Button(screen,self.button_pos(0),"Create")
        self.star_btn = Button(screen,self.button_pos(1),"Star")
        self.planet_btn = Button(screen,self.button_pos(1),"Planet")    
        self.planet_vel_btn = Button(screen,self.button_pos(2),"vel on")
        self.planet_vel_off_btn = Button(screen,self.button_pos(2),"vel off")
        self.line_btn = Button(screen,self.button_pos(3),"Force")
        self.path_btn = Button(screen,self.button_pos(4),"Path")
        self.static_btn = Button(screen,self.button_pos(5),"Static")
        self.clear_btn = Button(screen,self.button_pos(6),"Clear")
        self.kill_on_btn = Button(screen,self.button_pos(7),"Kill on")
        self.kill_off_btn = Button(screen,self.button_pos(7),"Kill off")
        self.del_btn = Button(screen,self.button_pos(8),"Del")
        
        
        
    def button_pos(self,n):
        return n*(conf.button_w+conf.button_space),conf.button_y,conf.button_w,conf.button_h
        
    def create_star(self):
        r = randint(*conf.star_size_range)
        color = [randint(180,255),randint(0,100),randint(0,100)]
        star = Sprite().from_circle(self.screen,r,dense_f=20,color=color,name="star")
        return star
        
    def create_planet(self):
        r = randint(*conf.planet_size_range)
        color = [randint(0,255),randint(50,255),randint(50,255)]
        planet = Sprite().from_circle(self.screen,r,color=color,name="planet")
        if conf.planet_velocity:
            planet.velocity_y=-conf.planet_starting_velocity
        return planet
        
    def sprite_move(self,mpos):
        #if selected in grab mode, mpos = mousemotion
        if self.selected:
            #then move selected sprite to mouse position
            self.selected.set_pos(*mpos)
            
    def listen(self,mpos):
        """Listen mouse button down"""
        mx,my = mpos
        if self.line_btn.clicked(mx,my): #force line button
            conf.draw_line = not conf.draw_line #toggle force line
            
        elif self.grab_btn.clicked(mx,my): #Grab button
            self.create=not self.create #toggle Grab | Create mode
            if self.selected: #Clearing previous selection
                self.selected.static = self.sel_state
                self.selected = None
                
        elif self.star_btn.clicked(mx,my) and self.create:
            self.planet = not self.planet #Toggle Planet | star mode
        
        elif self.path_btn.clicked(mx,my):
            conf.draw_path = not conf.draw_path
            
        elif self.clear_btn.clicked(mx,my): #Clear
            self.sprites = [] #new empty list
            
        elif self.planet_vel_btn.clicked(mx,my) and self.create and self.planet:
            #planet velocity is only valid in create and planet mode
            conf.planet_velocity = not conf.planet_velocity
            
        elif self.static_btn.clicked(mx,my):
            #Toggle last selected sprites static state
            if self.last_selected:
                self.last_selected.static = not self.last_selected.static
                
        elif self.kill_on_btn.clicked(mx,my):
            #toggle conf.kill
            conf.kill = not conf.kill
            
        elif self.del_btn.clicked(mx,my) and conf.kill:
            #Making last selected sprites alive state to dead.
            #Later it will be killed.
            if self.last_selected:
                self.last_selected.alive = False
                self.last_selected = None
            
        elif self.create:
            if self.planet:
                planet = self.create_planet()
                planet.set_pos(mx,my)
                self.sprites.append(planet)
            else: #star mode
                star = self.create_star()
                star.set_pos(mx,my)
                self.sprites.insert(0,star)
                star.static=True

        elif not self.create and not self.selected:
            #elif in grab mode
            for sprite in self.sprites:
                #check which sprite is under mouse clicked postion
                sx,sy = sprite.position
                r = sprite.size
                if sx<mx<sx+r and sy<my<sy+r:
                    self.selected=sprite #storing in self.selected
                    #so mouse motion event can be applied by self.sprite_move method
                    self.sel_state=self.selected.static
                    self.selected.static=True
        
                    
    def apply_gravity(self):
        for i,sprite in enumerate(self.sprites):
            if conf.kill:
                if not sprite.alive:
                    #storing in dead sprites
                    self.dead_sprites.append(sprite)
            sprite.move(self.sprites,i)
        if conf.kill:
            for sprite in self.dead_sprites:
                #all the dead sprite are being removed from all sprites
                self.sprites.remove(sprite)
            self.dead_sprites = [] #no more dead sprites
            
    def render(self):
        for sprite in self.sprites:
            sprite.render()
            
        if self.create:#it enables planet or star button
            self.create_btn.render()
            if self.planet: #it enable velocity button
                self.planet_btn.render()
                if conf.planet_velocity: #vel on button
                    self.planet_vel_btn.render()
                else:#vel off button
                    self.planet_vel_off_btn.render()
            else:
                self.star_btn.render()
        else: #grab mode
            self.grab_btn.render()
            
           
        if conf.kill: #it enables del button
            self.kill_on_btn.render()
            if self.last_selected: #if there is a selection
                self.del_btn.render() #render del button
        else:
            self.kill_off_btn.render()
            
            
        self.line_btn.render() #force line button
        self.clear_btn.render()
        self.path_btn.render()
        if self.last_selected:
            self.static_btn.render()
        
#from gameUtils import Camera
def simulate():
    screen = pygame.display.set_mode((conf.screen_w, conf.screen_h))
    game = Game(screen)
    clock = pygame.time.Clock()
    #camera = Camera(screen)
    while True:
        clock.tick(conf.fps)
        screen.fill(conf.bg)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                game.listen(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                if not game.create: #grab mode
                    game.sprite_move(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                if game.selected:
                    #restoring selected sprites state as it was before
                    game.selected.static = game.sel_state
                    game.last_selected = game.selected
                    #make it none to prevent listening mouse motion
                    game.selected = None
        
        game.apply_gravity()
        game.render()
        #camera.snap_pointer()
        pygame.display.update()
        
if __name__ == "__main__":
    if (in_android:=False):
        scr_w = 720
        scr_h = 1440
    else:
        scr_w = 500
        scr_h = 500
        conf.fps = 500
        conf.path_sample_sec=100
        conf.path_sample_size = 70
        #conf.bg=(210,210,210)
        #conf.button_bg=(10,10,10)
        
    conf.set_screen_info(scr_w,scr_h)
    simulate()
