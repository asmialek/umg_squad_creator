import pygame


hex_ids = 0

class Hex(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.surf = pygame.Surface((40, 40), pygame.SRCALPHA)
        self.token = None
        self.points = (9, 0), (29, 0), (39, 19), (29, 39), (9, 39), (0, 19)
        pygame.draw.polygon(self.surf, (204,204,14), self.points)
        self.mask = pygame.mask.from_surface(self.surf)
        screen.blit(self.surf, (self.x, self.y))
        global hex_ids
        self.id = hex_ids
        hex_ids += 1
        self.chosen = False
        self.hover = False

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

    def move(self, hex, map):
        if hex.token:
            raise RuntimeError('This hex is taken!')
        self.hex.token = None
        self.surf.fill((0, 0, 0, 0))
        screen.blit(self.surf, (self.x, self.y))
        update_map(map)
        self.hex = hex
        self.hex.token = self
        self.x = self.hex.x
        self.y = self.hex.y
        pygame.draw.rect(self.surf, (250, 0, 0), self.shape)
        screen.blit(self.surf, (self.x, self.y))


def update_map(map):
    for hex in map:
        pygame.draw.polygon(hex.surf, (204,204,14), hex.points)
        screen.blit(item.surf, (hex.x, hex.y))
        if hex.hover:
            pygame.draw.polygon(hex.surf, (204,14,14), hex.points)
            screen.blit(hex.surf, (hex.x, hex.y))
        if hex.chosen:
            pygame.draw.polygon(hex.surf, (14,204,14), hex.points)
            screen.blit(hex.surf, (hex.x, hex.y))

def update_tokens(tokens):
    for token in tokens:
        screen.blit(token.surf, (token.x, token.y))

        

pygame.init()
width=350
height=400
screen = pygame.display.set_mode((width, height ))
pygame.display.set_caption('clicked on image')

map = []
for i in range(4):
    for j in range(14):
        if not j%2:
            map.append(Hex(40+i*64, 40+j*22))
        else:
            map.append(Hex(72+i*64, 62+(j-1)*22)) 

tokens = (Token(map[10]), Token(map[12]), Token(map[32]), Token(map[3]), Token(map[20]))
chosen_token = None

pygame.display.flip() # paint screen one time


running = True
while (running):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEMOTION:
            # Set the x, y postions of the mouse click
            x, y = event.pos
            for item in map:
                if not item.chosen:
                    if item.surf.get_rect(topleft=(item.x, item.y)).collidepoint(x,y) and item.mask.get_at((x-item.x, y-item.y)):
                            item.hover = True
                            # item.surf.fill((200,0,0))
                    else:
                        item.hover = False                                

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Set the x, y postions of the mouse click
            x, y = event.pos
            for item in map:
                if item.surf.get_rect(topleft=(item.x, item.y)).collidepoint(x,y):
                    if item.mask.get_at((x-item.x, y-item.y)):
                        print('clicked on hex', item.id)
                        # item.surf.fill((200,0,0))
                        for hex in map:
                            hex.chosen = False
                            hex.hover = False
                        item.chosen = True
                        if item.token:
                            chosen_token = item.token
                        elif chosen_token:
                            chosen_token.move(item, map)
                            chosen_token = None
                        pygame.draw.polygon(item.surf, (14,14,204), item.points)
                        screen.blit(item.surf, (item.x, item.y))
            pass
                        
    update_map(map)
    update_tokens(tokens)
    pygame.display.update()

pygame.quit()
