import pygame
import math

hex_ids = 0
SQRT3 = math.sqrt(3)


class Token(object):
    def __init__(self, hex):
        self.hex = hex
        self.hex.token = self
        self.x = self.hex.x
        self.y = self.hex.y
        self.shape = (10,10,20,20)
        self.surf = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.rect(self.surf, (250, 0, 0), self.shape)
        screen.blit(self.surf, (self.x, self.y))

    def update(self):
        pygame.draw.rect(self.surf, (250, 0, 0), self.shape)
        screen.blit(self.surf, (self.x, self.y))


class HexMap(object):
    def __init__(self):
        self.chosen_hex = None
                
        self.size = 61

        self.hexmap = []

        self.radius = 7
        self.real_center = 400
        self.center = self.real_center-self.size/2
        self.tiles = [[None for i in range(-self.radius+1, self.radius)] for j in range(-self.radius+1, self.radius)]

        for q in range(-self.radius+1, self.radius):
            for r in range(-self.radius+1, self.radius):
                r_offset = r*(SQRT3*self.size/2+2)
                rq_offset = q*SQRT3*self.size/4
                q_offset = q*(3*self.size/4+2)
                if q+r in range(-self.radius+1, self.radius):
                    self.hexmap.append(Hex(self.center+q_offset, self.center+r_offset+rq_offset, self.size, (q, r)))
                    self.tiles[q+self.radius-1][r+self.radius-1] = self.hexmap[-1]

    def update(self):
        for hex in self.hexmap:
            hex.update()
        if self.chosen_hex:
            self.chosen_hex.update((204,14,204))
        if self.hover:
            self.hover.update((14,204,204))
        if self.hover is self.chosen_hex and self.hover:
            self.chosen_hex.update((14,14,204))            

    def check_position(self, x, y):
        new_x = x-self.real_center
        new_y = y-self.real_center
        q_id = int(new_x/(3*self.size/4+2))
        r_id = round((new_y/(SQRT3*self.size/2+2)-(new_x/(3*self.size/4+2))/2))
        hexes = (q_id, r_id), (q_id, r_id+1), (q_id, r_id-1), \
                (q_id-1, r_id), (q_id-1, r_id+1), \
                (q_id+1, r_id), (q_id+1, r_id-1)
                # (q_id, r_id+2), (q_id, r_id-2), \
                # (q_id-2, r_id), (q_id-2, r_id+2), \
                # (q_id+2, r_id), (q_id+2, r_id-2), \
                # (q_id-1, r_id+2), (q_id-2, r_id+1), \
                # (q_id+2, r_id-1), (q_id+2, r_id-1), \
                # (q_id+2, r_id+1), (q_id-2, r_id-1)
        print(q_id, r_id)
        print(hexes)
        for item in hexes:
            try:
                hex_object = self.tiles[item[0]+self.radius-1][item[1]+self.radius-1]
                if hex_object:
                    if hex_object.surf.get_rect(topleft=(hex_object.x, hex_object.y)).collidepoint(x,y):
                    # print("maks:", hex_object.mask.get_at((x-hex_object.x, y-hex_object.y)))
                        if hex_object.mask.get_at((x-hex_object.x, y-hex_object.y)):
                            print('clicked on mask', hex_object.id)
                            return hex_object
            except IndexError as e:
                # print(e)
                pass
        return None


class Hex(object):
    def __init__(self, x, y, size, id):
        self.x = int(x)
        self.y = int(y)
        self.size = size
        self.surf = pygame.Surface((size, size), pygame.SRCALPHA)
        self.id = id
        self.token = None
        a = self.size/2
        side = int(math.floor(a))
        diag = int(math.floor(SQRT3*a/2))
        half = int(math.floor(a/2))
        self.points = (side+side,0+side), (half+side, diag+side), (-half+side, diag+side), (-side+side,0+side), (-half+side, -diag+side), (half+side, -diag+side)
        print(self.points)
        pygame.draw.polygon(self.surf, (204,204,14), self.points)
        self.mask = pygame.mask.from_surface(self.surf)

        self.choice = False

    def update(self, color=None):
        if color:
            pygame.draw.polygon(self.surf, color, self.points)
        else:
            pygame.draw.polygon(self.surf, (204,204,14), self.points)
        screen.blit(self.surf, (self.x, self.y))
        if self.token:
            self.token.update()
        

pygame.init()
width=800
height=800
screen = pygame.display.set_mode((width, height ))

hexmap_object = HexMap()

token = Token(hexmap_object.tiles[6][6])

pygame.display.flip() # paint screen one time
           

running = True
while (running):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEMOTION:
            x, y = event.pos
            hexmap_object.hover = hexmap_object.check_position(x, y)
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            hex_object = hexmap_object.check_position(x, y)
            if hex_object:
                if hex_object.choice:
                    hex_object.choice = False
                    hexmap_object.chosen_hex = None
                else:
                    token = None
                    if hexmap_object.chosen_hex:
                        token = hexmap_object.chosen_hex.token
                        hexmap_object.chosen_hex.token = None
                        hexmap_object.chosen_hex.choice = False
                    hex_object.choice = True
                    hexmap_object.chosen_hex = hex_object
                    print(token)
                    if token:
                        token.hex = hex_object
                        token.x = hex_object.x
                        token.y = hex_object.y
                        hex_object.token = token
                        


    hexmap_object.update()
    pygame.display.update()

pygame.quit()
