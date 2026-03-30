from .Navios import Navios

class cruzador(Navios):
    def __init__(self, nome):
        super().__init__(3, nome)