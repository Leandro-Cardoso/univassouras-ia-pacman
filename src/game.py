import csv
import os
import pygame

from .character_renderer import CharacterRenderer

# Inicialização do Pygame
pygame.init()

# Cores
PRETO = (5, 5, 18)
AMARELO = (255, 220, 0)
VERMELHO = (235, 45, 55)
BRANCO = (245, 245, 245)
AZUL = (25, 75, 225)
AZUL_BRILHO = (65, 135, 255)
GOLD = (255, 215, 0)
ROSA_PORTAO = (255, 170, 210)

# Configurações do Grid (tela 560x620)
GRID_SIZE = 20
CLOCK = pygame.time.Clock()
FPS = 30

# Mapa clássico do Pac-Man (28 colunas × 31 linhas).
#   W = parede | . = pastilha | O = superpastilha | G = portão | P = Pac-Man | espaço = vazio
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
    "WO..WW.......P .......WW..OW",  # 23  <- início do Pac-Man
    "WWW.WW.WW.WWWWWWWW.WW.WW.WWW",  # 24
    "WWW.WW.WW.WWWWWWWW.WW.WW.WWW",  # 25
    "W......WW....WW....WW......W",  # 26
    "W.WWWWWWWWWW.WW.WWWWWWWWWW.W",  # 27
    "W.WWWWWWWWWW.WW.WWWWWWWWWW.W",  # 28
    "W..........................W",  # 29
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWW",  # 30
]

# Sanidade: cada linha deve ter 28 caracteres
for i, linha in enumerate(MAPA):
    assert len(linha) == 28, f"Linha {i} tem {len(linha)} chars (esperado 28)"

LARGURA = len(MAPA[0]) * GRID_SIZE
ALTURA = len(MAPA) * GRID_SIZE
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Pac-Man — Mapa Clássico com IA")

# Linha do túnel (a mesma do arcade)
TUNNEL_ROW = 14

# Paredes incluem W e G (o portão bloqueia o Pac-Man)
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
                # Estilo MazeRenderer: azul com borda brilhante
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
                # Portão rosa (linha horizontal no meio da célula)
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

        self.velocidade = 5
        self.tamanho = 16
        self.direcao_atual = "Parado"
        self.proxima_direcao = "Parado"
        self.paredes = Paredes

        # Fantasma acima da casa (posição clássica do Blinky)
        self.fantasma_x = 14 * GRID_SIZE + GRID_SIZE // 2
        self.fantasma_y = 11 * GRID_SIZE + GRID_SIZE // 2

        self.dados_telemetria = []
        self.rodando = True
        self.frame = 0

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

    def pode_mover(self, dx, dy):
        novo_x = self.pacman_x + dx
        novo_y = self.pacman_y + dy
        offset = self.tamanho // 2
        novo_rect = pygame.Rect(
            novo_x - offset, novo_y - offset, self.tamanho, self.tamanho
        )

        # Túnel: permite atravessar bordas na linha do meio
        eh_tunel = TUNNEL_ROW * GRID_SIZE <= novo_y < (TUNNEL_ROW + 1) * GRID_SIZE
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

    def atualizar_posicao(self):
        movendo = False
        direcao_anterior = self.direcao_atual

        dx, dy = self.obter_delta(self.proxima_direcao)
        if (dx != 0 or dy != 0) and self.pode_mover(dx, dy):
            self.pacman_x += dx
            self.pacman_y += dy
            self.direcao_atual = self.proxima_direcao
            movendo = True
        elif self.direcao_atual != "Parado":
            dx, dy = self.obter_delta(self.direcao_atual)
            if self.pode_mover(dx, dy):
                self.pacman_x += dx
                self.pacman_y += dy
                movendo = True
            else:
                self.direcao_atual = "Parado"
        else:
            self.direcao_atual = "Parado"

        # Wrap horizontal do túnel (linha 14)
        if TUNNEL_ROW * GRID_SIZE <= self.pacman_y < (TUNNEL_ROW + 1) * GRID_SIZE:
            self.pacman_x = self.pacman_x % LARGURA

        if movendo:
            distancia_fantasma = (
                (self.pacman_x - self.fantasma_x) ** 2
                + (self.pacman_y - self.fantasma_y) ** 2
            ) ** 0.5

            self.dados_telemetria.append({
                "pacman_x": self.pacman_x,
                "pacman_y": self.pacman_y,
                "fantasma_dist_min": round(distancia_fantasma, 2),
                "modo_medo": 0,
                "ultimas_direcoes": direcao_anterior,
                "proxima_direcao_jogador": self.proxima_direcao,
            })

    def desenhar(self):
        TELA.fill(PRETO)
        desenhar_tabuleiro(TELA)

        self.frame += 1
        dir_map = {
            "Cima": "up", "Baixo": "down",
            "Esquerda": "left", "Direita": "right",
        }
        direcao_ingles = dir_map.get(self.direcao_atual, "left")

        # Pac-Man vetorial
        pos_pac = (self.pacman_x / GRID_SIZE, self.pacman_y / GRID_SIZE)
        CharacterRenderer.draw_pacman(
            TELA, pygame, pos_pac, GRID_SIZE, direcao_ingles, self.frame
        )

        # Fantasma vetorial (Blinky)
        pos_ghost = (self.fantasma_x / GRID_SIZE, self.fantasma_y / GRID_SIZE)
        CharacterRenderer.draw_ghost(
            TELA, pygame, pos_ghost, GRID_SIZE, "blinky", "left",
            frame=self.frame,
        )

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
            f" registros em {caminho_arquivo}"
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