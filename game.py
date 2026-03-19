from pygame import *

# Inicializar pygame
init()

# Configurações da tela
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
display.set_caption("Batalha Naval")

# Cor de fundo
BLACK = (0, 0, 0)

# Game loop
running = True
clock = time.Clock()

while running:
    for evt in event.get():
        if evt.type == QUIT:
            running = False
    
    screen.fill(BLACK)
    display.flip()
    clock.tick(60)

quit()

