import math
import time
import queue
import pygame
import pathlib
from umg_game import hex_geometry, load_mechs, colors


SQRT3 = math.sqrt(3)


class Test():
    def __init__(self):
        print('created')


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
    def __init__(self, screen, hex_cell, mech_object=None, player=None, name=None):
        self.screen = screen
        self.hex_cell = hex_cell
        self.hex_cell.token = self
        self.x = self.hex_cell.x
        self.y = self.hex_cell.y
        self.shape_shadow = (5, 36, 50, 24)
        self.shape_player_flag = (16, 65, 29, 3)
        self.surf = pygame.Surface((60, 80), pygame.SRCALPHA)
        self.player = player

        self.mech = mech_object
        if self.mech:
            self.name = self.mech.name
        else:
            self.name = name
        img_name = '/'.join(self.mech.image.split('/')[3:])
        print(img_name)
        self.mech_img = pygame.image.load(img_name) 
        self.screen.blit(self.mech_img, (self.x, self.y))

    def update(self):
        pygame.draw.ellipse(self.surf, (124, 124, 24), self.shape_shadow)
        pygame.draw.rect(self.surf, self.player.color, self.shape_player_flag)
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
        self.hover_old = None
        self.chosen_old = None
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

        # Setting hex positions and creating map
        for q in range(-self.radius+1, self.radius):
            for r in range(-self.radius+1, self.radius):
                r_offset = r*(SQRT3*self.size/2+2)
                rq_offset = q*SQRT3*self.size/4
                q_offset = q*(3*self.size/4+2)
                if q+r in range(-self.radius+1, self.radius):
                    self.hexmap.append(Hex(self.screen, self.center+q_offset, self.center+r_offset+rq_offset, self.size, (q, r)))
                    self.tiles[q+self.radius-1][r+self.radius-1] = self.hexmap[-1]

    def reset(self):
        # Iterate through all hexes
        for hex_cell in self.hexmap:
            # Color reset
            hex_cell.update(x_offset=self.x_offset, y_offset=self.y_offset)

    def update(self):
        # Iterate through all hexes
        for hex_cell in self.hexmap:
            # Visibilty highlight
            if hex_cell.has_los and self.chosen_hex:
                hex_cell.update(colors.vis, x_offset=self.x_offset, y_offset=self.y_offset)
            # Visibilty highlight
            if hex_cell.has_mv and self.chosen_hex:
                hex_cell.update(colors.mov, x_offset=self.x_offset, y_offset=self.y_offset)
            # Rock coloring
            if hex_cell.token:
                if hex_cell.token.name == 'Rock':
                    hex_cell.update(colors.rock, x_offset=self.x_offset, y_offset=self.y_offset)
                    
        # Hover highlight
        if self.hover and hasattr(self.hover.token, 'player'):
            self.hover.update(self.hover.token.player.color,
                              x_offset=self.x_offset, y_offset=self.y_offset)
        elif self.hover and self.hover.token is not None:
            self.hover.update(colors.rock_highlight,
                              x_offset=self.x_offset, y_offset=self.y_offset)
        elif self.hover:
            self.hover.update(colors.highlight, x_offset=self.x_offset, y_offset=self.y_offset)
        
        # Display line of sight
        if self.hover and self.chosen_hex and self.show_los:
            _, los_path = self.check_line_of_sight(self.chosen_hex, self.hover)
            _ = [tile.update(colors.dred, x_offset=self.x_offset, y_offset=self.y_offset) for tile in los_path]
        # Display pathfinding
        elif self.hover and self.chosen_hex:
            if self.chosen_hex.token:
                if hasattr(self.chosen_hex.token, 'mech'):
                    if self.hover != self.hover_old:
                        self.pathfinding_path = self.astar_pathfinding(self.chosen_hex, self.hover)
                        self.hover_old = self.hover
                    if len(self.pathfinding_path) > self.chosen_hex.token.mech.remaining_mv+1:
                        self.pathfinding_path = self.pathfinding_path[1:self.chosen_hex.token.mech.remaining_mv+1]
                    _ = [tile.update(colors.dblue, x_offset=self.x_offset,
                                    y_offset=self.y_offset) for tile in self.pathfinding_path]

        # Cell selection
        if self.chosen_hex:
            self.chosen_hex.update(colors.selection, x_offset=self.x_offset, y_offset=self.y_offset)

        # Selected cell hover highlight
        if self.hover is self.chosen_hex and self.hover:
            self.chosen_hex.update((14, 14, 204), x_offset=self.x_offset, y_offset=self.y_offset)

        # Redraw tokens
        for hex_cell in self.hexmap:
            if hex_cell.token:
                hex_cell.token.update()
        if self.chosen_hex is None:
            self.pathfinding_path = []

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
                    if clicked_hex.surf.get_rect(topleft=(clicked_hex.x+self.x_offset,
                                                          clicked_hex.y+self.y_offset))\
                                                          .collidepoint(x, y):
                        if clicked_hex.mask.get_at((x-clicked_hex.x-self.x_offset,
                                                    y-clicked_hex.y-self.y_offset)):
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

    def get_neighbours(self, hex_tile):
        q_id = hex_tile.axial_id.q
        r_id = hex_tile.axial_id.r

        # Neigbours ids
        hexes = (q_id, r_id), (q_id, r_id+1), (q_id, r_id-1), \
                (q_id-1, r_id), (q_id-1, r_id+1), \
                (q_id+1, r_id), (q_id+1, r_id-1)

        ret = []

        for axial_id in hexes:
            try:
                tile = self.get_tile_from_axial(hex_geometry.Axial(*axial_id))
                if tile is not None:
                    ret.append(tile)
            except IndexError:
                pass

        return ret


    def astar_pathfinding(self, start, goal):
        frontier = queue.PriorityQueue()
        frontier.put((0, start))
        came_from = dict()
        cost_so_far = dict()
        came_from[start] = None
        cost_so_far[start] = 0

        if goal.token:
            return []

        while not frontier.empty():
            current = frontier.get()[1]

            if current == goal:
                path = []
                while current:
                    path.insert(0, current)
                    current = came_from[current]
                return path

            for child in self.get_neighbours(current):
                new_cost = cost_so_far[current] + 1
                if child.token:
                    continue
                if child not in cost_so_far or new_cost < cost_so_far[child]:
                    cost_so_far[child] = new_cost
                    priority = new_cost + hex_geometry.cube_distance(goal.cube_id, child.cube_id)
                    frontier.put((priority, child))
                    came_from[child] = current

        return []


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
        self.points = (side+side, 0+side), (half+side, diag+side), (-half+side, diag+side),\
                      (-side+side, 0+side), (-half+side, -diag+side), (half+side, -diag+side)
        pygame.draw.polygon(self.surf, colors.tile, self.points)
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
        self.has_mv = False

    def update(self, color=None, x_offset=0, y_offset=0):
        if color:
            pygame.draw.polygon(self.surf, color, self.points)
        else:
            pygame.draw.polygon(self.surf, colors.tile, self.points)
        self.screen.blit(self.surf, (self.x+x_offset, self.y+y_offset))
        if self.token:
            self.token.update()

    def __lt__(self, other):
        pass

    def __gt__(self, other):
        pass


if __name__ == '__main__':
    pass
