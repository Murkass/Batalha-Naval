import pygame as pg
from src.config import COLORS

class Botao:
    def __init__(self, x, y, width, height, texto, cor):
        self.rect = pg.Rect(x, y, width, height)
        self.texto = texto
        self.cor = cor
        self.cor_hover = (
            min(cor[0] + 40, 255),
            min(cor[1] + 40, 255),
            min(cor[2] + 40, 255),
        )
        self.cor_sombra = (20, 20, 20)
        self.is_hover = False

    def desenhar(self, screen, fonte):
        cor = self.cor_hover if self.is_hover else self.cor
        
        # Desenhar sombra
        sombra_rect = self.rect.copy()
        sombra_rect.x += 4
        sombra_rect.y += 4
        pg.draw.rect(screen, self.cor_sombra, sombra_rect, border_radius=10)
        
        # Desenhar botão preenchido
        pg.draw.rect(screen, cor, self.rect, border_radius=10)
        
        # Desenhar borda
        cor_borda = COLORS["WHITE"] if self.is_hover else (200, 200, 200)
        pg.draw.rect(screen, cor_borda, self.rect, 3, border_radius=10)
        
        # Desenhar texto
        texto_render = fonte.render(self.texto, True, COLORS["WHITE"])
        texto_rect = texto_render.get_rect(center=self.rect.center)
        screen.blit(texto_render, texto_rect)

    def verificar_hover(self, mouse_pos):
        self.is_hover = self.rect.collidepoint(mouse_pos)

    def foi_clicado(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
