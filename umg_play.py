import pygame
import pygame_gui
import pathlib
import copy
import time
from umg_game import hexmap, hex_geometry, load_mechs
from umg_shared import umg_logging


class Player(object):
    def __init__(self, name, color=(100, 100, 200)):
        self.name = name
        self.turn = False
        self.mech_list = []
        self.energy = 0
        self.energy_per_turn = 0
        self.color = color

    def update_params(self):
        self.energy_per_turn = sum([x.mech.EG for x in self.mech_list])


class Game(object):
    def __init__(self, hexmap_object, player_list, window_size=(1000, 640)):
        self.name = None
        self.hexmap_object = hexmap_object

        # Players and turns
        self.player_list = player_list
        self.current_player = player_list[0]
        self.current_player_list = copy.copy(self.player_list)
        
        self.turn = 0

        # Pygame initialization
        pygame.init()
        pygame.font.init()
        self.clock = pygame.time.Clock()
        self.font_base = self.define_fonts()
        self.window_size = window_size

        # Pygame graphics
        self.screen = self.create_window(self.window_size)
        self.background = pygame.Surface(self.window_size)
        self.background.fill(pygame.Color('#000000'))

        # Hexmap initialization
        self.hexmap_object = hexmap.HexMap(self.screen)

        # UI initialization
        self.ui_manager = pygame_gui.UIManager(self.window_size)
        self.time_delta = 0
        self.button_dict = {}
        self.button_list = []
        self.last_button = None

        # Gameplay interactions
        self.use_function = None
        self.mode = None

    def create_window(self, window_size):
        return pygame.display.set_mode(window_size)

    def define_fonts(self):
        font_base = {}
        font_base['basic'] = pygame.font.SysFont('dejavusansmono', 20)
        return font_base

    def create_slot_buttons(self):
        for player in self.player_list:
            self.button_dict[player] = {}
            for token in player.mech_list:
                self.button_dict[player][token] = {}
                i = 0
                for slot in token.mech.slots:
                    item_slot = token.mech.slots[slot]
                    if item_slot:
                        self.button_dict[player][token][slot] = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((680, 220+i*36),
                                                                                             (200, 30)),
                                                                                             text=item_slot.name,
                                                                                             manager=self.ui_manager,
                                                                                             tool_tip_text=item_slot.create_tooltip(),
                                                                                             visible=0)
                        self.button_list.append(self.button_dict[player][token][slot])
                        i += 1
                        
    def button_pressed(self, button):
        if self.last_button:
            # Unpress the old button
            self.show_movement_range(True)
            self.last_button._set_inactive()
            # Unpress the clicked button
            if self.last_button == button:
                self.last_button = None
                self.hexmap_object.show_los = False
                self.show_visibility(False)
                self.use_function = None
                return

        if button:
            # Set button state to pressed
            self.show_movement_range(False)
            button._set_active()
            # Use the chosen module
            for player in self.player_list:
                for token in self.button_dict[player]:
                    for slot in self.button_dict[player][token]:
                        if button == self.button_dict[player][token][slot]:
                            item_slot = token.mech.slots[slot]
                            # here should go the entire logic behind ranges and targeting
                            self.hexmap_object.show_los = True
                            self.show_visibility(True)
                            self.use_function = item_slot.use

        self.last_button = button
        return

    def change_mode(self, mode):
        if self.mode != mode:
            self.mode = mode
        print('mode:', self.mode)

    def show_visibility(self, toggle):
        if toggle and self.hexmap_object.chosen_hex:
            for hex_cell in self.hexmap_object.hexmap:
                has_los, _ = self.hexmap_object.check_line_of_sight(hex_cell,
                                                                self.hexmap_object.chosen_hex)
                hex_cell.has_los = has_los
            self.change_mode('targeting')
        else:
            for hex_cell in self.hexmap_object.hexmap:
                hex_cell.has_los = False
            self.change_mode(None)

    def show_movement_range(self, toggle):
        if not self.hexmap_object.chosen_hex.token:
            self.change_mode(None)
            return False
        elif not self.hexmap_object.chosen_hex.token.mech:
            self.change_mode(None)
            return False
        
        if toggle and self.hexmap_object.chosen_hex:
            old = time.time()
            for hex_cell in self.hexmap_object.hexmap:
                if hex_geometry.cube_distance(self.hexmap_object.chosen_hex.cube_id, hex_cell.cube_id) > self.hexmap_object.chosen_hex.token.mech.remaining_mv:
                    continue
                move_path = self.hexmap_object.astar_pathfinding(self.hexmap_object.chosen_hex, hex_cell)
                print(len(move_path), self.hexmap_object.chosen_hex.token.mech.remaining_mv)
                if len(move_path) - 1 <= self.hexmap_object.chosen_hex.token.mech.remaining_mv:
                    hex_cell.has_mv = bool(move_path)
            print('time:', time.time() - old)
            self.change_mode('movement')
        else:
            for hex_cell in self.hexmap_object.hexmap:
                hex_cell.has_mv = False
            self.change_mode(None)
        return True


    def move_token(self, start, end):
        # check current mode
        if self.mode != 'movement':
            return False
        # check remain movement
        remaining_movement = start.token.mech.remaining_mv
        if remaining_movement == 0:
            return False
        # calc pathfind
        path = self.hexmap_object.astar_pathfinding(start, end)[1:]
        # crop path
        if len(path) > remaining_movement:
            path = path[:remaining_movement]
        # maybe calculate some traps and stuff
        pass
        # move token
        start.token.mech.remaining_mv -= len(path)
        print(start.token.mech.remaining_mv)
        start.token.move(path[-1])
        return True

    def unclick_mech(self):
        self.show_visibility(False)
        self.show_movement_range(False)
        self.button_pressed(None)
        self.hexmap_object.chosen_hex = None

    def new_turn(self):
        self.current_player_list = copy.copy(self.player_list)
        for player in self.player_list:
            player.energy += player.energy_per_turn
        self.turn += 1

    def run(self):
        self.time_delta = self.clock.tick(60)/1000.0
        
        # Mech loading (temp)
        squad_path = pathlib.Path('./squads/alpha_squad.sqd')
        mech_list = load_mechs.load_mech_list(squad_path)

        self.player_list[0].mech_list.append(hexmap.Token(self.screen, self.hexmap_object.hexmap[48], mech_list[0], self.player_list[0]))
        self.player_list[0].mech_list.append(hexmap.Token(self.screen, self.hexmap_object.hexmap[24], mech_list[1], self.player_list[0]))
        self.player_list[1].mech_list.append(hexmap.Token(self.screen, self.hexmap_object.hexmap[27], mech_list[2], self.player_list[1]))

        for player in self.player_list:
            player.update_params()

        self.create_slot_buttons()

        # Rock placing
        rock_range = [(0, 0), (0, 1), (2, 1), (3, -3), (-3, -1), (-1, -3),
                    (-4, 3), (-4, 3), (-4, 4), (-3, 4), (-2, 4), (-2, 5),
                    (4, -2), (0, -4), (3, 1), (2, 2), (2, 3), (-1, 2), (-2, 4)]

        for coords in rock_range:
            if not self.hexmap_object.get_tile_from_axial(hex_geometry.Axial(*coords)).token:
                hexmap.Rock(self.screen, self.hexmap_object.get_tile_from_axial(hex_geometry.Axial(*coords)))
                print(f'Putting Rocks at {coords}.')
            else:
                print(f'Putting Rocks failed: {coords} is already taken.')

        pygame.display.flip() # paint screen one time
                
        running = True
        hover_text = ''
        while running:
            # Screen reset
            self.screen.blit(self.background, (0, 0))
            self.hexmap_object.reset()

            ################## START OF EVENT LOGIC ###################################
            ###########################################################################
            for event in pygame.event.get():

                # Quit the game if event is "quit"
                if event.type == pygame.QUIT:
                    running = False
                
                # Mouse hover highlight
                if event.type == pygame.MOUSEMOTION:
                    x, y = event.pos
                    self.hexmap_object.hover = self.hexmap_object.check_position(x, y)
                
                # Mouse click
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    clicked_hex = self.hexmap_object.check_position(x, y)
                    if clicked_hex:
                        # If clicked hex_cell is already chosen, unclick it
                        if clicked_hex == self.hexmap_object.chosen_hex:
                            self.unclick_mech()
                        # If holding token, put it on an empty place
                        elif not clicked_hex.token and self.hexmap_object.chosen_hex:
                            if self.hexmap_object.chosen_hex.token:
                                # Check whether chosen token is owned by the current player
                                if self.hexmap_object.chosen_hex.token in self.current_player.mech_list:
                                    self.move_token(self.hexmap_object.chosen_hex, clicked_hex)
                                    # self.unclick_mech()
                                    self.hexmap_object.chosen_hex = clicked_hex
                                    self.show_movement_range(False)
                                    self.show_movement_range(True)
                                else:
                                    self.unclick_mech()
                            # If not holding token, pick cliked hex
                            else:
                                self.hexmap_object.chosen_hex = clicked_hex
                                self.show_visibility(False)
                                self.show_movement_range(True)
                        # If mech is chosen and and mech is clicked
                        elif clicked_hex.token and self.hexmap_object.chosen_hex:
                            if self.hexmap_object.chosen_hex.token:
                                if hasattr(clicked_hex.token, 'mech') and hasattr(self.hexmap_object.chosen_hex.token, 'mech'):
                                    # If you have your mech and click on enemy
                                    if self.hexmap_object.chosen_hex.token in self.current_player.mech_list and \
                                       clicked_hex.token not in self.current_player.mech_list:
                                        print('targeting!')
                                        if self.use_function:
                                            if not self.hexmap_object.chosen_hex.token.mech.has_acted:
                                                self.use_function(self.hexmap_object.chosen_hex.token.mech, clicked_hex.token.mech)
                                                self.hexmap_object.chosen_hex.token.mech.has_acted = True
                                            else:
                                                # TODO: something here
                                                pass
                                                # log
                                            self.button_pressed(self.last_button)
                        # If clicking on space with token, grab it
                        else:
                            self.hexmap_object.chosen_hex = clicked_hex
                            self.show_visibility(False)
                            self.show_movement_range(True)
                        self.hexmap_object.chosen_old = self.hexmap_object.chosen_hex
                        print('Clicked:', clicked_hex.axial_id)
                    self.hexmap_object.hover = clicked_hex


                # Keyboard interaction
                if event.type == pygame.KEYDOWN:
                    # Click "D" to pause game while debugging
                    if event.key == pygame.K_d:
                        pass
                    # Press Space to pass turn between players
                    if event.key == pygame.K_SPACE:
                        self.current_player = self.current_player_list.pop()
                        if not self.current_player_list:
                            self.new_turn()
                    # Show line of sight
                    if event.key == pygame.K_a:
                        self.hexmap_object.show_los = not self.hexmap_object.show_los

                # All UI button events
                if event.type == pygame.USEREVENT:
                    if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                        for button in self.button_list:
                            if event.ui_element == button:
                                self.button_pressed(event.ui_element)
                    if event.user_type == pygame_gui.UI_BUTTON_ON_UNHOVERED:
                        if event.ui_element == self.last_button:
                            self.last_button._set_active()
                
                self.ui_manager.process_events(event)
            #########################################################################
            ################## END OF EVENT LOGIC ###################################

            for button in self.button_list:
                button.visible = 0

            # Set text to print on side
            token = None
            if self.hexmap_object.hover:
                if self.hexmap_object.hover.token:
                    token = self.hexmap_object.hover.token
                elif self.hexmap_object.chosen_hex:
                    if self.hexmap_object.chosen_hex.token:
                        token = self.hexmap_object.chosen_hex.token
            elif self.hexmap_object.chosen_hex:
                if self.hexmap_object.chosen_hex.token:
                    token = self.hexmap_object.chosen_hex.token

            text_color = (200, 200, 200)
            if token:
                hover_text = f'{token.name}\n\n'
                if hasattr(token, 'player'):
                    text_color = token.player.color
                else:
                    text_color = (200, 200, 200)
                if hasattr(token, 'mech'):
                    mech = token.mech
                    hover_text += f'AM: {mech.current_hp}  EG: {mech.EG}  MV: {mech.MV}\n'
                    hover_text += f'Player\'s Energy: {token.player.energy}\n\n'
                    for slot in mech.slots:
                        if mech.slots[slot]:
                            self.button_dict[token.player][token][slot].visible = 1
                            # hover_text += f'{mech.slots[slot].name}\n'
            else:
                hover_text = ''

            # UI update step
            self.ui_manager.update(self.time_delta)
            self.ui_manager.draw_ui(self.screen)

            # Hexmap update
            self.hexmap_object.update()

            # Text display
            for i, line in enumerate(hover_text.splitlines()):
                if i == 0:
                    textsurface = self.font_base['basic'].render(line, False, text_color)
                else:
                    textsurface = self.font_base['basic'].render(line, False, (200, 200, 200))
                self.screen.blit(textsurface, (680, 100+i*24))
            player_text = self.font_base['basic'].render("Player: ", False, (200, 200, 200))
            self.screen.blit(player_text, (680, 560-24))
            player_text = self.font_base['basic'].render("Energy: ", False, (200, 200, 200))
            self.screen.blit(player_text, (680, 560))
            if self.current_player:
                player_text = self.font_base['basic'].render(self.current_player.name, False, self.current_player.color)
                self.screen.blit(player_text, (780, 560-24))
                player_text = self.font_base['basic'].render(f'{self.current_player.energy} (+{self.current_player.energy_per_turn})', False, (200, 200, 200))
                self.screen.blit(player_text, (780, 560))
            turn_text = self.font_base['basic'].render("  Turn: ", False, (200, 200, 200))
            self.screen.blit(turn_text, (680, 584))
            turn_text = self.font_base['basic'].render(str(self.turn), False, (200, 200, 200))
            self.screen.blit(turn_text, (780, 584))

            # Pygame update
            pygame.display.update()
            pygame.display.flip()

        pygame.quit()



def print_mech_data():
    pass


if __name__ == '__main__':
    first_player = Player('Brorys', (100, 100, 200))
    second_player = Player('Pitor', (200, 100, 100))
    game_player_list = [first_player, second_player]
    
    Game(None, game_player_list).run()
