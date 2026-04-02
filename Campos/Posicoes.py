class posicoes:
    def __init__(self, linha: int, coluna: int):
        self.linha = linha
        self.coluna = coluna

    def __str__(self):
        return f"l {self.linha}, c {self.coluna}"
    
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
    

if __name__ == '__main__':
    p1 = posicoes(1, 2)
    p2 = posicoes(1, 2)

    p3 = posicoes(2, 1)
    p4 = posicoes(2, 1)

    ar1 = [p3, p1]
    ar2 = [p2, p4]

    ar1.sort(key=lambda x: (x.linha, x.coluna))
    ar2.sort(key=lambda x: (x.linha, x.coluna))

    print(ar1 == ar2)