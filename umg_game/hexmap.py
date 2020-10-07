import math
import pygame
import pathlib
from umg_game import hex_geometry, load_mechs


SQRT3 = math.sqrt(3)


class Rock(object):
    def __init__(self, screen, hex_cell, name='Rock'):
        self.name = name
        self.screen = screen
        self.hex_cell = hex_cell
        self.hex_cell.token = self
        self.x = self.hex_cell.x
        self.y = self.hex_cell.y

    def update(self):
        pass

    def move(self, hex_cell):
        pass


class Token(object):
    def __init__(self, screen, hex_cell, mech_object):
        self.screen = screen
        self.hex_cell = hex_cell
        self.hex_cell.token = self
        self.x = self.hex_cell.x
        self.y = self.hex_cell.y
        self.shape = (5, 36, 50, 24)
        self.surf = pygame.Surface((60, 60), pygame.SRCALPHA)
        # pygame.draw.rect(self.surf, (250, 0, 0), self.shape)
        # screen.blit(self.surf, (self.x, self.y))
        self.mech = mech_object
        self.name = self.mech.name
        self.mech_img = pygame.image.load(self.mech.image) 
        # self.mech_img = pygame.image.load('./umg_shared/mech_images/mech_b.png') 
        self.screen.blit(self.mech_img, (self.x, self.y))

    def update(self):
        pygame.draw.ellipse(self.surf, (124, 124, 24), self.shape)
        self.screen.blit(self.surf, (self.x, self.y-13))
        self.screen.blit(self.mech_img, (self.x, self.y-20))

    def move(self, hex_cell):
        if hex_cell.token:
            return
        self.hex_cell.token = None
        self.hex_cell = hex_cell
        self.hex_cell.token = self
        self.x = self.hex_cell.x
        self.y = self.hex_cell.y


class HexMap(object):
    def __init__(self, screen):
        self.screen = screen
    
        # Hex parameters
        self.chosen_hex = None
        self.hover = None
        self.show_los = False
                
        # Map parameters
        self.size = 61
        self.radius = 6
        self.real_center = 320
        self.center = self.real_center-self.size/2
        self.x_offset = 0
        self.y_offset = 0

        # Hex lists (different addresing?)
        self.hexmap = []
        self.tiles = [[None for i in range(-self.radius+1, self.radius)] for j in range(-self.radius+1, self.radius)]

        # Setting hex size and positions
        for q in range(-self.radius+1, self.radius):
            for r in range(-self.radius+1, self.radius):
                r_offset = r*(SQRT3*self.size/2+2)
                rq_offset = q*SQRT3*self.size/4
                q_offset = q*(3*self.size/4+2)
                if q+r in range(-self.radius+1, self.radius):
                    self.hexmap.append(Hex(self.screen, self.center+q_offset, self.center+r_offset+rq_offset, self.size, (q, r)))
                    self.tiles[q+self.radius-1][r+self.radius-1] = self.hexmap[-1]

    def update(self):
        # Iterate through all hexes
        for hex_cell in self.hexmap:
            # Color reset
            hex_cell.update(x_offset=self.x_offset, y_offset=self.y_offset)
            # Visibilty highlight
            if hex_cell.has_los and self.chosen_hex:
                hex_cell.update((180, 100, 49), x_offset=self.x_offset, y_offset=self.y_offset)
            # Rock coloring
            if hex_cell.token:
                if hex_cell.token.name == 'Rock':
                    hex_cell.update((128, 128, 128), x_offset=self.x_offset, y_offset=self.y_offset)
        # Linear approx pathfinding
        if self.hover and self.chosen_hex:
            _, los_path = self.check_line_of_sight(self.chosen_hex, self.hover)
            _ = [tile.update((14, 124, 124), x_offset=self.x_offset, y_offset=self.y_offset) for tile in los_path]
        # Cell selection
        if self.chosen_hex:
            self.chosen_hex.update((204, 14, 204), x_offset=self.x_offset, y_offset=self.y_offset)
        # Hover highlight
        if self.hover:
            self.hover.update((14, 204, 204), x_offset=self.x_offset, y_offset=self.y_offset)
        # Selected cell hover highlight
        if self.hover is self.chosen_hex and self.hover:
            self.chosen_hex.update((14, 14, 204), x_offset=self.x_offset, y_offset=self.y_offset)
        # Redraw tokens
        for hex_cell in self.hexmap:
            if hex_cell.token:
                hex_cell.token.update()

    def check_position(self, x, y):
        new_x = x-self.real_center
        new_y = y-self.real_center
        q_id = int(new_x/(3*self.size/4+2))
        r_id = round((new_y/(SQRT3*self.size/2+2)-(new_x/(3*self.size/4+2))/2))
        
        # Neigbours ids
        hexes = (q_id, r_id), (q_id, r_id+1), (q_id, r_id-1), \
                (q_id-1, r_id), (q_id-1, r_id+1), \
                (q_id+1, r_id), (q_id+1, r_id-1)
        
        for item in hexes:
            try:
                clicked_hex = self.tiles[item[0]+self.radius-1][item[1]+self.radius-1]
                if clicked_hex:
                    if clicked_hex.surf.get_rect(topleft=(clicked_hex.x+self.x_offset, clicked_hex.y+self.y_offset)).collidepoint(x,y):

                        if clicked_hex.mask.get_at((x-clicked_hex.x-self.x_offset, y-clicked_hex.y-self.y_offset)):
                            print('clicked on mask', clicked_hex.hex_id)
                            return clicked_hex
            except IndexError:
                pass
        return None

    def get_tile_from_cube(self, cube):
        axial = hex_geometry.cube_to_axial(cube)
        return self.get_tile_from_axial(axial)

    def get_tile_from_axial(self, axial):
        return self.tiles[axial.q+self.radius-1][axial.r+self.radius-1]

    def check_line_of_sight(self, a, b):
        distance = hex_geometry.cube_distance(a.cube_id, b.cube_id)
        if distance > 0:
            main_path = hex_geometry.cube_linedraw(a.cube_id, b.cube_id, distance, 0.0001)
            alter_path = hex_geometry.cube_linedraw(a.cube_id, b.cube_id, distance, -0.0001)

            final_path = []
            
            for main_id in main_path:
                proposed_tile = self.get_tile_from_cube(main_id)
                if proposed_tile.token and proposed_tile not in [a, b]:
                    final_path = []
                    for alter_id in alter_path:
                        proposed_tile = self.get_tile_from_cube(alter_id)
                        if proposed_tile.token and proposed_tile not in [a, b]:
                            print('False1')
                            return [False, final_path]
                        final_path.append(proposed_tile)
                    print('True1')
                    return [True, final_path]
                final_path.append(proposed_tile)
                
            print('True2')
            return [True, final_path]
        
        print('False2')
        return [False, []]


class Hex(object):
    def __init__(self, screen, x, y, size, hex_id):
        self.x = int(x)
        self.y = int(y)

        self.screen = screen

        # Hex parameters
        self.size = size
        self.hex_id = hex_geometry.Axial(*hex_id)
        self.cube_id = hex_geometry.axial_to_cube(self.hex_id)
        
        # Drawing
        self.surf = pygame.Surface((size, size), pygame.SRCALPHA)
        a = self.size/2
        side = int(math.floor(a))
        diag = int(math.floor(SQRT3*a/2))
        half = int(math.floor(a/2))
        self.points = (side+side, 0+side), (half+side, diag+side), (-half+side, diag+side), (-side+side, 0+side), (-half+side, -diag+side), (half+side, -diag+side)
        pygame.draw.polygon(self.surf, (204, 204, 14), self.points)
        self.mask = pygame.mask.from_surface(self.surf)
        # print(self.points)

        # Hex interactions
        self.token = None
        self.has_los = False

    def update(self, color=None, x_offset=0, y_offset=0):
        if color:
            pygame.draw.polygon(self.surf, color, self.points)
        else:
            pygame.draw.polygon(self.surf, (204, 204, 14), self.points)
        self.screen.blit(self.surf, (self.x+x_offset, self.y+y_offset))
        if self.token:
            self.token.update()


def run():
    pygame.init()
    pygame.font.init()
    clock = pygame.time.Clock()
    myfont = pygame.font.SysFont('dejavusansmono', 20)

    width = 1000
    height = 640
    screen = pygame.display.set_mode((width, height))

    hexmap_object = HexMap(screen)

    # Mech loading
    squad_path = pathlib.Path('./squads/alpha_squad.sqd')
    mech_list = load_mechs.load_mech_list(squad_path)

    Token(screen, hexmap_object.hexmap[48], mech_list[0])
    Token(screen, hexmap_object.hexmap[24], mech_list[1])
    Token(screen, hexmap_object.hexmap[27], mech_list[2])

    Rock(screen, hexmap_object.get_tile_from_axial(hex_geometry.Axial(0, 0)))
    Rock(screen, hexmap_object.get_tile_from_axial(hex_geometry.Axial(0, 1)))
    Rock(screen, hexmap_object.get_tile_from_axial(hex_geometry.Axial(2, 1)))
    Rock(screen, hexmap_object.get_tile_from_axial(hex_geometry.Axial(3, -3)))
    Rock(screen, hexmap_object.get_tile_from_axial(hex_geometry.Axial(-3, -1)))
    Rock(screen, hexmap_object.get_tile_from_axial(hex_geometry.Axial(-1, -3)))
    Rock(screen, hexmap_object.get_tile_from_axial(hex_geometry.Axial(-4, 3)))
    Rock(screen, hexmap_object.get_tile_from_axial(hex_geometry.Axial(-4, 3)))
    Rock(screen, hexmap_object.get_tile_from_axial(hex_geometry.Axial(-4, 4)))
    Rock(screen, hexmap_object.get_tile_from_axial(hex_geometry.Axial(-3, 4)))
    Rock(screen, hexmap_object.get_tile_from_axial(hex_geometry.Axial(-2, 4)))
    Rock(screen, hexmap_object.get_tile_from_axial(hex_geometry.Axial(-2, 5)))
    Rock(screen, hexmap_object.get_tile_from_axial(hex_geometry.Axial(4, -2)))
    Rock(screen, hexmap_object.get_tile_from_axial(hex_geometry.Axial(0, -4)))
    Rock(screen, hexmap_object.get_tile_from_axial(hex_geometry.Axial(3, 1)))

    pygame.display.flip() # paint screen one time
            
    running = True
    hover_text = ''

    # Main loop
    while running:
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
                    # If clicked hex_cell is already chosen, unclick it
                    if clicked_hex == hexmap_object.chosen_hex:
                        hexmap_object.chosen_hex = None
                    # If holding token, put it on an empty place
                    elif not clicked_hex.token and hexmap_object.chosen_hex:
                        if hexmap_object.chosen_hex.token:
                            hexmap_object.chosen_hex.token.move(clicked_hex)
                            hexmap_object.chosen_hex = None
                        # If not holding token, pick cliked hex
                        else:
                            hexmap_object.chosen_hex = clicked_hex
                    # If clicking on space with token, grab it
                    else:
                        hexmap_object.chosen_hex = clicked_hex
                hexmap_object.hover = clicked_hex
            if event.type == pygame.KEYDOWN:
                # Pause game on space during debugging
                if event.key == pygame.K_SPACE:
                    pass
                # Show visibility overlay
                if event.key == pygame.K_v:
                    if hexmap_object.show_los:
                        for hex_cell in hexmap_object.hexmap:
                            hex_cell.has_los = False
                        hexmap_object.show_los = False
                    elif hexmap_object.chosen_hex:
                        for hex_cell in hexmap_object.hexmap:
                            has_los, _ = hexmap_object.check_line_of_sight(hex_cell, hexmap_object.chosen_hex)
                            hex_cell.has_los = has_los
                            hexmap_object.show_los = True
                    else:
                        hexmap_object.show_los = False

        # Print text on side
        if hexmap_object.hover:
            if hexmap_object.hover.token:
                token = hexmap_object.hover.token
            else:
                token = None
        elif hexmap_object.chosen_hex:
            if hexmap_object.chosen_hex.token:
                token = hexmap_object.chosen_hex.token
            else:
                token = None
        else:
            token = None

        if token:
            hover_text = f'{token.name}\n\n'
            if hasattr(token, 'mech'):
                mech = token.mech
                hover_text += f'AM: {mech.current_hp}  EG: {mech.EG}\n'
                hover_text += f'Energy: {mech.energy}\n\n'
                for slot in mech.slots:
                    if mech.slots[slot]:
                        hover_text += f'{mech.slots[slot].name}\n'
        else:
            hover_text = ''
        
        # Update screen
        screen.fill(pygame.Color("black"))

        for i, line in enumerate(hover_text.splitlines()):
            textsurface = myfont.render(line, False, (200, 200, 200))
            screen.blit(textsurface, (680, 200+i*24))

        hexmap_object.update()
        pygame.display.update()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    run()
