import math
import time
import pygame
import pathlib
from umg_game import hex_geometry, load_mechs


SQRT3 = math.sqrt(3)


class Node(object):
    def __init__(self, hex_tile, parent=None):
        self.hex_tile = hex_tile
        self.parent = parent
        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.hex_tile == other.hex_tile


class Player(object):
    def __init__(self, name, color=(100, 100, 200)):
        self.name = name
        self.turn = False
        self.energy = 0
        self.color = color


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
    def __init__(self, screen, hex_cell, mech_object, player=None):
        self.screen = screen
        self.hex_cell = hex_cell
        self.hex_cell.token = self
        self.x = self.hex_cell.x
        self.y = self.hex_cell.y
        self.shape = (5, 36, 50, 24)
        self.surf = pygame.Surface((60, 60), pygame.SRCALPHA)
        self.player = player

        self.mech = mech_object
        self.name = self.mech.name
        self.mech_img = pygame.image.load(self.mech.image) 
        self.screen.blit(self.mech_img, (self.x, self.y))

    def update(self):
        pygame.draw.ellipse(self.surf, (124, 124, 24), self.shape)
        self.screen.blit(self.surf, (self.x, self.y-13))
        self.screen.blit(self.mech_img, (self.x, self.y-20))

    def move(self, hex_cell):
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
        self.show_vis = False
        self.hover_hex_old = None
        self.pathfinding_path = []
        self.pathfinding_closed_list = []
                
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
        # Display line of sight 
        if self.hover and self.chosen_hex and self.show_los:
            _, los_path = self.check_line_of_sight(self.chosen_hex, self.hover)
            _ = [tile.update((14, 124, 124), x_offset=self.x_offset, y_offset=self.y_offset) for tile in los_path]
        # Display pathfinding
        elif self.hover and self.chosen_hex:
            if self.hover != self.hover_hex_old:
                t = time.time()
                self.pathfinding_path, self.pathfinding_closed_list = self.astar_pathfinding(self.chosen_hex, self.hover)
                print("Tictoc:", time.time()-t)
                self.hover_hex_old = self.hover
            _ = [tile.hex_tile.update((194, 194, 194), x_offset=self.x_offset, y_offset=self.y_offset) for tile in self.pathfinding_closed_list]
            _ = [tile.update((174, 54, 174), x_offset=self.x_offset, y_offset=self.y_offset) for tile in self.pathfinding_path]
        # Cell selection
        if self.chosen_hex:
            self.chosen_hex.update((204, 14, 204), x_offset=self.x_offset, y_offset=self.y_offset)
        # Hover highlight
        if self.hover and hasattr(self.hover.token, 'player'):
            self.hover.update(self.hover.token.player.color, x_offset=self.x_offset, y_offset=self.y_offset)
        elif self.hover:
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
        
        for axial_id in hexes:
            try:
                clicked_hex = self.get_tile_from_axial(hex_geometry.Axial(*axial_id))
                if clicked_hex:
                    if clicked_hex.surf.get_rect(topleft=(clicked_hex.x+self.x_offset, clicked_hex.y+self.y_offset)).collidepoint(x, y):
                        if clicked_hex.mask.get_at((x-clicked_hex.x-self.x_offset, y-clicked_hex.y-self.y_offset)):
                            # print('clicked on mask', clicked_hex.axial_id)
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
                            return [False, final_path]
                        final_path.append(proposed_tile)
                    return [True, final_path]
                final_path.append(proposed_tile)
            return [True, final_path]
        return [False, []]

    def astar_pathfinding(self, a, b):
        closed_list = []
        open_list = [Node(a, None)]

        # a.parent = None
        # a.f = 0
        # a.g = 0
        # a.h = 0

        if b.token:
            return [], []

        while open_list:
            open_list.sort(key=lambda x: x.f)
            
            # for item in open_list:
                # print(f"Pathfinding: {item.hex_tile.axial_id}, f={item.f}")
            
            # print(open_list)
            q = open_list.pop(0)
            closed_list.append(q)
            
            # if q.hex_tile == b:
            #     path = []
            #     while q:
            #         path.insert(0, q.hex_tile)
            #         q = q.parent
            #     return path, closed_list

            # Neigbours ids
            q_id = q.hex_tile.axial_id.q
            r_id = q.hex_tile.axial_id.r
            hexes = (q_id, r_id), (q_id, r_id+1), (q_id, r_id-1), \
                    (q_id-1, r_id), (q_id-1, r_id+1), \
                    (q_id+1, r_id), (q_id+1, r_id-1)

            succecsors = []
            for axial_id in hexes:
                try:
                    hex_tile = self.get_tile_from_axial(hex_geometry.Axial(*axial_id))
                    # print(hex_tile)
                    if hex_tile:
                        if hex_tile.token:
                            continue

                        succecsors.append(Node(hex_tile, q))
                    
                except IndexError:
                    continue

            # print(succecsors)
            
            for successor in succecsors:
                # print(successor)
                if successor.hex_tile == b:
                    path = []
                    while successor:
                        path.insert(0, successor.hex_tile)
                        successor = successor.parent
                    return path, closed_list

                
                for closed_child in closed_list:
                    if successor == closed_child:
                        continue
                            

                successor.g = q.g + 1
                successor.h = hex_geometry.cube_distance(b.cube_id, successor.hex_tile.cube_id)
                successor.f = successor.g + successor.h

                for open_node in open_list:
                    # if successor == open_node:
                    if successor == open_node and successor.f > open_node.f:
                        continue

                open_list.append(successor)


class Hex(object):
    def __init__(self, screen, x, y, size, axial_id):
        self.x = int(x)
        self.y = int(y)

        self.screen = screen

        # Hex parameters
        self.size = size
        self.axial_id = hex_geometry.Axial(*axial_id)
        self.cube_id = hex_geometry.axial_to_cube(self.axial_id)
        
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

        # Pathfinding parameters
        self.parent = None
        self.f = 0
        self.q = 0
        self.h = 0

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

    first_player = Player('Brorys', (100, 100, 200))
    second_player = Player('Pitor', (200, 100, 100))
    player_list = [first_player, second_player]
    current_player = first_player

    # Mech loading
    squad_path = pathlib.Path('./squads/alpha_squad.sqd')
    mech_list = load_mechs.load_mech_list(squad_path)

    Token(screen, hexmap_object.hexmap[48], mech_list[0], first_player)
    Token(screen, hexmap_object.hexmap[24], mech_list[1], first_player)
    Token(screen, hexmap_object.hexmap[27], mech_list[2], second_player)
    
    # Rock placing
    rock_range = [(0, 0), (0, 1), (2, 1), (3, -3), (-3, -1), (-1, -3),
                  (-4, 3), (-4, 3), (-4, 4), (-3, 4), (-2, 4), (-2, 5),
                  (4, -2), (0, -4), (3, 1), (2, 2), (2, 3), (-1, 2), (-2, 4)]

    for coords in rock_range:
        if not hexmap_object.get_tile_from_axial(hex_geometry.Axial(*coords)).token:
            Rock(screen, hexmap_object.get_tile_from_axial(hex_geometry.Axial(*coords)))
            print(f'Putting Rocks at {coords}.')
        else:
            print(f'Putting Rocks failed: {coords} is already taken.')

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
                            # Check whether chosen token is owned by the current player
                            if hasattr(hexmap_object.chosen_hex.token, 'player'):
                                if hexmap_object.chosen_hex.token.player == current_player:
                                    hexmap_object.chosen_hex.token.move(clicked_hex)
                                    hexmap_object.chosen_hex = None
                                else:
                                    hexmap_object.chosen_hex = None
                            else:
                                hexmap_object.chosen_hex = None
                        # If not holding token, pick cliked hex
                        else:
                            hexmap_object.chosen_hex = clicked_hex
                    # If clicking on space with token, grab it
                    else:
                        hexmap_object.chosen_hex = clicked_hex
                    print('Clicked:', clicked_hex.axial_id)
                hexmap_object.hover = clicked_hex
            if event.type == pygame.KEYDOWN:
                # Click "D" to pause game while debugging
                if event.key == pygame.K_d:
                    pass
                # Press Space to pass turn between players
                if event.key == pygame.K_SPACE:
                    current_player = player_list[0]
                    player_list = [*player_list[1:], player_list[0]]
                # Show visibility overlay
                if event.key == pygame.K_v:
                    if hexmap_object.show_vis:
                        for hex_cell in hexmap_object.hexmap:
                            hex_cell.has_los = False
                        hexmap_object.show_vis = False
                    elif hexmap_object.chosen_hex:
                        for hex_cell in hexmap_object.hexmap:
                            has_los, _ = hexmap_object.check_line_of_sight(hex_cell, hexmap_object.chosen_hex)
                            hex_cell.has_los = has_los
                            hexmap_object.show_vis = True
                    else:
                        hexmap_object.show_vis = False
                # Show line of sight
                if event.key == pygame.K_a:
                    hexmap_object.show_los = not hexmap_object.show_los

        # Set text to print on side
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

        text_color = (200, 200, 200)

        if token:
            hover_text = f'{token.name}\n\n'
            if hasattr(token, 'player'):
                text_color = token.player.color
            else:
                text_color = (200, 200, 200)
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
            textsurface = myfont.render(line, False, text_color)
            screen.blit(textsurface, (680, 200+i*24))

    
        player_text = myfont.render("Player: ", False, (200, 200, 200))
        screen.blit(player_text, (680, 460))

        if current_player:
            player_text = myfont.render(current_player.name, False, current_player.color)
            screen.blit(player_text, (780, 460))

        hexmap_object.update()
        pygame.display.update()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    run()
