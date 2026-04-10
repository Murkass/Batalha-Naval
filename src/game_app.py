import random
import math

import pygame as pg

from assets.Campos     import *
from assets.Barcos     import *
from assets.attributes import *

from .config import *
from .state import EstadoJogo, Turno
from .ia import IAAvancada

class BatalhaNavalGame:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption(WINDOW_TITLE)
        self.clock = pg.time.Clock()

        self.botao_facil = Botao(SCREEN_WIDTH // 2 - 100, 230, 200, 50, "Facil", NAVY)
        self.botao_medio = Botao(SCREEN_WIDTH // 2 - 100, 300, 200, 50, "Medio", ORANGE)
        self.botao_dificil = Botao(SCREEN_WIDTH // 2 - 100, 370, 200, 50, "Dificil", DARK_RED)
        self.botao_sair = Botao(SCREEN_WIDTH // 2 - 100, 440, 200, 50, "Sair", RED)
        
        # Botões de fim de jogo
        self.botao_recomecar = Botao(SCREEN_WIDTH // 2 - 100, 350, 200, 50, "Recomecar", GREEN)
        self.botao_menu = Botao(SCREEN_WIDTH // 2 - 100, 420, 200, 50, "Menu", NAVY)
        
        # Sistema de notificação
        self.mensagem_narrador = ""
        self.tipo_mensagem = "info"  # info, acerto, erro, agua, afundou
        self.tempo_mensagem = 0
        
        # Efeitos visuais
        self.particulas_explosao = []

        self._resetar_partida()

    def _resetar_partida(self):
        self.estado_jogo = EstadoJogo.MENU
        self.turno = Turno.JOGADOR
        self.dificuldade = None
        self.tempo_espera_inicio = 0
        self.tempo_turno_inicio = 0

        self.tabuleiro_jogador = Tabuleiro(tamanho=TAMANHO_GRADE)
        self.tabuleiro_maquina = Tabuleiro(tamanho=TAMANHO_GRADE)

        self.indice_navio_atual = 0
        self.navios_jogador = []
        self.navios_maquina = []
        self.orientacao_navio = "horizontal"

        self.notificacao = ""
        
        # IA avançada
        self.ia = IAAvancada(TAMANHO_GRADE)
        
        # Sistema de narrador
        self.mensagem_narrador = ""
        self.tipo_mensagem = "info"
        self.tempo_mensagem = 0
        
        # Efeitos visuais
        self.particulas_explosao = []
        
        # Vencedor
        self.vencedor = None
        
        self.armas = [
            {"nome": "Torpedo",    "icone": "T", "munição": -1,  "area": [(0, 0)],
             "desc": "1 célula",   "cor": (80, 190, 255)},
            {"nome": "Bomba-Cruz", "icone": "B", "munição":  3,  "area": [(0,0),(0,1),(0,-1),(1,0),(-1,0)],
             "desc": "Cruz (5)",   "cor": (255, 160, 40)},
            {"nome": "Salvo 3x3",  "icone": "S", "munição":  1,  "area": [
                (-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)],
             "desc": "3x3 (9)",    "cor": (220, 60, 220)},
        ]
        self.arma_atual = 0
        
        self.armas_ia = [
            {"nome": "Torpedo",    "munição": -1, "area": [(0, 0)]},
            {"nome": "Bomba-Cruz", "munição":  3, "area": [(0,0),(0,1),(0,-1),(1,0),(-1,0)]},
            {"nome": "Salvo 3x3",  "munição":  1, "area": [
                (-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]},
        ]

    def _set_notificacao(self, texto):
        self.notificacao = texto
    
    def _set_mensagem_narrador(self, mensagem, tipo="info"):
        """Define mensagem do narrador com tipo (info, acerto, erro, agua, afundou)"""
        self.mensagem_narrador = mensagem
        self.tipo_mensagem = tipo
        self.tempo_mensagem = pg.time.get_ticks()
    
    def _criar_particulas_explosao(self, x, y):
        """Cria partículas de explosão em uma posição"""
        for _ in range(15):
            angulo = random.uniform(0, 2 * math.pi)
            velocidade = random.uniform(2, 6)
            particula = {
                'x': x,
                'y': y,
                'vx': math.cos(angulo) * velocidade,
                'vy': math.sin(angulo) * velocidade,
                'vida': random.randint(20, 40),
                'cor': random.choice([RED, FIRE_ORANGE, YELLOW, ORANGE])
            }
            self.particulas_explosao.append(particula)

    def _obter_celula_do_mouse_tabuleiro(self, mouse_pos, x_inicio, y_inicio):
        x, y = mouse_pos
        if x_inicio <= x < x_inicio + BOARD_WIDTH and y_inicio <= y < y_inicio + BOARD_HEIGHT:
            coluna = (x - x_inicio) // CELL_SIZE
            linha = (y - y_inicio) // CELL_SIZE
            if 0 <= linha < TAMANHO_GRADE and 0 <= coluna < TAMANHO_GRADE:
                return linha, coluna
        return None

    def _obter_posicoes_navio(self, linha, coluna, tamanho, orientacao):
        posicoes_navio = []
        if orientacao == "horizontal":
            for i in range(tamanho):
                if coluna + i >= TAMANHO_GRADE:
                    return None
                posicoes_navio.append(posicoes(linha, coluna + i))
        else:
            for i in range(tamanho):
                if linha + i >= TAMANHO_GRADE:
                    return None
                posicoes_navio.append(posicoes(linha + i, coluna))
        return posicoes_navio

    def _verificar_posicoes_validas(self, pos_list, tabuleiro):
        for pos in pos_list:
            if pos in tabuleiro.atingidos:
                return False
            for navio in tabuleiro.navios:
                if pos in navio.posicoes:
                    return False
        return True

    def _posicionar_navio_jogador(self, linha, coluna):
        if self.indice_navio_atual >= len(NAVIOS_TIPOS):
            return False

        navio_info = NAVIOS_TIPOS[self.indice_navio_atual]
        pos_navio = self._obter_posicoes_navio(
            linha,
            coluna,
            navio_info["tamanho"],
            self.orientacao_navio,
        )

        if pos_navio is None or not self._verificar_posicoes_validas(pos_navio, self.tabuleiro_jogador):
            self._set_notificacao(f"Posicao invalida para {navio_info['nome']}")
            return False

        novo_navio = navio_info["classe"](navio_info["nome"])
        self.tabuleiro_jogador.posicionar_navio(novo_navio, pos_navio)
        self.navios_jogador.append(novo_navio)
        self.indice_navio_atual += 1
        self._set_notificacao(f"{navio_info['nome']} posicionado")
        return True

    def _posicionar_navios_maquina(self):
        for navio_info in NAVIOS_TIPOS:
            posicionado = False
            tentativas = 0
            while not posicionado and tentativas < 100:
                linha = random.randint(0, TAMANHO_GRADE - 1)
                coluna = random.randint(0, TAMANHO_GRADE - 1)
                orientacao = random.choice(["horizontal", "vertical"])
                pos_navio = self._obter_posicoes_navio(
                    linha,
                    coluna,
                    navio_info["tamanho"],
                    orientacao,
                )
                if pos_navio and self._verificar_posicoes_validas(pos_navio, self.tabuleiro_maquina):
                    novo_navio = navio_info["classe"](navio_info["nome"])
                    self.tabuleiro_maquina.posicionar_navio(novo_navio, pos_navio)
                    self.navios_maquina.append(novo_navio)
                    posicionado = True
                tentativas += 1

    def _ia_escolher_arma(self, pos_centro):
        """Escolhe qual arma a IA vai usar baseado na dificuldade e situação"""
        bomba = self.armas_ia[1]
        salvo = self.armas_ia[2]
        em_caca = self.ia.modo_caca if self.dificuldade == "dificil" else False

        if self.dificuldade == "facil":
            return self.armas_ia[0]  # só torpedo

        elif self.dificuldade == "medio":
            # Médio: usa armas fora do modo caça com chance razoável
            if not em_caca:
                r = random.random()
                if r < 0.25 and salvo["munição"] != 0:
                    return salvo
                elif r < 0.50 and bomba["munição"] != 0:
                    return bomba
            return self.armas_ia[0]

        else:  # difícil
            # Difícil: em modo caça usa torpedo p/ precisão;
            # fora do modo caça prefere armas de área agressivamente
            if em_caca:
                return self.armas_ia[0]
            r = random.random()
            if r < 0.35 and salvo["munição"] != 0:
                return salvo
            elif r < 0.70 and bomba["munição"] != 0:
                return bomba
            return self.armas_ia[0]

    def _jogar_maquina(self):
        """IA da máquina faz um tiro usando o sistema de armas"""
        # ── 1. Escolhe a posição central da IA ────────────────────────────
        if self.dificuldade == "dificil":
            pos = self.ia.escolher_posicao(self.tabuleiro_jogador)
        elif self.dificuldade == "medio":
            if random.random() < 0.75:   # médio: usa IA 75% das vezes
                pos = self.ia.escolher_posicao(self.tabuleiro_jogador)
            else:
                acertos_recentes = [p for p in self.tabuleiro_jogador.atingidos
                                    if not any(p in navio.posicoes and navio.afundado
                                               for navio in self.tabuleiro_jogador.navios)]
                if acertos_recentes and random.random() < 0.6:
                    alvo = random.choice(acertos_recentes)
                    direcoes = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                    random.shuffle(direcoes)
                    pos = None
                    for dx, dy in direcoes:
                        nl, nc = alvo.linha + dx, alvo.coluna + dy
                        if 0 <= nl < TAMANHO_GRADE and 0 <= nc < TAMANHO_GRADE:
                            np_ = posicoes(nl, nc)
                            if np_ not in self.tabuleiro_jogador.clicados:
                                pos = np_
                                break
                    if pos is None:
                        while True:
                            pos = posicoes(random.randint(0, TAMANHO_GRADE - 1),
                                           random.randint(0, TAMANHO_GRADE - 1))
                            if pos not in self.tabuleiro_jogador.clicados:
                                break
                else:
                    while True:
                        pos = posicoes(random.randint(0, TAMANHO_GRADE - 1),
                                       random.randint(0, TAMANHO_GRADE - 1))
                        if pos not in self.tabuleiro_jogador.clicados:
                            break
        else:
            while True:
                pos = posicoes(random.randint(0, TAMANHO_GRADE - 1),
                               random.randint(0, TAMANHO_GRADE - 1))
                if pos not in self.tabuleiro_jogador.clicados:
                    break

        # ── 2. Escolhe a arma ─────────────────────────────────────────────
        arma = self._ia_escolher_arma(pos)

        # ── 3. Aplica área de impacto ─────────────────────────────────────
        acertou = False
        afundou = False
        primeiro_acerto_pos = pos  # para processar IA avançada
        for (dl, dc) in arma["area"]:
            al, ac = pos.linha + dl, pos.coluna + dc
            if 0 <= al < TAMANHO_GRADE and 0 <= ac < TAMANHO_GRADE:
                p_area = posicoes(al, ac)
                if p_area not in self.tabuleiro_jogador.clicados:
                    res = self.tabuleiro_jogador.registrar_tiro(p_area)
                    if res.get('sunk'):
                        afundou = True
                        acertou = True
                    elif res['hit']:
                        acertou = True
                        primeiro_acerto_pos = p_area
                    # Efeito visual
                    px = PADDING_LEFT_JOGADOR + 1 + ac * CELL_SIZE + CELL_SIZE // 2
                    py = PADDING_TOP + 1 + al * CELL_SIZE + CELL_SIZE // 2
                    if res['hit']:
                        self._criar_particulas_explosao(px, py)

        # ── 4. Desconta munição da IA ─────────────────────────────────────
        if arma["munição"] > 0:
            arma["munição"] -= 1

        # ── 5. Atualiza IA avançada (só no modo difícil) ──────────────────
        if self.dificuldade == "dificil":
            if arma is self.armas_ia[0]:
                # Torpedo: resultado direto na posição central
                self.ia.processar_resultado(pos, acertou, afundou)
            else:
                # Arma de área: informa o acerto mais relevante encontrado
                self.ia.processar_resultado(
                    primeiro_acerto_pos if acertou else pos,
                    acertou, afundou
                )

        # ── 6. Nome da arma para o narrador ───────────────────────────────
        nome_arma = f"[{arma['nome']}] " if arma is not self.armas_ia[0] else ""

        # ── 7. Mensagem do narrador ───────────────────────────────────────
        if afundou:
            self._set_mensagem_narrador(f"{nome_arma}AFUNDADO! A máquina destruiu seu navio!", "afundou")
        elif acertou:
            self._set_mensagem_narrador(f"{nome_arma}ACERTOU! A máquina atingiu seu navio!", "acerto")
        else:
            self._set_mensagem_narrador(f"{nome_arma}ÁGUA! A máquina errou o tiro.", "agua")

        # Verifica derrota imediata
        if self._todos_afundados(self.tabuleiro_jogador):
            self.vencedor = "maquina"
            self._set_mensagem_narrador("Derrota... A máquina venceu a batalha.", "erro")
            self.estado_jogo = EstadoJogo.FINALIZADO

    def _todos_afundados(self, tabuleiro):
        return bool(tabuleiro.navios) and all(navio.afundado for navio in tabuleiro.navios)

    def _desenhar_navio(self, x, y, tamanho, orientacao, afundado=False):
        """Desenha um navio com design melhorado"""
        if afundado:
            cor_principal = DARK_GRAY
            cor_borda = BLACK
        else:
            cor_principal = SHIP_GRAY
            cor_borda = SHIP_DARK
        
        if orientacao == "horizontal":
            # Corpo principal do navio
            corpo_rect = pg.Rect(x + 3, y + 8, tamanho * CELL_SIZE - 6, CELL_SIZE - 16)
            pg.draw.rect(self.screen, cor_principal, corpo_rect, border_radius=3)
            pg.draw.rect(self.screen, cor_borda, corpo_rect, 2, border_radius=3)
            
            # Proa (frente do navio - triângulo na direita)
            proa_points = [
                (x + tamanho * CELL_SIZE - 8, y + CELL_SIZE // 2),
                (x + tamanho * CELL_SIZE - 18, y + 10),
                (x + tamanho * CELL_SIZE - 18, y + CELL_SIZE - 10)
            ]
            pg.draw.polygon(self.screen, cor_principal, proa_points)
            pg.draw.polygon(self.screen, cor_borda, proa_points, 2)
            
            # Detalhes (janelas/portinholas)
            for i in range(tamanho):
                detalhe_x = x + 8 + i * CELL_SIZE
                detalhe_y = y + CELL_SIZE // 2 - 3
                pg.draw.circle(self.screen, cor_borda, (detalhe_x, detalhe_y), 2)
        else:  # vertical
            # Corpo principal do navio
            corpo_rect = pg.Rect(x + 8, y + 3, CELL_SIZE - 16, tamanho * CELL_SIZE - 6)
            pg.draw.rect(self.screen, cor_principal, corpo_rect, border_radius=3)
            pg.draw.rect(self.screen, cor_borda, corpo_rect, 2, border_radius=3)
            
            # Proa (frente do navio - triângulo na parte inferior)
            proa_points = [
                (x + CELL_SIZE // 2, y + tamanho * CELL_SIZE - 8),
                (x + 10, y + tamanho * CELL_SIZE - 18),
                (x + CELL_SIZE - 10, y + tamanho * CELL_SIZE - 18)
            ]
            pg.draw.polygon(self.screen, cor_principal, proa_points)
            pg.draw.polygon(self.screen, cor_borda, proa_points, 2)
            
            # Detalhes (janelas/portinholas)
            for i in range(tamanho):
                detalhe_x = x + CELL_SIZE // 2 - 3
                detalhe_y = y + 8 + i * CELL_SIZE
                pg.draw.circle(self.screen, cor_borda, (detalhe_x, detalhe_y), 2)

    def _desenhar_tabuleiro_base(self, x, y, tabuleiro, titulo, mostrar_navios):
        fonte_info = pg.font.SysFont(None, 24)
        titulo_texto = fonte_info.render(titulo, True, WHITE)
        self.screen.blit(titulo_texto, (x, y - 30))

        pg.draw.rect(self.screen, LIGHT_BLUE, (x, y, BOARD_WIDTH, BOARD_HEIGHT))
        for i in range(TAMANHO_GRADE + 1):
            linha_y = y + i * CELL_SIZE
            col_x = x + i * CELL_SIZE
            pg.draw.line(self.screen, BLACK, (x, linha_y), (x + BOARD_WIDTH - 2, linha_y), 1)
            pg.draw.line(self.screen, BLACK, (col_x, y), (col_x, y + BOARD_HEIGHT - 2), 1)

        if mostrar_navios:
            for navio in tabuleiro.navios:
                if navio.posicoes:
                    # Determinar orientação do navio
                    if len(navio.posicoes) > 1:
                        if navio.posicoes[0].linha == navio.posicoes[1].linha:
                            orientacao = "horizontal"
                        else:
                            orientacao = "vertical"
                    else:
                        orientacao = "horizontal"
                    
                    # Posição inicial do navio
                    primeira_pos = navio.posicoes[0]
                    px = x + 1 + primeira_pos.coluna * CELL_SIZE
                    py = y + 1 + primeira_pos.linha * CELL_SIZE
                    
                    # Desenhar o navio com o novo método
                    self._desenhar_navio(px, py, len(navio.posicoes), orientacao, navio.afundado)

        for p in tabuleiro.clicados:
            px = x + 1 + p.coluna * CELL_SIZE
            py = y + 1 + p.linha * CELL_SIZE
            centro_x = px + CELL_SIZE // 2
            centro_y = py + CELL_SIZE // 2
            
            if p in tabuleiro.atingidos:
                # Efeito de destruição - X vermelho grande com fogo
                pg.draw.line(self.screen, RED, (px + 8, py + 8), (px + CELL_SIZE - 8, py + CELL_SIZE - 8), 4)
                pg.draw.line(self.screen, RED, (px + CELL_SIZE - 8, py + 8), (px + 8, py + CELL_SIZE - 8), 4)
                
                # Círculo de explosão
                pg.draw.circle(self.screen, FIRE_ORANGE, (centro_x, centro_y), 12, 2)
                pg.draw.circle(self.screen, YELLOW, (centro_x, centro_y), 8, 2)
            else:
                # Tiro na água - círculo branco com ondas
                pg.draw.circle(self.screen, WHITE, (centro_x, centro_y), 6)
                pg.draw.circle(self.screen, WATER_BLUE, (centro_x, centro_y), 10, 2)

    def _desenhar_menu(self, mouse_pos):
        # Fundo gradiente simulado
        self.screen.fill(DARK_BLUE)
        for i in range(0, SCREEN_HEIGHT, 5):
            alpha = i / SCREEN_HEIGHT
            cor = (
                int(DARK_BLUE[0] + (BLACK[0] - DARK_BLUE[0]) * alpha),
                int(DARK_BLUE[1] + (BLACK[1] - DARK_BLUE[1]) * alpha),
                int(DARK_BLUE[2] + (BLACK[2] - DARK_BLUE[2]) * alpha),
            )
            pg.draw.rect(self.screen, cor, (0, i, SCREEN_WIDTH, 5))
        
        fonte_grande = pg.font.SysFont(None, 72)
        fonte_pequena = pg.font.SysFont(None, 36)
        fonte_subtitulo = pg.font.SysFont(None, 28)

        self.botao_facil.verificar_hover(mouse_pos)
        self.botao_medio.verificar_hover(mouse_pos)
        self.botao_dificil.verificar_hover(mouse_pos)
        self.botao_sair.verificar_hover(mouse_pos)

        # Título com sombra
        titulo = fonte_grande.render("BATALHA NAVAL", True, CYAN)
        titulo_sombra = fonte_grande.render("BATALHA NAVAL", True, DARK_GRAY)
        self.screen.blit(titulo_sombra, (SCREEN_WIDTH // 2 - titulo.get_width() // 2 + 3, 53))
        self.screen.blit(titulo, (SCREEN_WIDTH // 2 - titulo.get_width() // 2, 50))
        
        # Subtítulo
        instrucoes = fonte_subtitulo.render("Escolha a dificuldade", True, WHITE)
        self.screen.blit(instrucoes, (SCREEN_WIDTH // 2 - instrucoes.get_width() // 2, 160))        

        self.botao_facil.desenhar(self.screen, fonte_pequena)
        self.botao_medio.desenhar(self.screen, fonte_pequena)
        self.botao_dificil.desenhar(self.screen, fonte_pequena)
        self.botao_sair.desenhar(self.screen, fonte_pequena)

    def _desenhar_espera(self):
        self.screen.fill(BLACK)
        fonte_grande = pg.font.SysFont(None, 48)
        segundos_restantes = max(0, TEMPO_ESPERA_INICIO - self.tempo_espera_inicio // 1000)
        texto = fonte_grande.render(f"Partida iniciando em {segundos_restantes}s", True, WHITE)
        self.screen.blit(
            texto,
            (
                SCREEN_WIDTH // 2 - texto.get_width() // 2,
                SCREEN_HEIGHT // 2 - texto.get_height() // 2,
            ),
        )

    def _desenhar_posicionamento_navios(self):    
        COR_FUNDO_TOPO = (8, 20, 55)
        COR_FUNDO_BASE = (3, 8, 22)
        for i in range(SCREEN_HEIGHT):
            t = i / SCREEN_HEIGHT
            r = int(COR_FUNDO_TOPO[0] + (COR_FUNDO_BASE[0] - COR_FUNDO_TOPO[0]) * t)
            g = int(COR_FUNDO_TOPO[1] + (COR_FUNDO_BASE[1] - COR_FUNDO_TOPO[1]) * t)
            b = int(COR_FUNDO_TOPO[2] + (COR_FUNDO_BASE[2] - COR_FUNDO_TOPO[2]) * t)
            pg.draw.line(self.screen, (r, g, b), (0, i), (SCREEN_WIDTH, i))
        
        f_titulo   = pg.font.SysFont(None, 42)
        f_sub      = pg.font.SysFont(None, 22)
        f_sec      = pg.font.SysFont(None, 22)
        f_nome     = pg.font.SysFont(None, 26)
        f_badge    = pg.font.SysFont(None, 20)
        f_ctrl_key = pg.font.SysFont(None, 22)
        
        titulo = f_titulo.render("Posicionar Navios", True, WHITE)
        self.screen.blit(titulo, (PADDING_LEFT_JOGADOR, 18))

        dif_label = self.dificuldade.capitalize() if self.dificuldade else ""
        cores_dif = {"Facil": (100, 220, 100), "Medio": ORANGE, "Dificil": (255, 80, 80)}
        cor_dif = cores_dif.get(dif_label, LIGHT_GRAY)
        sub = f_sub.render(f"Dificuldade: {dif_label}", True, cor_dif)
        self.screen.blit(sub, (PADDING_LEFT_JOGADOR, 56))
        
        self._desenhar_tabuleiro_base(
            PADDING_LEFT_JOGADOR, PADDING_TOP,
            self.tabuleiro_jogador, "Seu Tabuleiro", True,
        )

        # ── Preview hover do navio ─────────────────────────────────────────
        mouse_pos = pg.mouse.get_pos()
        if self.indice_navio_atual < len(NAVIOS_TIPOS):
            celula = self._obter_celula_do_mouse_tabuleiro(
                mouse_pos, PADDING_LEFT_JOGADOR, PADDING_TOP
            )
            if celula:
                linha, coluna = celula
                navio_info = NAVIOS_TIPOS[self.indice_navio_atual]
                pos_navio = self._obter_posicoes_navio(
                    linha, coluna, navio_info["tamanho"], self.orientacao_navio
                )
                if pos_navio:
                    valido = self._verificar_posicoes_validas(pos_navio, self.tabuleiro_jogador)
                    cor_prev = (60, 220, 80, 110) if valido else (220, 50, 50, 110)
                    surf = pg.Surface((CELL_SIZE - 2, CELL_SIZE - 2), pg.SRCALPHA)
                    surf.fill(cor_prev)
                    for pos in pos_navio:
                        px = PADDING_LEFT_JOGADOR + 1 + pos.coluna * CELL_SIZE
                        py = PADDING_TOP + 1 + pos.linha * CELL_SIZE
                        self.screen.blit(surf, (px, py))
        
        PX = PADDING_LEFT_JOGADOR + BOARD_WIDTH + 48   # x = 500
        PY = 10
        PW = SCREEN_WIDTH - PX - 18                   # ≈ 682 px
        PH = SCREEN_HEIGHT - 20

        # Fundo
        panel_surf = pg.Surface((PW, PH), pg.SRCALPHA)
        panel_surf.fill((15, 28, 68, 210))
        self.screen.blit(panel_surf, (PX, PY))
        pg.draw.rect(self.screen, (45, 70, 140), pg.Rect(PX, PY, PW, PH), 2, border_radius=12)

        IX = PX + 20   
        IY = PY + 18   
        
        sec_frota = f_sec.render("FROTA DE COMBATE", True, (140, 165, 210))
        self.screen.blit(sec_frota, (IX, IY))
        pg.draw.line(self.screen, (45, 70, 140), (IX, IY + 22), (PX + PW - 20, IY + 22), 1)

        CARD_H   = 72
        CARD_GAP = 8
        CARD_W   = PW - 40        

        for idx, navio_info in enumerate(NAVIOS_TIPOS):
            cy = IY + 30 + idx * (CARD_H + CARD_GAP)
            card_rect = pg.Rect(IX, cy, CARD_W, CARD_H)

            if idx < len(self.navios_jogador):            # posicionado
                bg   = (15, 50, 22)
                bord = (50, 170, 70)
                cnome = (130, 230, 130)
                badge_txt = "OK"
                badge_cor = (60, 200, 80)
            elif idx == self.indice_navio_atual:           # atual
                bg   = (55, 42, 5)
                bord = (230, 185, 30)
                cnome = (255, 225, 80)
                badge_txt = "POSICIONAR"
                badge_cor = (240, 195, 40)
            else:                                          # aguardando
                bg   = (18, 28, 58)
                bord = (38, 55, 100)
                cnome = (85, 100, 145)
                badge_txt = "· · ·"
                badge_cor = (65, 80, 120)
            
            card_surf = pg.Surface((CARD_W, CARD_H), pg.SRCALPHA)
            card_surf.fill((*bg, 220))
            self.screen.blit(card_surf, (IX, cy))
            pg.draw.rect(self.screen, bord, card_rect, 2, border_radius=8)            
            
            nome_render = f_nome.render(navio_info["nome"], True, cnome)
            self.screen.blit(nome_render, (IX + 46, cy + 12))
            
            CL = 12   
            CG = 3    
            cells_w = navio_info["tamanho"] * (CL + CG) - CG
            cx0 = IX + 46
            cy_cells = cy + 36
            for ci in range(navio_info["tamanho"]):
                cell_x = cx0 + ci * (CL + CG)
                cor_cell = bord if idx >= len(self.navios_jogador) else (60, 200, 80)
                pg.draw.rect(self.screen, cor_cell,
                             pg.Rect(cell_x, cy_cells, CL, CL), border_radius=2)
            
            cells_label = f_badge.render(f"{navio_info['tamanho']} célula{'s' if navio_info['tamanho']>1 else ''}",
                                         True, badge_cor)
            self.screen.blit(cells_label, (IX + 46 + cells_w + 10, cy_cells))
            
            badge_render = f_badge.render(badge_txt, True, badge_cor)
            bx = IX + CARD_W - badge_render.get_width() - 14
            by = cy + CARD_H // 2 - badge_render.get_height() // 2
            self.screen.blit(badge_render, (bx, by))
        
        base_y = IY + 30 + len(NAVIOS_TIPOS) * (CARD_H + CARD_GAP) + 12

        if self.indice_navio_atual < len(NAVIOS_TIPOS):
            navio_info = NAVIOS_TIPOS[self.indice_navio_atual]

            atual_rect = pg.Rect(IX, base_y, CARD_W, 58)
            pg.draw.rect(self.screen, (50, 42, 5), atual_rect, border_radius=8)
            pg.draw.rect(self.screen, (230, 185, 30), atual_rect, 2, border_radius=8)

            txt_em = f_sec.render("EM JOGO:", True, (160, 140, 60))
            self.screen.blit(txt_em, (IX + 10, base_y + 8))

            txt_navio = f_nome.render(navio_info["nome"], True, (255, 225, 80))
            self.screen.blit(txt_navio, (IX + 90, base_y + 6))    

            base_y += 68
        
        pg.draw.line(self.screen, (45, 70, 140), (IX, base_y + 4), (PX + PW - 20, base_y + 4), 1)
        sec_ctrl = f_sec.render("CONTROLES", True, (140, 165, 210))
        self.screen.blit(sec_ctrl, (IX, base_y + 12))

        ctrl_y = base_y + 36
        
        def _draw_key(label, descricao, kx, ky):
            kb = pg.Rect(kx, ky, 90, 28)
            pg.draw.rect(self.screen, (30, 45, 90), kb, border_radius=5)
            pg.draw.rect(self.screen, (70, 100, 170), kb, 1, border_radius=5)
            k_txt = f_ctrl_key.render(label, True, WHITE)
            self.screen.blit(k_txt, (kx + kb.width // 2 - k_txt.get_width() // 2, ky + 5))
            desc = f_ctrl_key.render(descricao, True, (160, 175, 210))
            self.screen.blit(desc, (kx + 98, ky + 5))

        _draw_key("Clique", "Posicionar navio", IX, ctrl_y)
        _draw_key("  R", "Rotacionar", IX, ctrl_y + 36)

    def _desenhar_jogo(self):        
        COR_TOPO = (6, 18, 50)
        COR_BASE = (2, 7, 20)
        for i in range(SCREEN_HEIGHT):
            t = i / SCREEN_HEIGHT
            r = int(COR_TOPO[0] + (COR_BASE[0] - COR_TOPO[0]) * t)
            g = int(COR_TOPO[1] + (COR_BASE[1] - COR_TOPO[1]) * t)
            b = int(COR_TOPO[2] + (COR_BASE[2] - COR_TOPO[2]) * t)
            pg.draw.line(self.screen, (r, g, b), (0, i), (SCREEN_WIDTH, i))

        self._desenhar_tabuleiro_base(
            PADDING_LEFT_JOGADOR, PADDING_TOP,
            self.tabuleiro_jogador, "Seu tabuleiro", True,
        )
        self._desenhar_tabuleiro_base(
            PADDING_LEFT_MAQUINA, PADDING_TOP,
            self.tabuleiro_maquina, "Tabuleiro inimigo", False,
        )
        
        if self.turno == Turno.JOGADOR:
            mouse_pos = pg.mouse.get_pos()
            celula = self._obter_celula_do_mouse_tabuleiro(
                mouse_pos, PADDING_LEFT_MAQUINA, PADDING_TOP
            )
            if celula:
                hl, hc = celula
                arma = self.armas[self.arma_atual]
                surf_hover = pg.Surface((CELL_SIZE - 2, CELL_SIZE - 2), pg.SRCALPHA)
                for (dl, dc) in arma["area"]:
                    al, ac = hl + dl, hc + dc
                    if 0 <= al < TAMANHO_GRADE and 0 <= ac < TAMANHO_GRADE:
                        pos_test = posicoes(al, ac)
                        if pos_test in self.tabuleiro_maquina.clicados:
                            cor_h = (*DARK_GRAY, 90)
                        else:
                            cor_h = (*arma["cor"], 140)
                        surf_hover.fill(cor_h)
                        px = PADDING_LEFT_MAQUINA + 1 + ac * CELL_SIZE
                        py = PADDING_TOP + 1 + al * CELL_SIZE
                        self.screen.blit(surf_hover, (px, py))                
                cx = PADDING_LEFT_MAQUINA + 1 + hc * CELL_SIZE
                cy = PADDING_TOP + 1 + hl * CELL_SIZE
                pg.draw.rect(self.screen, arma["cor"],
                             pg.Rect(cx, cy, CELL_SIZE - 2, CELL_SIZE - 2), 2)
        
        mid_x = (PADDING_LEFT_JOGADOR + BOARD_WIDTH + PADDING_LEFT_MAQUINA) // 2
        fonte_turno = pg.font.SysFont(None, 34)
        fonte_tempo  = pg.font.SysFont(None, 26)
        tempo_restante = max(0, TEMPO_ENTRE_TURNOS - self.tempo_turno_inicio // 1000)

        if self.turno == Turno.JOGADOR:
            cor_turno  = (60, 220, 100)
            txt_turno  = "SUA VEZ"
        else:
            cor_turno  = ORANGE
            txt_turno  = "MAQUINA..."
        
        bar_w, bar_h = 160, 80
        bar_x = mid_x - bar_w // 2
        bar_y = PADDING_TOP + BOARD_HEIGHT // 2 - bar_h // 2
        bar_surf = pg.Surface((bar_w, bar_h), pg.SRCALPHA)
        bar_surf.fill((15, 28, 68, 210))
        self.screen.blit(bar_surf, (bar_x, bar_y))
        pg.draw.rect(self.screen, cor_turno, pg.Rect(bar_x, bar_y, bar_w, bar_h), 2, border_radius=10)

        t_surf = fonte_turno.render(txt_turno, True, cor_turno)
        self.screen.blit(t_surf, (mid_x - t_surf.get_width() // 2, bar_y + 10))

        txt_tempo = fonte_tempo.render(f"Tempo: {tempo_restante}s", True, YELLOW)
        self.screen.blit(txt_tempo, (mid_x - txt_tempo.get_width() // 2, bar_y + 46))
        
        self._desenhar_painel_armas()
        
        if self.mensagem_narrador:
            if pg.time.get_ticks() - self.tempo_mensagem < 4000:
                fonte_nar = pg.font.SysFont(None, 30)
                cores_tipo = {"acerto": RED, "agua": WATER_BLUE,
                              "afundou": FIRE_ORANGE, "info": CYAN}
                cor = cores_tipo.get(self.tipo_mensagem, WHITE)
                nar_y = SCREEN_HEIGHT - 72
                bg = pg.Rect(PADDING_LEFT_JOGADOR, nar_y - 8,
                             PAINEL_ARMAS_X - PADDING_LEFT_JOGADOR - 8, 52)
                pg.draw.rect(self.screen, NAVY, bg, border_radius=8)
                pg.draw.rect(self.screen, cor, bg, 2, border_radius=8)
                msg_s = fonte_nar.render(self.mensagem_narrador, True, WHITE)
                self.screen.blit(msg_s, (bg.x + 12, nar_y + 4))
        
        particulas_a_remover = []
        for particula in self.particulas_explosao:
            particula['x'] += particula['vx']
            particula['y'] += particula['vy']
            particula['vida'] -= 1
            if particula['vida'] <= 0:
                particulas_a_remover.append(particula)
            else:
                tamanho = max(1, int((particula['vida'] / 40) * 4))
                pg.draw.circle(self.screen, particula['cor'],
                               (int(particula['x']), int(particula['y'])), tamanho)
        for p in particulas_a_remover:
            self.particulas_explosao.remove(p)

    def _desenhar_painel_armas(self):        
        PX = PAINEL_ARMAS_X
        PY = PADDING_TOP - 10
        PW = PAINEL_ARMAS_W
        PH = BOARD_HEIGHT + 20
        
        ps = pg.Surface((PW, PH), pg.SRCALPHA)
        ps.fill((15, 28, 68, 215))
        self.screen.blit(ps, (PX, PY))
        pg.draw.rect(self.screen, (45, 70, 140),
                     pg.Rect(PX, PY, PW, PH), 2, border_radius=10)

        f_sec  = pg.font.SysFont(None, 19)
        f_nome = pg.font.SysFont(None, 22)
        f_muni = pg.font.SysFont(None, 19)

        sec = f_sec.render("ARSENAL", True, (140, 165, 210))
        self.screen.blit(sec, (PX + PW // 2 - sec.get_width() // 2, PY + 10))
        pg.draw.line(self.screen, (45, 70, 140),
                     (PX + 8, PY + 26), (PX + PW - 8, PY + 26), 1)

        CARD_H = 82
        CARD_G = 6
        IY = PY + 34

        for idx, arma in enumerate(self.armas):
            cy = IY + idx * (CARD_H + CARD_G)
            ativo = (idx == self.arma_atual)

            if ativo:
                bg_col = (40, 30, 70)
                brd    = arma["cor"]
            else:
                bg_col = (18, 26, 55)
                brd    = (40, 55, 100)

            c_surf = pg.Surface((PW - 8, CARD_H), pg.SRCALPHA)
            c_surf.fill((*bg_col, 220))
            self.screen.blit(c_surf, (PX + 4, cy))
            pg.draw.rect(self.screen, brd,
                         pg.Rect(PX + 4, cy, PW - 8, CARD_H), 2, border_radius=6)
            
            tec = f_muni.render(f"[{idx+1}]", True, (100, 120, 160) if not ativo else (200, 200, 255))
            self.screen.blit(tec, (PX + 10, cy + 6))
            
            f_icone = pg.font.SysFont(None, 30)
            ico_s = f_icone.render(arma["icone"], True, arma["cor"] if not ativo else WHITE)
            self.screen.blit(ico_s, (PX + PW // 2 - ico_s.get_width() // 2, cy + 6))
            
            nome_s = f_nome.render(arma["nome"], True,
                                   WHITE if ativo else (130, 145, 185))
            self.screen.blit(nome_s, (PX + PW // 2 - nome_s.get_width() // 2, cy + 32))
            
            if arma["munição"] == -1:
                muni_txt = "INF"
                cor_muni = (80, 200, 80)
            elif arma["munição"] > 0:
                muni_txt = f"x{arma['munição']}"
                cor_muni = YELLOW if arma["munição"] > 1 else RED
            else:
                muni_txt = "VAZIO"
                cor_muni = (90, 90, 90)

            muni_s = f_muni.render(muni_txt, True, cor_muni)
            self.screen.blit(muni_s, (PX + PW // 2 - muni_s.get_width() // 2, cy + 54))
            
            if ativo:
                pg.draw.circle(self.screen, arma["cor"],
                               (PX + PW - 12, cy + CARD_H // 2), 4)
        
        tip_y = IY + len(self.armas) * (CARD_H + CARD_G) + 6
        arma_sel = self.armas[self.arma_atual]
        desc_s = f_muni.render("Area: " + arma_sel["desc"], True, (120, 135, 175))
        self.screen.blit(desc_s, (PX + PW // 2 - desc_s.get_width() // 2, tip_y))
    
    def _desenhar_fim_jogo(self, mouse_pos):        
        superficie = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
        superficie.fill((0, 0, 0, 200))
        self.screen.blit(superficie, (0, 0))
        
        fonte_grande = pg.font.SysFont(None, 72)
        fonte_media = pg.font.SysFont(None, 48)
        fonte_pequena = pg.font.SysFont(None, 36)
        
        # Frame decorativo
        frame_rect = pg.Rect(SCREEN_WIDTH // 2 - 300, 150, 600, 400)
        pg.draw.rect(self.screen, NAVY, frame_rect, border_radius=20)
        pg.draw.rect(self.screen, GOLD, frame_rect, 5, border_radius=20)
        
        if self.vencedor == "jogador":
            titulo = fonte_grande.render("VITÓRIA!", True, GOLD)
            mensagem = fonte_media.render("Você derrotou a máquina!", True, GREEN)
        else:
            titulo = fonte_grande.render("DERROTA", True, RED)
            mensagem = fonte_media.render("A máquina venceu!", True, ORANGE)
        
        self.screen.blit(titulo, (SCREEN_WIDTH // 2 - titulo.get_width() // 2, 200))
        self.screen.blit(mensagem, (SCREEN_WIDTH // 2 - mensagem.get_width() // 2, 280))
        
        # Hover nos botões
        self.botao_recomecar.verificar_hover(mouse_pos)
        self.botao_menu.verificar_hover(mouse_pos)
        
        # Desenhar botões
        self.botao_recomecar.desenhar(self.screen, fonte_pequena)
        self.botao_menu.desenhar(self.screen, fonte_pequena)

    def _processar_eventos(self):
        for evt in pg.event.get():
            if evt.type == pg.QUIT:
                self.estado_jogo = EstadoJogo.ENCERRADO
                return

            if evt.type == pg.KEYDOWN and evt.key == pg.K_ESCAPE:
                self.estado_jogo = EstadoJogo.ENCERRADO
                return

            # Seleção de arma por teclado
            if self.estado_jogo == EstadoJogo.JOGANDO and evt.type == pg.KEYDOWN:
                if evt.key == pg.K_1:
                    self.arma_atual = 0
                elif evt.key == pg.K_2 and self.armas[1]["munição"] != 0:
                    self.arma_atual = 1
                elif evt.key == pg.K_3 and self.armas[2]["munição"] != 0:
                    self.arma_atual = 2

            if self.estado_jogo == EstadoJogo.MENU and evt.type == pg.MOUSEBUTTONDOWN:
                if self.botao_facil.foi_clicado(evt.pos):
                    self.dificuldade = "facil"
                    self.estado_jogo = EstadoJogo.POSICIONANDO_NAVIOS
                    self._set_mensagem_narrador("Modo Fácil selecionado! Boa sorte, Comandante!", "info")
                elif self.botao_medio.foi_clicado(evt.pos):
                    self.dificuldade = "medio"
                    self.estado_jogo = EstadoJogo.POSICIONANDO_NAVIOS
                    self._set_mensagem_narrador("Modo Médio! Um desafio equilibrado!", "info")
                elif self.botao_dificil.foi_clicado(evt.pos):
                    self.dificuldade = "dificil"
                    self.estado_jogo = EstadoJogo.POSICIONANDO_NAVIOS
                    self._set_mensagem_narrador("Modo Difícil! Prepare-se para o desafio extremo!", "info")
                elif self.botao_sair.foi_clicado(evt.pos):
                    self.estado_jogo = EstadoJogo.ENCERRADO

            if self.estado_jogo == EstadoJogo.POSICIONANDO_NAVIOS:
                if evt.type == pg.MOUSEBUTTONDOWN:
                    celula = self._obter_celula_do_mouse_tabuleiro(
                        evt.pos,
                        PADDING_LEFT_JOGADOR,
                        PADDING_TOP,
                    )
                    if celula and self.indice_navio_atual < len(NAVIOS_TIPOS):
                        linha, coluna = celula
                        if self._posicionar_navio_jogador(linha, coluna):
                            if self.indice_navio_atual >= len(NAVIOS_TIPOS):
                                self._posicionar_navios_maquina()
                                self.estado_jogo = EstadoJogo.INICIANDO
                                self.tempo_espera_inicio = 0
                                self._set_mensagem_narrador("Todos os navios posicionados! Preparando batalha...", "info")

                elif evt.type == pg.KEYDOWN and evt.key == pg.K_r:
                    self.orientacao_navio = (
                        "vertical" if self.orientacao_navio == "horizontal" else "horizontal"
                    )
                    self._set_notificacao(f"Orientacao: {self.orientacao_navio}")

            if (
                self.estado_jogo == EstadoJogo.JOGANDO
                and self.turno == Turno.JOGADOR
                and evt.type == pg.MOUSEBUTTONDOWN
                and evt.button == 1
            ):
                celula = self._obter_celula_do_mouse_tabuleiro(
                    evt.pos,
                    PADDING_LEFT_MAQUINA,
                    PADDING_TOP,
                )
                if celula:
                    linha, coluna = celula
                    pos = posicoes(linha, coluna)
                    if pos not in self.tabuleiro_maquina.clicados:
                        arma = self.armas[self.arma_atual]
                        acertou = False
                        afundou = False
                        for (dl, dc) in arma["area"]:
                            al, ac = linha + dl, coluna + dc
                            if 0 <= al < TAMANHO_GRADE and 0 <= ac < TAMANHO_GRADE:
                                p_area = posicoes(al, ac)
                                if p_area not in self.tabuleiro_maquina.clicados:
                                    res = self.tabuleiro_maquina.registrar_tiro(p_area)
                                    if res.get('sunk'):
                                        afundou = True
                                    elif res['hit']:
                                        acertou = True
                                    if res['hit']:
                                        px = PADDING_LEFT_MAQUINA + 1 + ac * CELL_SIZE + CELL_SIZE // 2
                                        py = PADDING_TOP + 1 + al * CELL_SIZE + CELL_SIZE // 2
                                        self._criar_particulas_explosao(px, py)

                        # Descontar munição (exceto torpedo)
                        if arma["munição"] > 0:
                            arma["munição"] -= 1
                            if arma["munição"] == 0 and self.arma_atual != 0:
                                self.arma_atual = 0  # volta para torpedo

                        # Mensagem do narrador
                        if afundou:
                            self._set_mensagem_narrador("AFUNDOU! Você destruiu um navio inimigo!", "afundou")
                        elif acertou:
                            self._set_mensagem_narrador("ACERTO! Você atingiu o navio inimigo!", "acerto")
                        else:
                            self._set_mensagem_narrador("ÁGUA! Seu tiro errou o alvo.", "agua")

                        # Verifica vitória imediata (sem esperar próximo frame)
                        if self._todos_afundados(self.tabuleiro_maquina):
                            self.vencedor = "jogador"
                            self._set_mensagem_narrador("VITÓRIA ÉPICA! Você é o vencedor!", "afundou")
                            self.estado_jogo = EstadoJogo.FINALIZADO
                        else:
                            self.tempo_turno_inicio = 0
                            self.turno = Turno.MAQUINA

            # Clique no painel de armas para selecionar arma
            if (self.estado_jogo == EstadoJogo.JOGANDO
                    and self.turno == Turno.JOGADOR
                    and evt.type == pg.MOUSEBUTTONDOWN
                    and evt.button == 1):
                mx, my = evt.pos
                CARD_H = 82
                CARD_G = 6
                IY_arm = PADDING_TOP - 10 + 34
                for idx in range(len(self.armas)):
                    cy = IY_arm + idx * (CARD_H + CARD_G)
                    card_rect = pg.Rect(PAINEL_ARMAS_X + 4, cy, PAINEL_ARMAS_W - 8, CARD_H)
                    if card_rect.collidepoint(mx, my):
                        if self.armas[idx]["munição"] != 0:
                            self.arma_atual = idx
                        break

            # Tela de fim de jogo
            if self.estado_jogo == EstadoJogo.FINALIZADO and evt.type == pg.MOUSEBUTTONDOWN:
                if self.botao_recomecar.foi_clicado(evt.pos):
                    self._resetar_partida()
                elif self.botao_menu.foi_clicado(evt.pos):
                    self._resetar_partida()
                    self.estado_jogo = EstadoJogo.MENU

    def _atualizar(self, dt):
        if self.estado_jogo == EstadoJogo.INICIANDO:
            self.tempo_espera_inicio += dt
            if self.tempo_espera_inicio >= TEMPO_ESPERA_INICIO * 1000:
                self.estado_jogo = EstadoJogo.JOGANDO
                self.turno = Turno.JOGADOR
                self.tempo_turno_inicio = 0
                self._set_mensagem_narrador("BATALHA INICIADA! Boa sorte, comandante!", "info")

        if self.estado_jogo == EstadoJogo.JOGANDO:
            self.tempo_turno_inicio += dt
            if self.turno == Turno.MAQUINA and self.tempo_turno_inicio >= TEMPO_ENTRE_TURNOS * 1000:
                self._jogar_maquina()
                self.turno = Turno.JOGADOR
                self.tempo_turno_inicio = 0

            if self._todos_afundados(self.tabuleiro_maquina):
                self.vencedor = "jogador"
                self._set_mensagem_narrador("VITÓRIA ÉPICA! Você é o vencedor!", "afundou")
                self.estado_jogo = EstadoJogo.FINALIZADO
            elif self._todos_afundados(self.tabuleiro_jogador):
                self.vencedor = "maquina"
                self._set_mensagem_narrador("Derrota... A máquina venceu a batalha.", "erro")
                self.estado_jogo = EstadoJogo.FINALIZADO

    def _desenhar(self):
        mouse_pos = pg.mouse.get_pos()
        if self.estado_jogo == EstadoJogo.MENU:
            self._desenhar_menu(mouse_pos)
        elif self.estado_jogo == EstadoJogo.POSICIONANDO_NAVIOS:
            self._desenhar_posicionamento_navios()
        elif self.estado_jogo == EstadoJogo.INICIANDO:
            self._desenhar_espera()
        elif self.estado_jogo == EstadoJogo.FINALIZADO:
            # Desenha o jogo de fundo
            self._desenhar_jogo()
            # Sobrepõe a tela de fim de jogo
            self._desenhar_fim_jogo(mouse_pos)
        else:
            self._desenhar_jogo()

        if self.notificacao and self.estado_jogo not in [EstadoJogo.JOGANDO, EstadoJogo.FINALIZADO]:
            fonte_msg = pg.font.SysFont(None, 28)
            msg = fonte_msg.render(self.notificacao, True, CYAN)
            self.screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT - 40))

        pg.display.flip()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            self._processar_eventos()
            if self.estado_jogo == EstadoJogo.ENCERRADO:
                running = False
                continue
            self._atualizar(dt)
            self._desenhar()

        pg.quit()
