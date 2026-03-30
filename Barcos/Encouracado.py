from .Navios import Navios

class Encouracado(Navios):
    def __init__(self, nome):
        super().__init__(4, nome)