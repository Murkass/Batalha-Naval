class Tabuleiro:
    def __init__(self, tamanho = 10):
        self.tamanho = tamanho
        self.navios = []
        self.atingidos = []
        self.clicados = []

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
            if resultado["status"]:
                self.atingidos.append(posicao)
                self.clicados.append(posicao)
                return {"hit": True, "sunk": navio.afundado}
        self.clicados.append(posicao)
        return {"hit": False, "sunk": False}
