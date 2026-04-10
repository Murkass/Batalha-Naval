from ._Navios import Navios

class portaavioes(Navios):
    def __init__(self, nome):
        super().__init__(5, nome)