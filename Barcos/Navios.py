class Navios:
    def __init__(self, tamanho: int, nome: str):
        self.tamanho = tamanho
        self.nome = nome
        self.posicoes = []
        self.atingidos = []
        self.afundado = False

    def posicionar(self, posicoes: list):
        self.posicoes = posicoes
        
    def acertado(self, posicao):
        if posicao in self.posicoes:
            self.atingidos.append(posicao)
            if(self.afundou()): return f"Navio {self.nome} afundou"
            return f"Navio {self.nome} atingido na posição: {posicao.__str__()}"
        return False
    
    def afundou(self):
        if( self.acertado == self.posicoes):
            self.afundado = True
        return self.afundado



if __name__ == '__main__':
    teste = [1, 2, 3]
    teste2 = [1, 2, 3]

    print(teste == teste2)