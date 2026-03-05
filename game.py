import pygame as pg
if __name__ == "__main__":
    
    pg.init()
    screen = pg.display.set_mode((800, 600))
    pg.display.set_caption("Batalha Naval")
    clock = pg.time.Clock()
    running = True

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        screen.fill((255, 255, 255))
        pg.display.flip()
        clock.tick(60)

    pg.quit()