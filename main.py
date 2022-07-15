import pygame

import env

environment = env.Environment()

running = True
pressed = False

if __name__ == "__main__":
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pressed = True
            elif event.type == pygame.MOUSEBUTTONUP:
                pressed = False

        mouse = pygame.mouse.get_pos()

        if pressed:
            # environment.add_mouse(mouse)
            pass

        # draw background
        environment.update()
        
        pygame.display.update()
        prev_mouse = mouse


    # environment.save()
    pygame.quit()
