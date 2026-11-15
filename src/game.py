import csv
import os
import random
from collections import deque
import pygame

from character_renderer import CharacterRenderer

# Inicialização do Pygame
pygame.init()

# Cores
PRETO = (5, 5, 18)
AMARELO = (255, 220, 0)
VERMELHO = (235, 45, 55)
BRANCO = (245, 245, 245)
AZUL = (25, 75, 225)
AZUL_BRILHO = (65, 135, 255)
ROSA_PORTAO = (255, 170, 210)

# Configurações do Grid (tela 560x620)
GRID_SIZE = 20
CLOCK = pygame.time.Clock()
FPS = 30

# Mapa clássico do Pac-Man (28 colunas × 31 linhas).
MAPA = [
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWW",  # 0
    "W............WW............W",  # 1
    "W.WWWW.WWWWW.WW.WWWWW.WWWW.W",  # 2
    "WOWWWW.WWWWW.WW.WWWWW.WWWWOW",  # 3
    "W.WWWW.WWWWW.WW.WWWWW.WWWW.W",  # 4
    "W..........................W",  # 5
    "W.WWWW.WW.WWWWWWWW.WW.WWWW.W",  # 6
    "W.WWWW.WW.WWWWWWWW.WW.WWWW.W",  # 7
    "W......WW....WW....WW......W",  # 8
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
    "W......WW....WW....WW......W",  # 26
    "W.WWWWWWWWWW.WW.WWWWWWWWWW.W",  # 27
    "W.WWWWWWWWWW.WW.WWWWWWWWWW.W",  # 28
    "W..........................W",  # 29
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWW",  # 30
]

for i, linha in enumerate(MAPA):
    assert len(linha) == 28, f"Linha {i} tem {len(linha)} chars (esperado 28)"

LARGURA = len(MAPA[0]) * GRID_SIZE
ALTURA = len(MAPA) * GRID_SIZE
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Pac-Man — IA com BFS e Alinhamento Corrigido")

TUNNEL_ROW = 14

Paredes = []
for linha_idx, linha in enumerate(MAPA):
    for coluna_idx, caractere in enumerate(linha):
        if caractere in ("W", "G"):
            x = coluna_idx * GRID_SIZE
            y = linha_idx * GRID_SIZE
            Paredes.append(pygame.Rect(x, y, GRID_SIZE, GRID_SIZE))


def desenhar_tabuleiro(superficie):
    for linha_idx, linha in enumerate(MAPA):
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


class PacmanGame:
    def __init__(self):
        # Localiza Pac-Man no mapa
        self.pacman_x = 13 * GRID_SIZE + GRID_SIZE // 2
        self.pacman_y = 23 * GRID_SIZE + GRID_SIZE // 2
        for l_idx, linha in enumerate(MAPA):
            for c_idx, char in enumerate(linha):
                if char == "P":
                    self.pacman_x = c_idx * GRID_SIZE + GRID_SIZE // 2
                    self.pacman_y = l_idx * GRID_SIZE + GRID_SIZE // 2
                    break

        self.velocidade = 2
        self.tamanho = 16
        self.direcao_atual = "Parado"
        self.proxima_direcao = "Parado"
        self.paredes = Paredes

        # Dicionário com os 4 fantasmas
        self.fantasmas = {
            'blinky': {
                'x': 13 * GRID_SIZE + GRID_SIZE // 2,
                'y': 11 * GRID_SIZE + GRID_SIZE // 2,
                'dir': 'Esquerda',
                'estado': 'BFS Direto'
            },
            'pinky': {
                'x': 13 * GRID_SIZE + GRID_SIZE // 2,
                'y': 14 * GRID_SIZE + GRID_SIZE // 2,
                'dir': 'Cima',
                'estado': 'BFS Antecipado'
            },
            'inky': {
                'x': 12 * GRID_SIZE + GRID_SIZE // 2,
                'y': 14 * GRID_SIZE + GRID_SIZE // 2,
                'dir': 'Cima',
                'estado': 'BFS Flanco'
            },
            'clyde': {
                'x': 15 * GRID_SIZE + GRID_SIZE // 2,
                'y': 14 * GRID_SIZE + GRID_SIZE // 2,
                'dir': 'Cima',
                'estado': 'BFS / Dispersão'
            }
        }

        self.dados_telemetria = []
        self.rodando = True
        self.frame = 0
        self.debug_mode = False

    def processar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.rodando = False
            elif evento.type == pygame.KEYDOWN:
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

    def pode_mover(self, x, y, rect_size):
        offset = rect_size // 2
        novo_rect = pygame.Rect(x - offset, y - offset, rect_size, rect_size)

        eh_tunel = TUNNEL_ROW * GRID_SIZE <= y < (TUNNEL_ROW + 1) * GRID_SIZE
        if not eh_tunel and (
            novo_rect.left < 0
            or novo_rect.right > LARGURA
            or novo_rect.top < 0
            or novo_rect.bottom > ALTURA
        ):
            return False

        if novo_rect.collidelist(self.paredes) != -1:
            return False
        return True

    def atualizar_posicao_pacman(self):
        movendo = False
        direcao_anterior = self.direcao_atual

        dx, dy = self.obter_delta(self.proxima_direcao)
        if (dx != 0 or dy != 0) and self.pode_mover(self.pacman_x + dx, self.pacman_y + dy, self.tamanho):
            self.pacman_x += dx
            self.pacman_y += dy
            self.direcao_atual = self.proxima_direcao
            movendo = True
        elif self.direcao_atual != "Parado":
            dx, dy = self.obter_delta(self.direcao_atual)
            if self.pode_mover(self.pacman_x + dx, self.pacman_y + dy, self.tamanho):
                self.pacman_x += dx
                self.pacman_y += dy
                movendo = True
            else:
                self.direcao_atual = "Parado"

        if TUNNEL_ROW * GRID_SIZE <= self.pacman_y < (TUNNEL_ROW + 1) * GRID_SIZE:
            self.pacman_x = self.pacman_x % LARGURA

        return movendo, direcao_anterior

    def calcular_proximo_passo_bfs(self, inicio_x, inicio_y, destino_x, destino_y):
        """Calcula o caminho livre de colisão (sem bater em paredes 'W' ou 'G') usando BFS."""
        inicio_col = int(round(inicio_x // GRID_SIZE))
        inicio_lin = int(round(inicio_y // GRID_SIZE))
        dest_col = int(round(destino_x // GRID_SIZE))
        dest_lin = int(round(destino_y // GRID_SIZE))

        if (inicio_col, inicio_lin) == (dest_col, dest_lin):
            return None

        fila = deque()
        visitados = {(inicio_col, inicio_lin)}

        movs = [
            ("Cima", 0, -1),
            ("Baixo", 0, 1),
            ("Esquerda", -1, 0),
            ("Direita", 1, 0)
        ]

        for d_nome, dc, dl in movs:
            nc, nl = inicio_col + dc, inicio_lin + dl
            if 0 <= nl < len(MAPA) and 0 <= nc < len(MAPA[0]):
                if MAPA[nl][nc] not in ("W", "G"):
                    fila.append((nc, nl, d_nome))
                    visitados.add((nc, nl))

        while fila:
            c, l, primeiro_passo = fila.popleft()
            if (c, l) == (dest_col, dest_lin):
                return primeiro_passo

            for d_nome, dc, dl in movs:
                nc, nl = c + dc, l + dl
                if 0 <= nl < len(MAPA) and 0 <= nc < len(MAPA[0]):
                    if MAPA[nl][nc] not in ("W", "G"):
                        if (nc, nl) not in visitados:
                            visitados.add((nc, nl))
                            fila.append((nc, nl, primeiro_passo))
        return None

    def atualizar_fantasmas_ia(self):
        direcoes_possiveis = {
            "Cima": (0, -self.velocidade),
            "Baixo": (0, self.velocidade),
            "Esquerda": (-self.velocidade, 0),
            "Direita": (self.velocidade, 0)
        }

        # Alvos estratégicos de cerco
        alvos = {}
        alvos['blinky'] = (self.pacman_x, self.pacman_y)  # Direto
        
        # Pinky: Antecipa 4 tiles à frente
        offset_frente = 4 * GRID_SIZE
        px, py = self.pacman_x, self.pacman_y
        if self.direcao_atual == "Cima": py -= offset_frente
        elif self.direcao_atual == "Baixo": py += offset_frente
        elif self.direcao_atual == "Esquerda": px -= offset_frente
        elif self.direcao_atual == "Direita": px += offset_frente
        alvos['pinky'] = (px, py)

        # Inky: Flanco oposto
        alvos['inky'] = (self.pacman_x - (px - self.pacman_x), self.pacman_y - (py - self.pacman_y))

        # Clyde: Dispersa se muito perto, caso contrário persegue
        dist_clyde = ((self.fantasmas['clyde']['x'] - self.pacman_x)**2 + (self.fantasmas['clyde']['y'] - self.pacman_y)**2)**0.5
        if dist_clyde < 4 * GRID_SIZE:
            alvos['clyde'] = (0, ALTURA)
        else:
            alvos['clyde'] = (self.pacman_x, self.pacman_y)

        for nome, f_data in self.fantasmas.items():
            alvo_x, alvo_y = alvos[nome]
            
            # Tenta encontrar rota sem colisão por BFS
            proximo_passo_nome = self.calcular_proximo_passo_bfs(f_data['x'], f_data['y'], alvo_x, alvo_y)
            
            if proximo_passo_nome and proximo_passo_nome in direcoes_possiveis:
                dx, dy = direcoes_possiveis[proximo_passo_nome]
                if self.pode_mover(f_data['x'] + dx, f_data['y'] + dy, self.tamanho):
                    f_data['x'] += dx
                    f_data['y'] += dy
                    f_data['dir'] = proximo_passo_nome
                    f_data['estado'] = f"BFS ({proximo_passo_nome})"
                    continue

            # Fallback: Movimento aleatório seguro se o BFS falhar/estiver preso
            f_data['estado'] = "Aleatório (Fallback)"
            validos = [
                (d, dx, dy) for d, (dx, dy) in direcoes_possiveis.items()
                if self.pode_mover(f_data['x'] + dx, f_data['y'] + dy, self.tamanho)
            ]
            if validos:
                d_nome, dx, dy = random.choice(validos)
                f_data['x'] += dx
                f_data['y'] += dy
                f_data['dir'] = d_nome

    def atualizar_posicao(self):
        movendo, direcao_anterior = self.atualizar_posicao_pacman()
        self.atualizar_fantasmas_ia()

        self.frame += 1
        registro = {
            "frame": self.frame,
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
            "proxima_direcao_jogador": self.proxima_direcao
        }
        self.dados_telemetria.append(registro)

    def desenhar_debug(self):
        if not self.debug_mode:
            return

        font = pygame.font.Font(None, 18)
        linhas_debug = [
            "[MODO DEBUG ATIVO - TAB]",
            f"Blinky: {self.fantasmas['blinky']['estado']}",
            f"Pinky:  {self.fantasmas['pinky']['estado']}",
            f"Inky:   {self.fantasmas['inky']['estado']}",
            f"Clyde:  {self.fantasmas['clyde']['estado']}"
        ]

        box_width = 240
        box_height = 20 + len(linhas_debug) * 18
        debug_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        debug_surface.fill((10, 10, 30, 220))
        pygame.draw.rect(debug_surface, (65, 135, 255), debug_surface.get_rect(), 1, border_radius=4)

        for idx, texto in enumerate(linhas_debug):
            color = (255, 215, 0) if idx == 0 else (245, 245, 245)
            txt_surface = font.render(texto, True, color)
            debug_surface.blit(txt_surface, (10, 8 + idx * 18))

        TELA.blit(debug_surface, (10, 10))

    def desenhar(self):
        TELA.fill(PRETO)
        desenhar_tabuleiro(TELA)

        dir_map = {
            "Cima": "up", "Baixo": "down",
            "Esquerda": "left", "Direita": "right",
        }
        direcao_ingles_pac = dir_map.get(self.direcao_atual, "left")

        # Correção do alinhamento: Subtrai metade do tile para ajustar perfeitamente ao topo-esquerdo do grid
        pos_pac = (
            (self.pacman_x - GRID_SIZE // 2) / GRID_SIZE,
            (self.pacman_y - GRID_SIZE // 2) / GRID_SIZE
        )
        CharacterRenderer.draw_pacman(
            TELA, pygame, pos_pac, GRID_SIZE, direcao_ingles_pac, self.frame
        )

        for nome, f_data in self.fantasmas.items():
            pos_ghost = (
                (f_data['x'] - GRID_SIZE // 2) / GRID_SIZE,
                (f_data['y'] - GRID_SIZE // 2) / GRID_SIZE
            )
            dir_ghost_ingles = dir_map.get(f_data['dir'], "left")
            CharacterRenderer.draw_ghost(
                TELA, pygame, pos_ghost, GRID_SIZE, nome, dir_ghost_ingles,
                frame=self.frame,
            )

        self.desenhar_debug()
        pygame.display.flip()

    def salvar_dataset(self, caminho_arquivo="dataset_pacman.csv"):
        if not self.dados_telemetria:
            return
        chaves = self.dados_telemetria[0].keys()
        diretorio = os.path.dirname(caminho_arquivo)
        if diretorio:
            os.makedirs(diretorio, exist_ok=True)
        with open(caminho_arquivo, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=chaves)
            writer.writeheader()
            writer.writerows(self.dados_telemetria)
        print(
            f"[INFO] Dataset salvo com {len(self.dados_telemetria)}"
            f" registros por frame em {caminho_arquivo}"
        )

    def executar(self):
        while self.rodando:
            self.processar_eventos()
            self.atualizar_posicao()
            self.desenhar()
            CLOCK.tick(FPS)
        pygame.quit()
        self.salvar_dataset()


def main():
    jogo = PacmanGame()
    jogo.executar()


if __name__ == "__main__":
    main()
