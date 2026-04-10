from assets.Barcos.Cruzador import cruzador
from assets.Barcos.Destroyer import destroyer
from assets.Barcos.Encouracado import Encouracado
from assets.Barcos.Portaavioes import portaavioes
from assets.Barcos.Submarino import submarino

# Tela
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
WINDOW_TITLE = "Batalha Naval"
FPS = 60

# Cores
COLORS = {
    "BLACK": (0, 0, 0),
    "WHITE": (255, 255, 255),
    "BLUE": (0, 100, 200),
    "LIGHT_BLUE": (173, 216, 230),
    "RED": (255, 0, 0),
    "DARK_RED": (139, 0, 0),
    "GRAY": (100, 100, 100),
    "GREEN": (0, 200, 0),
    "YELLOW": (255, 255, 0),
    "ORANGE": (255, 165, 0),
    "CYAN": (0, 255, 255),
    "DARK_BLUE": (10, 30, 80),
    "NAVY": (30, 60, 120),
    "DARK_GRAY": (50, 50, 50),
    "SHIP_GRAY": (120, 120, 130),
    "SHIP_DARK": (80, 80, 90),
    "FIRE_ORANGE": (255, 69, 0),
    "GOLD": (255, 215, 0),
    "PURPLE": (128, 0, 128),
    "LIGHT_GRAY": (200, 200, 200),
    "WATER_BLUE": (64, 164, 223),
}

BLACK = COLORS["BLACK"]
WHITE = COLORS["WHITE"]
BLUE = COLORS["BLUE"]
LIGHT_BLUE = COLORS["LIGHT_BLUE"]
RED = COLORS["RED"]
DARK_RED = COLORS["DARK_RED"]
GRAY = COLORS["GRAY"]
GREEN = COLORS["GREEN"]
YELLOW = COLORS["YELLOW"]
ORANGE = COLORS["ORANGE"]
CYAN = COLORS["CYAN"]
DARK_BLUE = COLORS["DARK_BLUE"]
NAVY = COLORS["NAVY"]
DARK_GRAY = COLORS["DARK_GRAY"]
SHIP_GRAY = COLORS["SHIP_GRAY"]
SHIP_DARK = COLORS["SHIP_DARK"]
FIRE_ORANGE = COLORS["FIRE_ORANGE"]
GOLD = COLORS["GOLD"]
PURPLE = COLORS["PURPLE"]
LIGHT_GRAY = COLORS["LIGHT_GRAY"]
WATER_BLUE = COLORS["WATER_BLUE"]

# Tabuleiro
TAMANHO_GRADE = 10
CELL_SIZE = 40
PADDING_BOARD = 20
PADDING_LEFT_JOGADOR = 20
PADDING_LEFT_MAQUINA = 590
PADDING_TOP = 90
BOARD_WIDTH = TAMANHO_GRADE * CELL_SIZE + 2
BOARD_HEIGHT = TAMANHO_GRADE * CELL_SIZE + 2

# Painel lateral de armas (tela de jogo)
PAINEL_ARMAS_X = 1055
PAINEL_ARMAS_W = 135

# Fluxo de jogo
TEMPO_ESPERA_INICIO = 3
TEMPO_ENTRE_TURNOS = 2

# Definicao dos navios
NAVIOS_TIPOS = [
    {"nome": "Destroyer", "tamanho": 1, "classe": destroyer},
    {"nome": "Submarino", "tamanho": 2, "classe": submarino},
    {"nome": "Cruzador", "tamanho": 3, "classe": cruzador},
    {"nome": "Encouracado", "tamanho": 4, "classe": Encouracado},
    {"nome": "Portaavioes", "tamanho": 5, "classe": portaavioes},
]
