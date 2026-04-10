"""
Módulo de IA avançada para Batalha Naval
Implementa estratégias inteligentes de ataque
"""
import random
from assets.Campos import posicoes


class IAAvancada:
    """IA inteligente para o jogo de Batalha Naval"""
    
    def __init__(self, tamanho_grade=10):
        self.tamanho_grade = tamanho_grade
        self.modo_caca = False  # Modo de caça ativado quando acerta um navio
        self.ultima_posicao_acerto = None
        self.posicoes_para_investigar = []  # Fila de posições adjacentes para investigar
        self.direcao_ataque = None  # Direção do ataque quando encontra sequência
        self.historico_acertos = []  # Histórico de acertos no navio atual
        
    def _obter_adjacentes(self, pos):
        """Retorna posições adjacentes válidas (cima, baixo, esquerda, direita)"""
        adjacentes = []
        direcoes = [
            (-1, 0),  # cima
            (1, 0),   # baixo
            (0, -1),  # esquerda
            (0, 1)    # direita
        ]
        
        for dx, dy in direcoes:
            nova_linha = pos.linha + dx
            nova_coluna = pos.coluna + dy
            if 0 <= nova_linha < self.tamanho_grade and 0 <= nova_coluna < self.tamanho_grade:
                adjacentes.append(posicoes(nova_linha, nova_coluna))
        
        return adjacentes
    
    def _calcular_probabilidades(self, tabuleiro):
        """Calcula probabilidades de posições com base em padrões"""
        probabilidades = {}
        
        for linha in range(self.tamanho_grade):
            for coluna in range(self.tamanho_grade):
                pos = posicoes(linha, coluna)
                if pos not in tabuleiro.clicados:
                    # Pontuação base
                    score = 1
                    
                    # Aumenta pontuação se está próximo a acertos não afundados
                    for acerto in tabuleiro.atingidos:
                        # Verifica se a posição de acerto pertence a navio não afundado
                        navio_afundado = False
                        for navio in tabuleiro.navios:
                            if acerto in navio.posicoes and navio.afundado:
                                navio_afundado = True
                                break
                        
                        if not navio_afundado:
                            dist = abs(pos.linha - acerto.linha) + abs(pos.coluna - acerto.coluna)
                            if dist == 1:
                                score += 50  # Adjacente a acerto
                            elif dist == 2:
                                score += 10  # Próximo a acerto
                    
                    # Padrão de tabuleiro de xadrez (estatisticamente melhor)
                    if (linha + coluna) % 2 == 0:
                        score += 2
                    
                    probabilidades[pos] = score
        
        return probabilidades
    
    def escolher_posicao(self, tabuleiro):
        """
        Escolhe a melhor posição para atacar
        
        Args:
            tabuleiro: Tabuleiro do jogador para analisar
            
        Returns:
            posicoes: Posição escolhida para o ataque
        """
        # Modo 1: Temos posições específicas para investigar (após um acerto)
        if self.posicoes_para_investigar:
            # Remove e retorna a próxima posição da fila
            while self.posicoes_para_investigar:
                pos = self.posicoes_para_investigar.pop(0)
                if pos not in tabuleiro.clicados:
                    return pos
        
        # Modo 2: Modo caça - acabamos de acertar algo
        if self.modo_caca and self.ultima_posicao_acerto:
            # Se temos direção definida (já acertamos 2+ vezes seguidas)
            if self.direcao_ataque and len(self.historico_acertos) >= 2:
                # Continua na mesma direção
                ultima = self.historico_acertos[-1]
                dx, dy = self.direcao_ataque
                proxima = posicoes(ultima.linha + dx, ultima.coluna + dy)
                
                if (0 <= proxima.linha < self.tamanho_grade and 
                    0 <= proxima.coluna < self.tamanho_grade and
                    proxima not in tabuleiro.clicados):
                    return proxima
                else:
                    # Se não pode continuar, tenta a direção oposta
                    primeira = self.historico_acertos[0]
                    proxima = posicoes(primeira.linha - dx, primeira.coluna - dy)
                    if (0 <= proxima.linha < self.tamanho_grade and 
                        0 <= proxima.coluna < self.tamanho_grade and
                        proxima not in tabuleiro.clicados):
                        return proxima
            
            # Adiciona posições adjacentes ao último acerto não exploradas
            adjacentes = self._obter_adjacentes(self.ultima_posicao_acerto)
            for pos in adjacentes:
                if pos not in tabuleiro.clicados and pos not in self.posicoes_para_investigar:
                    self.posicoes_para_investigar.append(pos)
            
            if self.posicoes_para_investigar:
                return self.posicoes_para_investigar.pop(0)
        
        # Modo 3: Ataque inteligente baseado em probabilidades
        probabilidades = self._calcular_probabilidades(tabuleiro)
        
        if probabilidades:
            # Escolhe a posição com maior probabilidade
            melhor_pos = max(probabilidades.items(), key=lambda x: x[1])[0]
            return melhor_pos
        
        # Modo 4: Fallback - escolha aleatória (improvável)
        while True:
            linha = random.randint(0, self.tamanho_grade - 1)
            coluna = random.randint(0, self.tamanho_grade - 1)
            pos = posicoes(linha, coluna)
            if pos not in tabuleiro.clicados:
                return pos
    
    def processar_resultado(self, pos, acertou, afundou):
        """
        Processa o resultado do último ataque para ajustar estratégia
        
        Args:
            pos: Posição atacada
            acertou: Se acertou um navio
            afundou: Se afundou o navio
        """
        if acertou:
            self.modo_caca = True
            self.ultima_posicao_acerto = pos
            self.historico_acertos.append(pos)
            
            # Se temos 2+ acertos, determina a direção
            if len(self.historico_acertos) >= 2:
                ultimo = self.historico_acertos[-1]
                penultimo = self.historico_acertos[-2]
                dx = ultimo.linha - penultimo.linha
                dy = ultimo.coluna - penultimo.coluna
                self.direcao_ataque = (dx, dy)
            
            if afundou:
                # Navio afundado - reseta modo caça
                self.modo_caca = False
                self.ultima_posicao_acerto = None
                self.posicoes_para_investigar.clear()
                self.direcao_ataque = None
                self.historico_acertos.clear()
        else:
            # Errou - não faz nada, continua com a estratégia atual
            pass
    
    def resetar(self):
        """Reseta o estado da IA para um novo jogo"""
        self.modo_caca = False
        self.ultima_posicao_acerto = None
        self.posicoes_para_investigar.clear()
        self.direcao_ataque = None
        self.historico_acertos.clear()
