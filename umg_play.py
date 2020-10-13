import pygame
import pygame_gui
import pathlib
from umg_game import hexmap, hex_geometry, load_mechs


class Player(object):
    def __init__(self, name, color=(100, 100, 200)):
        self.name = name
        self.turn = False
        self.energy = 0
        self.color = color


class Game(object):
    def __init__(self, hexmap_object, player_list, window_size=(1000, 640)):
        self.name = None
        self.hexmap_object = hexmap_object

        self.player_list = player_list
        self.current_player = player_list[0]
        self.player_list = [*player_list[1:], player_list[0]]

        pygame.init()
        pygame.font.init()
        self.clock = pygame.time.Clock()

        self.font_base = self.define_fonts()

        self.window_size = window_size

        # Pygame graphics
        self.screen = self.create_window(self.window_size)
        self.background = pygame.Surface(self.window_size)
        self.background.fill(pygame.Color('#000000'))

        # UI Initialization
        self.ui_manager = pygame_gui.UIManager(self.window_size)
        self.time_delta = 0
        self.button_list = []

    def create_window(self, window_size):
        return pygame.display.set_mode(window_size)

    def define_fonts(self):
        font_base = {}
        font_base['basic'] = pygame.font.SysFont('dejavusansmono', 20)
        return font_base

    def run(self):
        self.time_delta = self.clock.tick(60)/1000.0

        hexmap_object = hexmap.HexMap(self.screen)

        # Mech loading
        squad_path = pathlib.Path('./squads/alpha_squad.sqd')
        mech_list = load_mechs.load_mech_list(squad_path)

        hexmap.Token(self.screen, hexmap_object.hexmap[48], mech_list[0], first_player)
        hexmap.Token(self.screen, hexmap_object.hexmap[24], mech_list[1], first_player)
        hexmap.Token(self.screen, hexmap_object.hexmap[27], mech_list[2], second_player)
        
        # Rock placing
        rock_range = [(0, 0), (0, 1), (2, 1), (3, -3), (-3, -1), (-1, -3),
                    (-4, 3), (-4, 3), (-4, 4), (-3, 4), (-2, 4), (-2, 5),
                    (4, -2), (0, -4), (3, 1), (2, 2), (2, 3), (-1, 2), (-2, 4)]

        for coords in rock_range:
            if not hexmap_object.get_tile_from_axial(hex_geometry.Axial(*coords)).token:
                hexmap.Rock(self.screen, hexmap_object.get_tile_from_axial(hex_geometry.Axial(*coords)))
                print(f'Putting Rocks at {coords}.')
            else:
                print(f'Putting Rocks failed: {coords} is already taken.')

        pygame.display.flip() # paint screen one time
                
        running = True
        hover_text = ''


        
        ################## START OF EVENT LOOP ####################################
        ###########################################################################
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
                                    if hexmap_object.chosen_hex.token.player == self.current_player:
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
                        hexmap_object.chosen_old = hexmap_object.chosen_hex
                        print('Clicked:', clicked_hex.axial_id)
                    hexmap_object.hover = clicked_hex

                if event.type == pygame.KEYDOWN:
                    # Click "D" to pause game while debugging
                    if event.key == pygame.K_d:
                        # for button in button_list:
                            # button.visible = 1
                        pass
                    # Press Space to pass turn between players
                    if event.key == pygame.K_SPACE:
                        self.current_player = self.player_list[0]
                        self.player_list = [*self.player_list[1:], self.player_list[0]]
                    # Show visibility overlay
                    if event.key == pygame.K_v:
                        if hexmap_object.show_vis:
                            for hex_cell in hexmap_object.hexmap:
                                hex_cell.has_los = False
                            hexmap_object.show_vis = False
                        elif hexmap_object.chosen_hex:
                            for hex_cell in hexmap_object.hexmap:
                                has_los, _ = hexmap_object.check_line_of_sight(hex_cell, 
                                                                            hexmap_object.chosen_hex)
                                hex_cell.has_los = has_los
                                hexmap_object.show_vis = True
                        else:
                            hexmap_object.show_vis = False
                    # Show line of sight
                    if event.key == pygame.K_a:
                        hexmap_object.show_los = not hexmap_object.show_los

                if event.type == pygame.USEREVENT:
                    if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                        print('userevent')
                        for button in self.button_list:
                            print(self.button_list)
                            if event.ui_element == button:
                                print('Hello World!')
                                button.visible = 0
                
                self.ui_manager.process_events(event)
            #########################################################################
            ################## END OF EVENT LOOP ####################################

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
            self.screen.fill(pygame.Color("black"))

            # UI update step
            if not self.button_list:
                hello_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((640, 75),
                                                                                (100, 50)),
                                                        text='Say Hello',
                                                        manager=self.ui_manager,
                                                        tool_tip_text='Hello <b>world</b> from: Me!')
                self.button_list.append(hello_button)

            self.ui_manager.update(self.time_delta)
            self.screen.blit(self.background, (0, 0))
            self.ui_manager.draw_ui(self.screen)

            # Hexmap update
            hexmap_object.update()

            # Text display
            for i, line in enumerate(hover_text.splitlines()):
                textsurface = self.font_base['basic'].render(line, False, text_color)
                self.screen.blit(textsurface, (680, 200+i*24))
            player_text = self.font_base['basic'].render("Player: ", False, (200, 200, 200))
            self.screen.blit(player_text, (680, 460))
            if self.current_player:
                player_text = self.font_base['basic'].render(self.current_player.name, False, self.current_player.color)
                self.screen.blit(player_text, (780, 460))

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
