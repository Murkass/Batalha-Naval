import pygame as pg
import os

main_dir = os.path.split(os.path.abspath(__file__))[0]
def load_image(file):
    """loads an image, prepares it for play"""
    file = os.path.join(main_dir, "data", file)
    try:
        surface = pg.image.load(file)
    except pg.error:
        raise SystemExit(f'Could not load image "{file}" {pg.get_error()}')
    return surface.convert()

class boats(pg.sprite.Sprite):
    def __init__(self, name: str, size: int):
        self.name = name
        self.size = size
        self.state = 0 #0: intact, 1:hit, 2:sunk

    def update(self, state: int):
        if self.state == state:
            return
        self.state = state
        if self.state == 1:
            #TODO: logica para trocar a sprite para de um barco atingido
            pass
        elif self.state == 2:
            #TODO: logica trocar a sprite para de um barco afundado
            pass
        else:
            #TODO: logica para o estado inteiro do barco
            pass

class bomb(pg.sprite.Sprite):
    def __init__(self, position: tuple, type: str, qty: int):
        super().__init__()
        self.image = load_image("bomb.png") #TODO: criar a imagem da bomba
        self.rect = self.image.get_rect()
        self.rect.topleft = position
        self.type = type #TODO: definir os tipos de bombas (ex: bomba normal, bomba em área, bomba em sequencia, etc)
        self.qty = qty #TODO: definir a quantidade de bombas por tipo selecionado

    def use_bomb(self, position: tuple, type: str):
        if self.qty > 0 and self.type == type:
            self.qty -= 1
            #TODO: logica da bomba ser usada na posição e realizando a animação

            boats.update(1) #TODO: atualizar o estado do barco atingido para "hit" ou "sunk" dependendo da quantidade de acertos

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