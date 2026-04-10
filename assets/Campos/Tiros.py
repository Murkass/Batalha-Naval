from assets.Campos.Posicoes import posicoes

class tiros:
    def tiro_simples(self, posicao, tabuleiro):
        if not posicao.validade(tabuleiro): return "Posição inválida"
        return tabuleiro.registrar_tiro(posicao)
    
    def tiro_triplo(self, posicao1, posicao2, posicao3, tabuleiro):
        resultados = []
        for posicao in [posicao1, posicao2, posicao3]:
            if not posicao.validade(tabuleiro): 
                resultados.append("Posição inválida")
                continue
            resultados.append(tabuleiro.registrar_tiro(posicao))
        return resultados
    
    def tiro_cruz(self, posicao, tabuleiro):
        resultados = []
        direcoes = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]
        for d in direcoes:
            nova_posicao = posicoes(posicao.linha + d[0], posicao.coluna + d[1])
            if not nova_posicao.validade(tabuleiro): 
                resultados.append("Posição inválida")
                continue
            resultados.append(tabuleiro.registrar_tiro(nova_posicao))
        return resultados
    
    def tiro_bomba(self, posicao, tabuleiro):
        resultados = []
        direcoes = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for d in direcoes:
            nova_posicao = posicoes(posicao.linha + d[0], posicao.coluna + d[1])
            if not nova_posicao.validade(tabuleiro): 
                resultados.append("Posição inválida")
                continue
            resultados.append(tabuleiro.registrar_tiro(nova_posicao))
        return resultados