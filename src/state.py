from enum import Enum, auto


class EstadoJogo(Enum):
    MENU = auto()
    POSICIONANDO_NAVIOS = auto()
    INICIANDO = auto()
    JOGANDO = auto()
    FINALIZADO = auto()
    ENCERRADO = auto()


class Turno(Enum):
    JOGADOR = auto()
    MAQUINA = auto()
