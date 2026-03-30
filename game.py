from pygame import *
from Campos.Tabuleiro import Tabuleiro
from Campos.Posicoes import posicoes
from Barcos.Destroyer import destroyer
from Barcos.Submarino import submarino
from Barcos.Cruzador import cruzador
from Barcos.Encouracado import Encouracado
from Barcos.Portaavioes import portaavioes
import random

# Inicializar pygame
init()

#TODO: Adicionar a logica de jogar novamente quando uma dos dois acerta a posição do inimigo
#TODO: arrumar o espeço que mostra qual dos navios está para ser posicionado, e orientado
#TODO: Adicionar as bombas e logicas para cada uma e as opções que podem ser utilizadas durante o jogo
#TODO: Arrumar o que mostra o lugar do tiro disparado e se um navio foi atingido ou afundado

# Configurações da tela
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
screen = display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
display.set_caption("Batalha Naval")

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 100, 200)
LIGHT_BLUE = (173, 216, 230)
RED = (255, 0, 0)
GRAY = (100, 100, 100)
GREEN = (0, 200, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)

# Configurações do tabuleiro
TAMANHO_GRADE = 10
CELL_SIZE = 40
PADDING_BOARD = 20

# Posição dos tabuleiros
PADDING_LEFT_JOGADOR = 50
PADDING_LEFT_MAQUINA = 650
PADDING_TOP = 100

BOARD_WIDTH = TAMANHO_GRADE * CELL_SIZE + 2
BOARD_HEIGHT = TAMANHO_GRADE * CELL_SIZE + 2

# Estados do jogo
MENU = 0
POSICIONANDO_NAVIOS = 1
JOGANDO = 2
INICIANDO = 3

# Turnos
JOGADOR = 0
MAQUINA = 1

# Definir navios disponíveis
NAVIOS_TIPOS = [
    {"nome": "Destroyer", "tamanho": 1, "classe": destroyer},
    {"nome": "Submarino", "tamanho": 2, "classe": submarino},
    {"nome": "Cruzador", "tamanho": 3, "classe": cruzador},
    {"nome": "Encouracado", "tamanho": 4, "classe": Encouracado},
    {"nome": "Portavião", "tamanho": 5, "classe": portaavioes},
]

# Criar tabuleiros
tabuleiro_jogador = Tabuleiro(tamanho=TAMANHO_GRADE)
tabuleiro_maquina = Tabuleiro(tamanho=TAMANHO_GRADE)

# Posições clicadas
posicoes_clicadas_jogador = []
posicoes_clicadas_maquina = []

# Dificuldade do jogo
dificuldade = None
tempo_espera_inicio = None
TEMPO_ESPERA = 3  # segundos
turno = JOGADOR

# Timer de turnos
tempo_turno_inicio = None
TEMPO_ENTRE_TURNOS = 2  # segundos de espera entre turnos

# Posicionamento de navios
indice_navio_atual = 0
navios_jogador = []
navios_maquina = []
orientacao_navio = "horizontal"  # horizontal ou vertical

class Botao:
    """Classe para representar botões no menu"""
    def __init__(self, x, y, width, height, texto, cor):
        self.rect = Rect(x, y, width, height)
        self.texto = texto
        self.cor = cor
        self.cor_hover = (min(cor[0] + 50, 255), min(cor[1] + 50, 255), min(cor[2] + 50, 255))
        self.is_hover = False
    
    def desenhar(self, screen, font):
        cor = self.cor_hover if self.is_hover else self.cor
        draw.rect(screen, cor, self.rect, 2)
        text_render = font.render(self.texto, True, WHITE)
        text_rect = text_render.get_rect(center=self.rect.center)
        screen.blit(text_render, text_rect)
    
    def verificar_hover(self, mouse_pos):
        self.is_hover = self.rect.collidepoint(mouse_pos)
    
    def foi_clicado(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

def desenhar_menu(mouse_pos, botao_facil, botao_medio):
    """Exibe o menu inicial do jogo"""
    screen.fill(BLACK)
    font_grande = font.SysFont(None, 48)
    font_pequena = font.SysFont(None, 36)
    
    # Verificar hover dos botões
    botao_facil.verificar_hover(mouse_pos)
    botao_medio.verificar_hover(mouse_pos)
    
    # Título
    title_text = font_grande.render("Batalha Naval", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))
    
    # Instruções
    instruction_text = font_pequena.render("Escolha a dificuldade:", True, GRAY)
    screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, 180))
    
    # Desenhar botões
    botao_facil.desenhar(screen, font_pequena)
    botao_medio.desenhar(screen, font_pequena)

def desenhar_espera(tempo_decorrido):
    """Exibe a tela de espera antes do jogo começar"""
    screen.fill(BLACK)
    font_grande = font.SysFont(None, 48)
    
    segundos_restantes = max(0, TEMPO_ESPERA - tempo_decorrido // 1000)
    
    espera_text = font_grande.render(f"Partida iniciando em {segundos_restantes}s", True, WHITE)
    screen.blit(espera_text, (SCREEN_WIDTH // 2 - espera_text.get_width() // 2, SCREEN_HEIGHT // 2 - espera_text.get_height() // 2))
    
    return segundos_restantes == 0

def desenhar_tabuleiro_posicionamento(x, y, tab, posicoes_clicadas, titulo):
    """Desenha um tabuleiro para o posicionamento de navios"""
    font_info = font.SysFont(None, 24)
    
    # Título
    titulo_text = font_info.render(titulo, True, WHITE)
    screen.blit(titulo_text, (x, y - 30))
    
    # Fundo do tabuleiro
    boardRect = (x, y, BOARD_WIDTH, BOARD_HEIGHT)
    draw.rect(screen, LIGHT_BLUE, boardRect)
    
    # Grid
    for i in range(TAMANHO_GRADE + 1):
        linha_y = y + i * CELL_SIZE
        draw.line(screen, BLACK, (x, linha_y), (x + BOARD_WIDTH - 2, linha_y), 1)
        
        col_x = x + i * CELL_SIZE
        draw.line(screen, BLACK, (col_x, y), (col_x, y + BOARD_HEIGHT - 2), 1)
    
    # Desenhar navios posicionados
    for navio in tab.navios:
        for posicao in navio.posicoes:
            px = x + 1 + posicao.coluna * CELL_SIZE
            py = y + 1 + posicao.linha * CELL_SIZE
            draw.rect(screen, GREEN, (px, py, CELL_SIZE - 1, CELL_SIZE - 1))
    
    # Desenhar tiros (posições clicadas)
    for posicao in posicoes_clicadas:
        px = x + 1 + posicao.coluna * CELL_SIZE
        py = y + 1 + posicao.linha * CELL_SIZE
        draw.circle(screen, RED, (px + CELL_SIZE // 2, py + CELL_SIZE // 2), 5)

def obter_celula_do_mouse_tabuleiro(mouse_pos, x_inicio, y_inicio):
    """Converte posição do mouse para índices da grade de um tabuleiro específico"""
    x, y = mouse_pos
    
    if (x_inicio <= x < x_inicio + BOARD_WIDTH and 
        y_inicio <= y < y_inicio + BOARD_HEIGHT):
        
        coluna = (x - x_inicio) // CELL_SIZE
        linha = (y - y_inicio) // CELL_SIZE
        
        if 0 <= linha < TAMANHO_GRADE and 0 <= coluna < TAMANHO_GRADE:
            return linha, coluna
    
    return None

def desenhar_posicionamento_navios(mouse_pos):
    """Tela para o jogador posicionar seus navios"""
    screen.fill(BLACK)
    
    # Desenhar título
    font_grande = font.SysFont(None, 48)
    titulo = font_grande.render("Posicione seus Navios", True, WHITE)
    screen.blit(titulo, (SCREEN_WIDTH // 2 - titulo.get_width() // 2, 20))
    
    # Desenhar tabuleiros
    desenhar_tabuleiro_posicionamento(PADDING_LEFT_JOGADOR, PADDING_TOP, tabuleiro_jogador, 
                                      posicoes_clicadas_jogador, "Seu Tabuleiro")
    desenhar_tabuleiro_posicionamento(PADDING_LEFT_MAQUINA, PADDING_TOP, tabuleiro_maquina, 
                                      posicoes_clicadas_maquina, "Tabuleiro Máquina")
    
    # Desenhar lista de navios para selecionar
    font_info = font.SysFont(None, 24)
    font_titulo = font.SysFont(None, 28)
    
    # Painel de navios à direita (entre os dois tabuleiros)
    panel_x = PADDING_LEFT_JOGADOR + BOARD_WIDTH + 100
    panel_y = PADDING_TOP
    
    navios_title = font_titulo.render("Navios a Posicionar:", True, CYAN)
    screen.blit(navios_title, (panel_x, panel_y))
    
    # Desenhar navios disponíveis
    for idx, navio_info in enumerate(NAVIOS_TIPOS):
        if idx < len(navios_jogador):
            # Já posicionado
            cor = GREEN
            status = "✓"
        elif idx == indice_navio_atual:
            # Selecionado
            cor = YELLOW
            status = "→"
        else:
            # Disponível
            cor = GRAY
            status = " "
        
        navio_text = font_info.render(f"{status} {navio_info['nome']} (Tam: {navio_info['tamanho']})", True, cor)
        screen.blit(navio_text, (panel_x, panel_y + 40 + idx * 30))
    
    # Instruções
    font_pequena = font.SysFont(None, 20)
    inst1 = font_pequena.render("Clique para posicionar", True, WHITE)
    inst2 = font_pequena.render("R: Rotacionar | Enter: Confirmar", True, WHITE)
    
    screen.blit(inst1, (panel_x, panel_y + 250))
    screen.blit(inst2, (panel_x, panel_y + 280))
    
    # Mostrar navio atual e orientação
    if indice_navio_atual < len(NAVIOS_TIPOS):
        navio_info = NAVIOS_TIPOS[indice_navio_atual]
        navio_atual = font_info.render(f"Navio: {navio_info['nome']}", True, YELLOW)
        orientacao_text = font_info.render(f"Orientação: {orientacao_navio.upper()}", True, YELLOW)
        screen.blit(navio_atual, (panel_x, panel_y + 320))
        screen.blit(orientacao_text, (panel_x, panel_y + 350))

def obter_posicoes_navio(linha, coluna, tamanho, orientacao_):
    """Retorna as posições que um navio ocuparia"""
    posicoes_navio = []
    
    if orientacao_ == "horizontal":
        for i in range(tamanho):
            if coluna + i >= TAMANHO_GRADE:
                return None
            posicoes_navio.append(posicoes(linha, coluna + i))
    else:  # vertical
        for i in range(tamanho):
            if linha + i >= TAMANHO_GRADE:
                return None
            posicoes_navio.append(posicoes(linha + i, coluna))
    
    return posicoes_navio

def verificar_posicoes_validas(pos_list, tab):
    """Verifica se as posições estão vazias"""
    for pos in pos_list:
        if pos in tab.atingidos:
            return False
        for navio in tab.navios:
            if pos in navio.posicoes:
                return False
    return True

def posicionar_navio_jogador(linha, coluna):
    """Posiciona um navio do jogador"""
    global indice_navio_atual, navios_jogador
    
    if indice_navio_atual >= len(NAVIOS_TIPOS):
        return False
    
    navio_info = NAVIOS_TIPOS[indice_navio_atual]
    pos_navio = obter_posicoes_navio(linha, coluna, navio_info['tamanho'], orientacao_navio)
    
    if pos_navio is None or not verificar_posicoes_validas(pos_navio, tabuleiro_jogador):
        print(f"Posição inválida para {navio_info['nome']}")
        return False
    
    # Criar navio e posicionar
    novo_navio = navio_info['classe'](navio_info['nome'])
    tabuleiro_jogador.posicionar_navio(novo_navio, pos_navio)
    navios_jogador.append(novo_navio)
    print(f"{navio_info['nome']} posicionado!")
    
    # Próximo navio
    indice_navio_atual += 1
    return True

def posicionar_navios_maquina():
    """IA posiciona todos os navios da máquina"""
    global navios_maquina
    
    for navio_info in NAVIOS_TIPOS:
        posicionado = False
        tentativas = 0
        
        while not posicionado and tentativas < 100:
            linha = random.randint(0, TAMANHO_GRADE - 1)
            coluna = random.randint(0, TAMANHO_GRADE - 1)
            orientacao_ = random.choice(["horizontal", "vertical"])
            
            pos_navio = obter_posicoes_navio(linha, coluna, navio_info['tamanho'], orientacao_)
            
            if pos_navio and verificar_posicoes_validas(pos_navio, tabuleiro_maquina):
                novo_navio = navio_info['classe'](navio_info['nome'])
                tabuleiro_maquina.posicionar_navio(novo_navio, pos_navio)
                navios_maquina.append(novo_navio)
                posicionado = True
            
            tentativas += 1

def jogar_maquina():
    """IA da máquina escolhe uma posição e atira"""
    while True:
        linha = random.randint(0, TAMANHO_GRADE - 1)
        coluna = random.randint(0, TAMANHO_GRADE - 1)
        pos = posicoes(linha, coluna)
        if pos not in posicoes_clicadas_maquina:
            posicoes_clicadas_maquina.append(pos)
            resultado = tabuleiro_jogador.registrar_tiro(pos)
            print(f"Máquina atira em ({linha}, {coluna}): {resultado}")
            return

def obter_celula_do_mouse(mouse_pos):
    """Converte posição do mouse para índices da grade - COMPATIBILIDADE"""
    x, y = mouse_pos
    
    # Verificar se o clique está dentro do tabuleiro JOGADOR
    if (PADDING_LEFT_JOGADOR <= x < PADDING_LEFT_JOGADOR + BOARD_WIDTH and 
        PADDING_TOP <= y < PADDING_TOP + BOARD_HEIGHT):
        
        coluna = (x - PADDING_LEFT_JOGADOR) // CELL_SIZE
        linha = (y - PADDING_TOP) // CELL_SIZE
        
        if 0 <= linha < TAMANHO_GRADE and 0 <= coluna < TAMANHO_GRADE:
            return linha, coluna
    
    # Verificar tabuleiro MÁQUINA
    if (PADDING_LEFT_MAQUINA <= x < PADDING_LEFT_MAQUINA + BOARD_WIDTH and 
        PADDING_TOP <= y < PADDING_TOP + BOARD_HEIGHT):
        
        coluna = (x - PADDING_LEFT_MAQUINA) // CELL_SIZE
        linha = (y - PADDING_TOP) // CELL_SIZE
        
        if 0 <= linha < TAMANHO_GRADE and 0 <= coluna < TAMANHO_GRADE:
            return linha, coluna
    
    return None

def desenhar_tabuleiro(turno, tempo_turno):
    """Desenha os dois tabuleiros lado a lado durante o jogo"""
    screen.fill(WHITE)
    
    # Desenhar tabuleiro do jogador
    desenhar_tabuleiro_posicionamento(PADDING_LEFT_JOGADOR, PADDING_TOP, tabuleiro_jogador, 
                                      posicoes_clicadas_jogador, "Seu Tabuleiro")
    
    # Desenhar tabuleiro da máquina (sem mostrar navios)
    screen_temp = screen.copy()
    
    # Tabuleiro máquina - não mostrar navios
    boardRect_maquina = (PADDING_LEFT_MAQUINA, PADDING_TOP, BOARD_WIDTH, BOARD_HEIGHT)
    draw.rect(screen, LIGHT_BLUE, boardRect_maquina)
    
    for i in range(TAMANHO_GRADE + 1):
        linha_y = PADDING_TOP + i * CELL_SIZE
        draw.line(screen, BLACK, (PADDING_LEFT_MAQUINA, linha_y), 
                 (PADDING_LEFT_MAQUINA + BOARD_WIDTH - 2, linha_y), 1)
        
        col_x = PADDING_LEFT_MAQUINA + i * CELL_SIZE
        draw.line(screen, BLACK, (col_x, PADDING_TOP), 
                 (col_x, PADDING_TOP + BOARD_HEIGHT - 2), 1)
    
    # Desenhar tiros do jogador no tabuleiro da máquina
    for posicao in posicoes_clicadas_jogador:
        px = PADDING_LEFT_MAQUINA + 1 + posicao.coluna * CELL_SIZE
        py = PADDING_TOP + 1 + posicao.linha * CELL_SIZE
        draw.circle(screen, RED, (px + CELL_SIZE // 2, py + CELL_SIZE // 2), 5)
    
    # Título tabuleiro máquina
    font_info = font.SysFont(None, 24)
    titulo_text = font_info.render("Tabuleiro Máquina", True, WHITE)
    screen.blit(titulo_text, (PADDING_LEFT_MAQUINA, PADDING_TOP - 30))
    
    # Desenhar informações de turno
    font_turno = font.SysFont(None, 36)
    
    if tempo_turno is not None:
        tempo_restante = max(0, TEMPO_ENTRE_TURNOS - tempo_turno // 1000)
    else:
        tempo_restante = 0
    
    if turno == JOGADOR:
        turno_text = font_turno.render("Sua vez!", True, GREEN)
        tempo_text = font_turno.render(f"Tempo: {tempo_restante}s", True, YELLOW)
    else:
        turno_text = font_turno.render("Máquina está jogando...", True, ORANGE)
        tempo_text = font_turno.render(f"Tempo: {tempo_restante}s", True, YELLOW)
    
    screen.blit(turno_text, (SCREEN_WIDTH // 2 - turno_text.get_width() // 2, 20))
    screen.blit(tempo_text, (SCREEN_WIDTH // 2 - tempo_text.get_width() // 2, 60))
    

# Game loop
running = True
estado_jogo = MENU
clock = time.Clock()

# Criar botões do menu
botao_facil = Botao(SCREEN_WIDTH // 2 - 100, 280, 200, 50, "Fácil", BLUE)
botao_medio = Botao(SCREEN_WIDTH // 2 - 100, 360, 200, 50, "Médio", BLUE)

while running:
    dt = clock.tick(60)  # Tempo decorrido desde o último frame em ms
    mouse_pos = mouse.get_pos()
    
    for evt in event.get():
        if evt.type == QUIT:
            running = False
        
        # Processar eventos do menu
        if estado_jogo == MENU and evt.type == MOUSEBUTTONDOWN:
            if botao_facil.foi_clicado(evt.pos):
                dificuldade = "facil"
                estado_jogo = POSICIONANDO_NAVIOS
                print("Dificuldade: Fácil selecionada!")
            elif botao_medio.foi_clicado(evt.pos):
                dificuldade = "medio"
                estado_jogo = POSICIONANDO_NAVIOS
                print("Dificuldade: Médio selecionada!")
        
        # Processar eventos do posicionamento de navios
        if estado_jogo == POSICIONANDO_NAVIOS:
            if evt.type == MOUSEBUTTONDOWN:
                # Clique no tabuleiro do jogador para posicionar navio
                celula = obter_celula_do_mouse_tabuleiro(evt.pos, PADDING_LEFT_JOGADOR, PADDING_TOP)
                if celula and indice_navio_atual < len(NAVIOS_TIPOS):
                    linha, coluna = celula
                    posicionar_navio_jogador(linha, coluna)
                    
                    # Se todos os navios foram posicionados, transição para jogo
                    if indice_navio_atual >= len(NAVIOS_TIPOS):
                        print("Todos os seus navios foram posicionados!")
                        posicionar_navios_maquina()
                        print("Navios da máquina posicionados!")
                        estado_jogo = INICIANDO
                        tempo_espera_inicio = 0
            
            elif evt.type == KEYDOWN:
                # R para rotacionar o navio
                if evt.key == K_r:
                    orientacao_navio = "vertical" if orientacao_navio == "horizontal" else "horizontal"
                    print(f"Orientação: {orientacao_navio}")
        
        # Processar eventos do jogo - APENAS jogador pode clicar
        if estado_jogo == JOGANDO and turno == JOGADOR and evt.type == MOUSEBUTTONDOWN:
            if evt.button == 1:  # Botão esquerdo do mouse
                celula = obter_celula_do_mouse_tabuleiro(evt.pos, PADDING_LEFT_MAQUINA, PADDING_TOP)
                if celula:
                    linha, coluna = celula
                    pos = posicoes(linha, coluna)
                    
                    # Evitar clicar na mesma posição duas vezes
                    if pos not in posicoes_clicadas_jogador:
                        posicoes_clicadas_jogador.append(pos)
                        # Registrar o tiro no tabuleiro da máquina
                        resultado = tabuleiro_maquina.registrar_tiro(pos)
                        print(f"Tiro jogador em ({linha}, {coluna}): {resultado}")
                        
                        # Iniciar timer para próximo turno
                        tempo_turno_inicio = 0
                        turno = MAQUINA
    
    # Atualizar estado de espera do menu
    if estado_jogo == INICIANDO:
        tempo_espera_inicio += dt
        if tempo_espera_inicio >= TEMPO_ESPERA * 1000:  # Converter para ms
            estado_jogo = JOGANDO
            turno = JOGADOR
            tempo_turno_inicio = None
            print("Jogo iniciado! Sua vez!")
    
    # Gerenciar turnos durante o jogo
    if estado_jogo == JOGANDO:
        if turno == JOGADOR and tempo_turno_inicio is not None:
            # Se o jogador já jogou, contar tempo até mudar para máquina
            tempo_turno_inicio += dt
            if tempo_turno_inicio >= TEMPO_ENTRE_TURNOS * 1000:
                turno = MAQUINA
                tempo_turno_inicio = 0
        
        elif turno == MAQUINA:
            # Contar tempo para máquina jogar
            tempo_turno_inicio += dt
            if tempo_turno_inicio >= TEMPO_ENTRE_TURNOS * 1000:
                # Máquina faz seu tiro
                jogar_maquina()
                # Voltar para jogador
                turno = JOGADOR
                tempo_turno_inicio = None
                print("Sua vez novamente!")
    
    # Desenhar baseado no estado do jogo
    if estado_jogo == MENU:
        desenhar_menu(mouse_pos, botao_facil, botao_medio)
    elif estado_jogo == POSICIONANDO_NAVIOS:
        desenhar_posicionamento_navios(mouse_pos)
    elif estado_jogo == JOGANDO:
        desenhar_tabuleiro(turno, tempo_turno_inicio if tempo_turno_inicio is not None else 0)
    elif estado_jogo == INICIANDO:
        desenhar_espera(tempo_espera_inicio)
    
    display.flip()

quit()


