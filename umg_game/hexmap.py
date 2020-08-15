import pygame
import math


hex_ids = 0
SQRT3 = math.sqrt(3)


class Token(object):
    def __init__(self, screen, hex, name='None'):
        self.name = name
        self.screen = screen
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
        self.screen.blit(self.surf, (self.x, self.y))

    def move(self, hex):
        if hex.token:
            return
        self.hex.token = None
        self.hex = hex
        self.hex.token = self
        self.x = self.hex.x
        self.y = self.hex.y


class HexMap(object):
    def __init__(self, screen):
        self.screen = screen
    
        self.chosen_hex = None
                
        self.size = 31

        self.hexmap = []
    
        self.radius = 7
        self.real_center = 200
        self.center = self.real_center-self.size/2
        self.tiles = [[None for i in range(-self.radius+1, self.radius)] for j in range(-self.radius+1, self.radius)]
        self.x_offset = 0
        self.y_offset = 0

        for q in range(-self.radius+1, self.radius):
            for r in range(-self.radius+1, self.radius):
                r_offset = r*(SQRT3*self.size/2+2)
                rq_offset = q*SQRT3*self.size/4
                q_offset = q*(3*self.size/4+2)
                if q+r in range(-self.radius+1, self.radius):
                    self.hexmap.append(Hex(self.screen, self.center+q_offset, self.center+r_offset+rq_offset, self.size, (q, r)))
                    self.tiles[q+self.radius-1][r+self.radius-1] = self.hexmap[-1]

    def update(self):
        for hex in self.hexmap:
            hex.update(x_offset=self.x_offset, y_offset=self.y_offset)
        if self.chosen_hex:
            self.chosen_hex.update((204,14,204),x_offset=self.x_offset, y_offset=self.y_offset)
        if self.hover:
            self.hover.update((14,204,204),x_offset=self.x_offset, y_offset=self.y_offset)
        if self.hover is self.chosen_hex and self.hover:
            self.chosen_hex.update((14,14,204),x_offset=self.x_offset, y_offset=self.y_offset)            

    def check_position(self, x, y):
        new_x = x-self.real_center
        new_y = y-self.real_center
        q_id = int(new_x/(3*self.size/4+2))
        r_id = round((new_y/(SQRT3*self.size/2+2)-(new_x/(3*self.size/4+2))/2))
        hexes = (q_id, r_id), (q_id, r_id+1), (q_id, r_id-1), \
                (q_id-1, r_id), (q_id-1, r_id+1), \
                (q_id+1, r_id), (q_id+1, r_id-1)
        print(q_id, r_id)
        print(hexes)
        for item in hexes:
            try:
                clicked_hex = self.tiles[item[0]+self.radius-1][item[1]+self.radius-1]
                if clicked_hex:
                    if clicked_hex.surf.get_rect(topleft=(clicked_hex.x+self.x_offset, clicked_hex.y+self.y_offset)).collidepoint(x,y):

                        if clicked_hex.mask.get_at((x-clicked_hex.x-self.x_offset, y-clicked_hex.y-self.y_offset)):
                            print('clicked on mask', clicked_hex.id)
                            return clicked_hex
            except IndexError:
                pass
        return None


class Hex(object):
    def __init__(self, screen, x, y, size, id):
        self.x = int(x)
        self.y = int(y)
        self.screen = screen
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

        # self.choice = False

    def update(self, color=None, x_offset=0, y_offset=0):
        if color:
            pygame.draw.polygon(self.surf, color, self.points)
        else:
            pygame.draw.polygon(self.surf, (204,204,14), self.points)
        self.screen.blit(self.surf, (self.x+x_offset, self.y+y_offset))
        if self.token:
            self.token.update()


def run():
    pygame.init()
    pygame.font.init()
    clock = pygame.time.Clock()
    myfont = pygame.font.SysFont('Comic Sans MS', 14)

    width=600
    height=400
    screen = pygame.display.set_mode((width, height ))

    hexmap_object = HexMap(screen)

    Token(screen, hexmap_object.tiles[6][6], 'Adam')
    Token(screen, hexmap_object.tiles[6][8], 'Kuba')

    pygame.display.flip() # paint screen one time
            
    running = True
    hover_text = ''

    # Main loop
    while (running):
        for event in pygame.event.get():
            # Quit the game if event is "quit"
            if event.type == pygame.QUIT:
                running = False
            # Mouse hover highlight
            if event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                hexmap_object.hover = hexmap_object.check_position(x, y)
            # Mouse click
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                clicked_hex = hexmap_object.check_position(x, y)
                if clicked_hex:
                    # If clicked hex is already chosen, unclick it
                    if clicked_hex == hexmap_object.chosen_hex:
                        hexmap_object.chosen_hex = None
                    # If holding token, put it on an empty place
                    elif not clicked_hex.token and hexmap_object.chosen_hex:
                        hexmap_object.chosen_hex.token.move(clicked_hex)
                        hexmap_object.chosen_hex = None
                    # If clicking on space with token, grab it
                    else:
                        hexmap_object.chosen_hex = clicked_hex
                hexmap_object.hover = clicked_hex

        # Print text on side
        if hexmap_object.hover:
            if hexmap_object.hover.token:
                hover_text = hexmap_object.hover.token.name
        elif hexmap_object.chosen_hex:
            if hexmap_object.chosen_hex.token:
                print(hexmap_object.chosen_hex.token.name)
                hover_text = hexmap_object.chosen_hex.token.name
        else:
            hover_text = ''
                            
        # Update screen
        screen.fill(pygame.Color("black"))
        textsurface = myfont.render(hover_text, False, (200, 0, 0))
        screen.blit(textsurface,(400,20))
        hexmap_object.update()
        pygame.display.update()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    run()