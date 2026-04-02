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
            self.atingidos.sort(key=lambda x: (x.linha, x.coluna))
            self.atingidos.append(posicao)
            if(self.afundou()): return {"status": True, "message": f"Navio {self.nome} afundou"}
            return {"status": True, "message":f"Navio {self.nome} atingido na posição: {posicao.__str__()}"}
        return {"status": False, "message":f"Não Atingido"}
    
    def afundou(self):
        self.posicoes.sort(key=lambda x: (x.linha, x.coluna))
        if( self.atingidos == self.posicoes):
            self.afundado = True
        return self.afundado



if __name__ == '__main__':
    teste = [2, 1, 3]
    teste2 = [1, 2, 3]

    print(teste == teste2)