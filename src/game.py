import csv
import os
import random
from collections import deque
import pygame

# Inicialização do Pygame
pygame.init()

# Cores
PRETO = (5, 5, 18)
AMARELO = (255, 220, 0)
VERMELHO = (235, 45, 55)
ROSA = (255, 182, 193)
CIANO = (0, 255, 255)
LARANJA = (255, 165, 0)
BRANCO = (245, 245, 245)
AZUL = (25, 75, 225)
AZUL_BRILHO = (65, 135, 255)
AZUL_MEDO = (30, 144, 255)
AZUL_PISCANDO = (240, 248, 255)
ROSA_PORTAO = (255, 170, 210)
VERDE = (46, 204, 113)
CINZA_INPUT = (35, 35, 60)
BORDA_INPUT = (65, 135, 255)

# Configurações do Grid (tela 560x620)
GRID_SIZE = 20
CLOCK = pygame.time.Clock()
FPS = 30

MAPA_ORIGINAL = [
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWW",  # 0
    "W............WW............W",  # 1
    "W.WWWW.WWWWW.WW.WWWWW.WWWW.W",  # 2
    "WOWWWW.WWWWW.WW.WWWWW.WWWWOW",  # 3
    "W.WWWW.WWWWW.WW.WWWWW.WWWW.W",  # 4
    "W..........................W",  # 5
    "W.WWWW.WW.WWWWWWWW.WW.WWWW.W",  # 6
    "W.WWWW.WW.WWWWWWWW.WW.WWWW.W",  # 7
    "W......WW....WW    WW......W",  # 8
    "WWWWWW.WWWWW WW WWWWW.WWWWWW",  # 9
    "     W.WWWWW WW WWWWW.W     ",  # 10
    "     W.WW          WW.W     ",  # 11
    "     W.WW WWWGGWWW WW.W     ",  # 12
    "WWWWWW.WW W      W WW.WWWWWW",  # 13
    "      .   W      W   .      ",  # 14  <- túnel
    "WWWWWW.WW W      W WW.WWWWWW",  # 15
    "     W.WW WWWWWWWW WW.W     ",  # 16
    "     W.WW          WW.W     ",  # 17
    "     W.WW WWWWWWWW WW.W     ",  # 18
    "WWWWWW.WW WWWWWWWW WW.WWWWWW",  # 19
    "W............WW............W",  # 20
    "W.WWWW.WWWWW.WW.WWWWW.WWWW.W",  # 21
    "W.WWWW.WWWWW.WW.WWWWW.WWWW.W",  # 22
    "WO..WW.......P .......WW..OW",  # 23
    "WWW.WW.WW.WWWWWWWW.WW.WW.WWW",  # 24
    "WWW.WW.WW.WWWWWWWW.WW.WW.WWW",  # 25
    "W......WW....WW    WW......W",  # 26
    "W.WWWWWWWWWW.WW.WWWWWWWWWW.W",  # 27
    "W.WWWWWWWWWW.WW.WWWWWWWWWW.W",  # 28
    "W..........................W",  # 29
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWW",  # 30
]

LARGURA = len(MAPA_ORIGINAL[0]) * GRID_SIZE
ALTURA = len(MAPA_ORIGINAL) * GRID_SIZE
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Pac-Man — Menu Gráfico e IA")

TUNNEL_ROW = 14
OPOSTOS = {
    "Cima": "Baixo",
    "Baixo": "Cima",
    "Esquerda": "Direita",
    "Direita": "Esquerda",
}


def carregar_ranking(arquivo="scores.csv"):
    ranking = []
    if os.path.exists(arquivo):
        try:
            with open(arquivo, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    ranking.append(row)
        except Exception:
            pass
    return ranking


def salvar_ranking(nome, pontuacao, tempo, arquivo="scores.csv"):
    ranking = carregar_ranking(arquivo)
    ranking.append({"Nome": nome, "Pontuacao": str(pontuacao), "Tempo": str(tempo)})
    ranking = sorted(ranking, key=lambda x: int(x["Pontuacao"]), reverse=True)[:5]
    
    with open(arquivo, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Nome", "Pontuacao", "Tempo"])
        writer.writeheader()
        writer.writerows(ranking)


class PacmanGame:
    def __init__(self, nome_jogador):
        self.nome_jogador = nome_jogador
        self.mapa = [list(linha) for linha in MAPA_ORIGINAL]
        
        self.pacman_x = 13 * GRID_SIZE + GRID_SIZE // 2
        self.pacman_y = 23 * GRID_SIZE + GRID_SIZE // 2
        for l_idx, linha in enumerate(self.mapa):
            for c_idx, char in enumerate(linha):
                if char == "P":
                    self.pacman_x = c_idx * GRID_SIZE + GRID_SIZE // 2
                    self.pacman_y = l_idx * GRID_SIZE + GRID_SIZE // 2
                    self.mapa[l_idx][c_idx] = " "

        self.velocidade_normal = 2
        self.velocidade_turbo = 3
        self.velocidade = self.velocidade_normal
        self.tamanho = 18
        self.direcao_atual = "Parado"
        self.proxima_direcao = "Parado"
        self.pontuacao = 0

        self.modo_medo_ativo = False
        self.timer_medo = 0
        self.pausado = False
        self.morreu = False
        self.pos_morte_x = 0
        self.pos_morte_y = 0

        self.posicoes_iniciais_fantasmas = {
            'blinky': (13 * GRID_SIZE + GRID_SIZE // 2, 11 * GRID_SIZE + GRID_SIZE // 2),
            'pinky': (13 * GRID_SIZE + GRID_SIZE // 2, 14 * GRID_SIZE + GRID_SIZE // 2),
            'inky': (12 * GRID_SIZE + GRID_SIZE // 2, 14 * GRID_SIZE + GRID_SIZE // 2),
            'clyde': (15 * GRID_SIZE + GRID_SIZE // 2, 14 * GRID_SIZE + GRID_SIZE // 2)
        }

        self.fantasmas = {
            'blinky': {
                'x': self.posicoes_iniciais_fantasmas['blinky'][0],
                'y': self.posicoes_iniciais_fantasmas['blinky'][1],
                'dir': 'Esquerda',
                'estado': 'Iniciando',
                'timer_saida': 0,
                'dist_alvo': 0,
                'cor_original': VERMELHO
            },
            'pinky': {
                'x': self.posicoes_iniciais_fantasmas['pinky'][0],
                'y': self.posicoes_iniciais_fantasmas['pinky'][1],
                'dir': 'Cima',
                'estado': 'Na Casa',
                'timer_saida': 15,
                'dist_alvo': 0,
                'cor_original': ROSA
            },
            'inky': {
                'x': self.posicoes_iniciais_fantasmas['inky'][0],
                'y': self.posicoes_iniciais_fantasmas['inky'][1],
                'dir': 'Cima',
                'estado': 'Na Casa',
                'timer_saida': 30,
                'dist_alvo': 0,
                'cor_original': CIANO
            },
            'clyde': {
                'x': self.posicoes_iniciais_fantasmas['clyde'][0],
                'y': self.posicoes_iniciais_fantasmas['clyde'][1],
                'dir': 'Cima',
                'estado': 'Na Casa',
                'timer_saida': 45,
                'dist_alvo': 0,
                'cor_original': LARANJA
            }
        }

        self.cantos_dispersao = {
            'blinky': (LARGURA - 2 * GRID_SIZE, GRID_SIZE),
            'pinky': (2 * GRID_SIZE, GRID_SIZE),
            'inky': (LARGURA - 2 * GRID_SIZE, ALTURA - GRID_SIZE),
            'clyde': (2 * GRID_SIZE, ALTURA - GRID_SIZE)
        }

        self.centro_casa_fantasmas = (13 * GRID_SIZE + GRID_SIZE // 2, 14 * GRID_SIZE + GRID_SIZE // 2)

        self.dados_telemetria = []
        self.rodando = True
        self.retornar_menu = True
        self.frame = 0
        self.debug_mode = True

    def processar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.rodando = False
                self.retornar_menu = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    self.rodando = False
                    self.retornar_menu = True
                elif evento.key == pygame.K_SPACE:
                    self.pausado = not self.pausado
                elif not self.pausado:
                    if evento.key in (pygame.K_UP, pygame.K_w):
                        self.proxima_direcao = "Cima"
                    elif evento.key in (pygame.K_DOWN, pygame.K_s):
                        self.proxima_direcao = "Baixo"
                    elif evento.key in (pygame.K_LEFT, pygame.K_a):
                        self.proxima_direcao = "Esquerda"
                    elif evento.key in (pygame.K_RIGHT, pygame.K_d):
                        self.proxima_direcao = "Direita"
                    elif evento.key == pygame.K_TAB:
                        self.debug_mode = not self.debug_mode

    def obter_delta(self, direcao):
        if direcao == "Cima":
            return 0, -self.velocidade
        if direcao == "Baixo":
            return 0, self.velocidade
        if direcao == "Esquerda":
            return -self.velocidade, 0
        if direcao == "Direita":
            return self.velocidade, 0
        return 0, 0

    def celula_livre(self, col, lin, fantasma_dentro_casa=False):
        if lin == TUNNEL_ROW and (col < 0 or col >= len(self.mapa[0])):
            return True
        if 0 <= lin < len(self.mapa) and 0 <= col < len(self.mapa[0]):
            char = self.mapa[lin][col]
            if char == "W":
                return False
            if char == "G":
                return fantasma_dentro_casa
            return True
        return False

    def pode_mover(self, x, y, direcao, fantasma_dentro_casa=False):
        dx, dy = self.obter_delta(direcao)
        if dx == 0 and dy == 0:
            return False

        nx = x + dx
        ny = y + dy

        raio = GRID_SIZE // 2 - 1
        if direcao == "Cima":
            check_x, check_y = nx, ny - raio
        elif direcao == "Baixo":
            check_x, check_y = nx, ny + raio
        elif direcao == "Esquerda":
            check_x, check_y = nx - raio, ny
        else:
            check_x, check_y = nx + raio, ny

        col = int(check_x // GRID_SIZE)
        lin = int(check_y // GRID_SIZE)
        return self.celula_livre(col, lin, fantasma_dentro_casa)

    def no_centro_celula(self, x, y, tolerancia=2):
        col = int(x // GRID_SIZE)
        lin = int(y // GRID_SIZE)
        centro_x = col * GRID_SIZE + GRID_SIZE // 2
        centro_y = lin * GRID_SIZE + GRID_SIZE // 2
        return abs(x - centro_x) <= tolerancia and abs(y - centro_y) <= tolerancia

    def alinhar_ao_centro(self, x, y):
        col = int(x // GRID_SIZE)
        lin = int(y // GRID_SIZE)
        return col * GRID_SIZE + GRID_SIZE // 2, lin * GRID_SIZE + GRID_SIZE // 2

    def verificar_coleta_pontos(self):
        col = int(self.pacman_x // GRID_SIZE)
        lin = int(self.pacman_y // GRID_SIZE)
        
        if 0 <= lin < len(self.mapa) and 0 <= col < len(self.mapa[0]):
            item = self.mapa[lin][col]
            if item == ".":
                self.mapa[lin][col] = " "
                self.pontuacao += 10
            elif item == "O":
                self.mapa[lin][col] = " "
                self.pontuacao += 50
                self.modo_medo_ativo = True
                self.timer_medo = 210
                self.velocidade = self.velocidade_turbo
                for f_data in self.fantasmas.values():
                    f_data['dir'] = OPOSTOS.get(f_data['dir'], f_data['dir'])

    def verificar_colisoes_fantasmas(self):
        for nome, f_data in self.fantasmas.items():
            distancia = ((self.pacman_x - f_data['x']) ** 2 + (self.pacman_y - f_data['y']) ** 2) ** 0.5
            if distancia < GRID_SIZE * 0.8:
                if self.modo_medo_ativo:
                    self.pontuacao += 200
                    pos_inicial = self.posicoes_iniciais_fantasmas[nome]
                    f_data['x'], f_data['y'] = pos_inicial
                    f_data['dir'] = 'Cima'
                    f_data['timer_saida'] = self.frame + 10
                    f_data['estado'] = "Comido (Respawn)"
                else:
                    self.morreu = True
                    self.pos_morte_x = self.pacman_x
                    self.pos_morte_y = self.pacman_y
                    self.rodando = False
                    self.retornar_menu = True

    def atualizar_posicao_pacman(self):
        if self.proxima_direcao != "Parado" and self.proxima_direcao != self.direcao_atual:
            eh_oposto = OPOSTOS.get(self.direcao_atual) == self.proxima_direcao
            if eh_oposto and self.pode_mover(self.pacman_x, self.pacman_y, self.proxima_direcao):
                self.direcao_atual = self.proxima_direcao
            elif self.no_centro_celula(self.pacman_x, self.pacman_y):
                cx, cy = self.alinhar_ao_centro(self.pacman_x, self.pacman_y)
                if self.pode_mover(cx, cy, self.proxima_direcao):
                    self.pacman_x, self.pacman_y = cx, cy
                    self.direcao_atual = self.proxima_direcao

        if self.direcao_atual != "Parado":
            if self.pode_mover(self.pacman_x, self.pacman_y, self.direcao_atual):
                dx, dy = self.obter_delta(self.direcao_atual)
                self.pacman_x += dx
                self.pacman_y += dy
            else:
                self.pacman_x, self.pacman_y = self.alinhar_ao_centro(self.pacman_x, self.pacman_y)
                self.direcao_atual = "Parado"

        if TUNNEL_ROW * GRID_SIZE <= self.pacman_y < (TUNNEL_ROW + 1) * GRID_SIZE:
            self.pacman_x = self.pacman_x % LARGURA

        self.verificar_coleta_pontos()
        self.verificar_colisoes_fantasmas()

    def calcular_proximo_passo_bfs(self, inicio_x, inicio_y, destino_x, destino_y, dir_atual, dentro_casa=False):
        inicio_col = max(0, min(len(self.mapa[0]) - 1, int(inicio_x // GRID_SIZE)))
        inicio_lin = max(0, min(len(self.mapa) - 1, int(inicio_y // GRID_SIZE)))
        dest_col = max(0, min(len(self.mapa[0]) - 1, int(destino_x // GRID_SIZE)))
        dest_lin = max(0, min(len(self.mapa) - 1, int(destino_y // GRID_SIZE)))

        if (inicio_col, inicio_lin) == (dest_col, dest_lin):
            return None

        fila = deque()
        visitados = {(inicio_col, inicio_lin)}
        oposto = OPOSTOS.get(dir_atual)

        movs = [
            ("Cima", 0, -1),
            ("Baixo", 0, 1),
            ("Esquerda", -1, 0),
            ("Direita", 1, 0),
        ]

        for d_nome, dc, dl in movs:
            if d_nome == oposto:
                continue
            nc, nl = inicio_col + dc, inicio_lin + dl
            if 0 <= nl < len(self.mapa) and 0 <= nc < len(self.mapa[0]):
                if self.celula_livre(nc, nl, dentro_casa):
                    fila.append((nc, nl, d_nome))
                    visitados.add((nc, nl))

        if not fila and oposto:
            for d_nome, dc, dl in movs:
                if d_nome == oposto:
                    nc, nl = inicio_col + dc, inicio_lin + dl
                    if 0 <= nl < len(self.mapa) and 0 <= nc < len(self.mapa[0]):
                        if self.celula_livre(nc, nl, dentro_casa):
                            fila.append((nc, nl, d_nome))
                            visitados.add((nc, nl))

        while fila:
            c, l, primeiro_passo = fila.popleft()
            if (c, l) == (dest_col, dest_lin):
                return primeiro_passo

            for d_nome, dc, dl in movs:
                nc, nl = c + dc, l + dl
                if 0 <= nl < len(self.mapa) and 0 <= nc < len(self.mapa[0]):
                    if self.celula_livre(nc, nl, dentro_casa) and (nc, nl) not in visitados:
                        visitados.add((nc, nl))
                        fila.append((nc, nl, primeiro_passo))
        return None

    def atualizar_fantasmas_ia(self):
        if self.modo_medo_ativo:
            self.timer_medo -= 1
            if self.timer_medo <= 0:
                self.modo_medo_ativo = False
                self.velocidade = self.velocidade_normal

        px, py = self.pacman_x, self.pacman_y

        alvo_blinky = (px, py)
        offset = 4 * GRID_SIZE
        p_frente_x, p_frente_y = px, py
        if self.direcao_atual == "Cima": p_frente_y -= offset
        elif self.direcao_atual == "Baixo": p_frente_y += offset
        elif self.direcao_atual == "Esquerda": p_frente_x -= offset
        elif self.direcao_atual == "Direita": p_frente_x += offset
        alvo_pinky = (p_frente_x, p_frente_y)

        bx, by = self.fantasmas['blinky']['x'], self.fantasmas['blinky']['y']
        alvo_inky = (px - (bx - px), py - (by - py))

        dist_clyde = ((self.fantasmas['clyde']['x'] - px) ** 2 + (self.fantasmas['clyde']['y'] - py) ** 2) ** 0.5
        alvo_clyde = (GRID_SIZE * 2, ALTURA - GRID_SIZE * 2) if dist_clyde < 5 * GRID_SIZE else (px, py)

        alvos_perseguicao = {
            'blinky': (alvo_blinky, "Ataque Direto"),
            'pinky': (alvo_pinky, "Interceptando Frente"),
            'inky': (alvo_inky, "Flanco Cruzado"),
            'clyde': (alvo_clyde, "Cerco Retaguarda")
        }

        for nome, f_data in self.fantasmas.items():
            lin_atual = max(0, min(len(self.mapa) - 1, int(f_data['y'] // GRID_SIZE)))
            dentro_casa = 12 <= lin_atual <= 14

            if dentro_casa:
                if self.frame < f_data['timer_saida']:
                    f_data['estado'] = "Aguardando Saída"
                    continue
                alvo_x, alvo_y = (13 * GRID_SIZE + GRID_SIZE // 2, 11 * GRID_SIZE + GRID_SIZE // 2)
                f_data['estado'] = "Saindo da Casa"
            elif self.modo_medo_ativo:
                alvo_x, alvo_y = self.centro_casa_fantasmas
                f_data['estado'] = "Fuginho p/ Casa 😨"
            else:
                tempo_fora = self.frame - f_data['timer_saida']
                if tempo_fora < 90:
                    alvo_x, alvo_y = self.cantos_dispersao[nome]
                    f_data['estado'] = "Dispersão Inicial"
                else:
                    par_alvo, estrategia = alvos_perseguicao[nome]
                    alvo_x, alvo_y = par_alvo
                    f_data['estado'] = f"{estrategia}"

            f_data['dist_alvo'] = int(((f_data['x'] - alvo_x) ** 2 + (f_data['y'] - alvo_y) ** 2) ** 0.5)

            if self.no_centro_celula(f_data['x'], f_data['y'], tolerancia=1):
                f_data['x'], f_data['y'] = self.alinhar_ao_centro(f_data['x'], f_data['y'])

                proximo = self.calcular_proximo_passo_bfs(
                    f_data['x'], f_data['y'], alvo_x, alvo_y, f_data['dir'], dentro_casa
                )

                if proximo and self.pode_mover(f_data['x'], f_data['y'], proximo, dentro_casa):
                    f_data['dir'] = proximo
                else:
                    oposto = OPOSTOS.get(f_data['dir'])
                    livres = [
                        d for d in ("Cima", "Baixo", "Esquerda", "Direita")
                        if self.pode_mover(f_data['x'], f_data['y'], d, dentro_casa)
                    ]
                    sem_recuo = [d for d in livres if d != oposto]
                    escolhas = sem_recuo if sem_recuo else livres
                    if escolhas:
                        f_data['dir'] = random.choice(escolhas)

            if self.pode_mover(f_data['x'], f_data['y'], f_data['dir'], dentro_casa):
                dx, dy = self.obter_delta(f_data['dir'])
                f_data['x'] += dx
                f_data['y'] += dy

            if TUNNEL_ROW * GRID_SIZE <= f_data['y'] < (TUNNEL_ROW + 1) * GRID_SIZE:
                f_data['x'] = f_data['x'] % LARGURA

    def atualizar_posicao(self):
        if self.pausado:
            return

        self.atualizar_posicao_pacman()
        if not self.rodando:
            return

        self.atualizar_fantasmas_ia()

        self.frame += 1
        
        registro = {
            "frame": self.frame,
            "jogador": self.nome_jogador,
            "pontuacao": self.pontuacao,
            "modo_medo": self.modo_medo_ativo,
            "pacman_x": self.pacman_x,
            "pacman_y": self.pacman_y,
            "blinky_x": self.fantasmas['blinky']['x'],
            "blinky_y": self.fantasmas['blinky']['y'],
            "pinky_x": self.fantasmas['pinky']['x'],
            "pinky_y": self.fantasmas['pinky']['y'],
            "inky_x": self.fantasmas['inky']['x'],
            "inky_y": self.fantasmas['inky']['y'],
            "clyde_x": self.fantasmas['clyde']['x'],
            "clyde_y": self.fantasmas['clyde']['y'],
            "ia_sucesso_captura": 0,
            "pos_morte_x": "",
            "pos_morte_y": ""
        }
        self.dados_telemetria.append(registro)

    def desenhar_tabuleiro(self, superficie):
        for linha_idx, linha in enumerate(self.mapa):
            for coluna_idx, caractere in enumerate(linha):
                x = coluna_idx * GRID_SIZE
                y = linha_idx * GRID_SIZE

                if caractere == "W":
                    rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
                    pygame.draw.rect(superficie, AZUL, rect)
                    inset = max(2, GRID_SIZE // 9)
                    inner = rect.inflate(-inset * 2, -inset * 2)
                    pygame.draw.rect(
                        superficie, AZUL_BRILHO, inner,
                        width=1, border_radius=4,
                    )
                elif caractere == ".":
                    cx = x + GRID_SIZE // 2
                    cy = y + GRID_SIZE // 2
                    pygame.draw.circle(
                        superficie, AMARELO, (cx, cy),
                        max(2, GRID_SIZE // 10),
                    )
                elif caractere == "O":
                    cx = x + GRID_SIZE // 2
                    cy = y + GRID_SIZE // 2
                    pygame.draw.circle(
                        superficie, (255, 255, 245), (cx, cy),
                        max(4, GRID_SIZE // 4),
                    )
                elif caractere == "G":
                    pygame.draw.line(
                        superficie, ROSA_PORTAO,
                        (x + 2, y + GRID_SIZE // 2),
                        (x + GRID_SIZE - 2, y + GRID_SIZE // 2),
                        3,
                    )

    def desenhar_debug(self):
        if not self.debug_mode:
            return

        font = pygame.font.Font(None, 16)
        tempo_seg = round(self.frame / FPS, 1)
        tempo_medo_seg = round(self.timer_medo / FPS, 1) if self.modo_medo_ativo else 0.0
        status_medo = f" | 😨 MEDO: {tempo_medo_seg}s" if self.modo_medo_ativo else ""
        status_pause = " [PAUSADO - ESPAÇO]" if self.pausado else ""

        linhas_debug = [
            f"[JOGADOR: {self.nome_jogador} | PONTOS: {self.pontuacao} | TEMPO: {tempo_seg}s{status_medo}{status_pause}]",
            f"Blinky: {self.fantasmas['blinky']['estado']} | Dist: {self.fantasmas['blinky']['dist_alvo']}px",
            f"Pinky:  {self.fantasmas['pinky']['estado']} | Dist: {self.fantasmas['pinky']['dist_alvo']}px",
            f"Inky:   {self.fantasmas['inky']['estado']} | Dist: {self.fantasmas['inky']['dist_alvo']}px",
            f"Clyde:  {self.fantasmas['clyde']['estado']} | Dist: {self.fantasmas['clyde']['dist_alvo']}px",
        ]

        box_width = 440
        box_height = 22 + len(linhas_debug) * 16
        debug_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        debug_surface.fill((10, 10, 30, 230))
        pygame.draw.rect(debug_surface, (65, 135, 255), debug_surface.get_rect(), 1, border_radius=4)

        for idx, texto in enumerate(linhas_debug):
            color = (255, 215, 0) if idx == 0 else (245, 245, 245)
            txt_surface = font.render(texto, True, color)
            debug_surface.blit(txt_surface, (8, 6 + idx * 16))

        pos_x = 10
        if self.pacman_y < (ALTURA / 2):
            pos_y = ALTURA - box_height - 10
        else:
            pos_y = 10

        TELA.blit(debug_surface, (pos_x, pos_y))

    def desenhar(self):
        TELA.fill(PRETO)
        self.desenhar_tabuleiro(TELA)

        pygame.draw.circle(TELA, AMARELO, (int(self.pacman_x), int(self.pacman_y)), self.tamanho // 2)

        for nome, f_data in self.fantasmas.items():
            fx, fy = int(f_data['x']), int(f_data['y'])
            
            if self.modo_medo_ativo:
                if self.timer_medo < 60 and (self.frame // 6) % 2 == 0:
                    cor_fantasma = AZUL_PISCANDO
                else:
                    cor_fantasma = AZUL_MEDO
            else:
                cor_fantasma = f_data['cor_original']

            pygame.draw.circle(TELA, cor_fantasma, (fx, fy), self.tamanho // 2)
            pygame.draw.circle(TELA, BRANCO, (fx - 3, fy - 2), 3)
            pygame.draw.circle(TELA, BRANCO, (fx + 3, fy - 2), 3)

        self.desenhar_debug()
        pygame.display.flip()

    def salvar_dataset(self):
        if not self.dados_telemetria:
            return
        
        if self.morreu and self.dados_telemetria:
            self.dados_telemetria[-1]["ia_sucesso_captura"] = 1
            self.dados_telemetria[-1]["pos_morte_x"] = self.pos_morte_x
            self.dados_telemetria[-1]["pos_morte_y"] = self.pos_morte_y

        caminho_arquivo = "dataset_pacman.csv"
        existe = os.path.exists(caminho_arquivo)
        chaves = self.dados_telemetria[0].keys()
        
        with open(caminho_arquivo, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=chaves)
            if not existe:
                writer.writeheader()
            writer.writerows(self.dados_telemetria)
        
        tempo_total = round(self.frame / FPS, 1)
        salvar_ranking(self.nome_jogador, self.pontuacao, f"{tempo_total}s")
        print(f"[INFO] Dataset atualizado e pontuação salva!")

    def executar(self):
        try:
            while self.rodando:
                self.processar_eventos()
                self.atualizar_posicao()
                self.desenhar()
                CLOCK.tick(FPS)
        except Exception as e:
            print(f"[ERRO CAPTURADO] {e}")
        finally:
            self.salvar_dataset()
            return self.retornar_menu


def menu_principal():
    font_titulo = pygame.font.Font(None, 44)
    font_texto = pygame.font.Font(None, 22)
    
    nome_jogador = "Player1"
    ativo_input = True  # Começa focado no input de nome

    rodando_menu = True
    while rodando_menu:
        TELA.fill(PRETO)
        
        # Título
        titulo = font_titulo.render("PAC-MAN — MENU PRINCIPAL", True, AMARELO)
        TELA.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 25))

        # Caixa de Digitação do Nome
        label_nome = font_texto.render("Digite seu Nome:", True, BRANCO)
        TELA.blit(label_nome, (LARGURA // 2 - 140, 75))

        input_rect = pygame.Rect(LARGURA // 2 - 140, 100, 280, 36)
        pygame.draw.rect(TELA, CINZA_INPUT, input_rect, border_radius=6)
        pygame.draw.rect(TELA, BORDA_INPUT if ativo_input else BRANCO, input_rect, 2, border_radius=6)

        txt_surface = font_texto.render(nome_jogador, True, AMARELO if ativo_input else BRANCO)
        TELA.blit(txt_surface, (input_rect.x + 10, input_rect.y + 8))

        # Instrução para iniciar
        instrucao = font_texto.render("Pressione [ENTER] para Jogar | [ESC] para Sair", True, VERDE)
        TELA.blit(instrucao, (LARGURA // 2 - instrucao.get_width() // 2, 150))

        # Quadro de Pontuações (Leaderboard)
        rank_titulo = font_texto.render("--- MELHORES PONTUAÇÕES (RANKING) ---", True, CIANO)
        TELA.blit(rank_titulo, (LARGURA // 2 - rank_titulo.get_width() // 2, 195))

        ranking = carregar_ranking()
        if not ranking:
            vazio = font_texto.render("Nenhuma partida registrada ainda.", True, BRANCO)
            TELA.blit(vazio, (LARGURA // 2 - vazio.get_width() // 2, 235))
        else:
            header = font_texto.render(f"{'Pos':<4} {'Nome':<12} {'Pontos':<10} {'Tempo'}", True, AMARELO)
            TELA.blit(header, (70, 230))
            for i, r in enumerate(ranking):
                linha_txt = font_texto.render(f"{i+1}º   {r['Nome']:<12} {r['Pontuacao']:<10} {r['Tempo']}", True, BRANCO)
                TELA.blit(linha_txt, (70, 260 + i * 26))

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    if nome_jogador.strip():
                        rodando_menu = False
                elif evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
                elif evento.key == pygame.K_BACKSPACE:
                    if ativo_input:
                        nome_jogador = nome_jogador[:-1]
                else:
                    if ativo_input and len(nome_jogador) < 12:
                        nome_jogador += evento.unicode

    return nome_jogador.strip() if nome_jogador.strip() else "Player1"


def main():
    while True:
        nome_jogador = menu_principal()
        jogo = PacmanGame(nome_jogador)
        voltar = jogo.executar()
        if not voltar:
            break


if __name__ == "__main__":
    main()
