class posicoes:
    def __init__(self, linha: int, coluna: int):
        self.linha = linha
        self.coluna = coluna

    def __str__(self):
        return f"Linha: {self.linha}, Coluna: {self.coluna}"
    
    def __eq__(self, other):
        if not isinstance(other, posicoes):
            return False
        return self.linha == other.linha and self.coluna == other.coluna
    
    def __hash__(self):
        return hash((self.linha, self.coluna))

    def validade(self, tabuleiro):
        if((self.linha < 0 or self.linha >= tabuleiro.tamanho )or (self.coluna < 0 or self.coluna >= tabuleiro.tamanho)):
            return False
        if self in tabuleiro.atingidos:
              return False
        for navio in tabuleiro.navios:
            if self in navio.posicoes:
                return False
        return True
    
    def indices(self):
        return {"l": self.linha, "c": self.coluna}
    

if __name__ == '__main__':
    posicao1 = posicoes(1, 2)

    print(posicao1.__str__())