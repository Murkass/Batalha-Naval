class Tabuleiro:
    def __init__(self, tamanho = 10):
        self.tamanho = tamanho
        self.navios = []
        self.atingidos = []

    def posicionar_navio(self, navio, posicoes: list):
        for each in posicoes:
            if not each.validade(self): 
                return False
        navio.posicionar(posicoes)
        self.navios.append(navio)
        return True
    
    def registrar_tiro(self, posicao):
        for navio in self.navios:
            resultado = navio.acertado(posicao)
            if resultado:
                self.atingidos.append(posicao)
                return resultado
        return "Tiro na água"
