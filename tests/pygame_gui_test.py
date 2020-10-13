import pygame
import pygame_gui


pygame.init()

pygame.display.set_caption('Quick Start')
window_surface = pygame.display.set_mode((800, 600))

background = pygame.Surface((800, 600))
background.fill(pygame.Color('#000000'))

manager = pygame_gui.UIManager((800, 600))

hello_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)),
                                            text='Say Hello',
                                            manager=manager)
good_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 375), (100, 50)),
                                            text='Say Goodbye',
                                            manager=manager)

button_list = [good_button, hello_button]

clock = pygame.time.Clock()
is_running = True

clicked_button = None
old_button = None

while is_running:
    time_delta = clock.tick(60)/1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == hello_button:
                    clicked_button = hello_button
                    print('Hello World!')
                if event.ui_element == good_button:
                    clicked_button = good_button
                    print('Goodbye World!')
                update_call = True
                
            if event.user_type == pygame_gui.UI_BUTTON_ON_UNHOVERED:
                if event.ui_element == hello_button and clicked_button == hello_button:
                    hello_button._set_active()
                if event.ui_element == good_button and clicked_button == good_button:
                    good_button._set_active()

            # cliked_button.drawable_shape.set_active_state('hovered')

        manager.process_events(event)

    
    if clicked_button and update_call:
        for button in button_list:
            button._set_inactive()
        clicked_button._set_active()
        update_call = False

    manager.update(time_delta)

    window_surface.blit(background, (0, 0))
    manager.draw_ui(window_surface)

    pygame.display.update()