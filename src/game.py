import csv
import os
import random
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
GOLD = (255, 215, 0)
ROSA_PORTAO = (255, 170, 210)
DEBUG_BG = (10, 10, 30, 200)

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
pygame.display.set_caption("Pac-Man — IA de Cerco e Multi-Fantasmas")

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

        self.velocidade = 2  # Velocidade ajustada para melhor fluidez dos fantasmas
        self.tamanho = 16
        self.direcao_atual = "Parado"
        self.proxima_direcao = "Parado"
        self.paredes = Paredes

        # Dicionário com os 4 fantasmas e seus estados de IA
        self.fantasmas = {
            'blinky': {
                'x': 13 * GRID_SIZE + GRID_SIZE // 2,
                'y': 11 * GRID_SIZE + GRID_SIZE // 2,
                'dir': 'Esquerda',
                'estado': 'Perseguindo Direto'
            },
            'pinky': {
                'x': 13 * GRID_SIZE + GRID_SIZE // 2,
                'y': 14 * GRID_SIZE + GRID_SIZE // 2,
                'dir': 'Cima',
                'estado': 'Antecipando Frente'
            },
            'inky': {
                'x': 12 * GRID_SIZE + GRID_SIZE // 2,
                'y': 14 * GRID_SIZE + GRID_SIZE // 2,
                'dir': 'Cima',
                'estado': 'Flanco Lateral'
            },
            'clyde': {
                'x': 15 * GRID_SIZE + GRID_SIZE // 2,
                'y': 14 * GRID_SIZE + GRID_SIZE // 2,
                'dir': 'Cima',
                'estado': 'Cerco/Aleatório'
            }
        }

        self.dados_telemetria = []
        self.rodando = True
        self.frame = 0
        self.debug_mode = False  # Modo Debug ativado por tecla

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
                    self.debug_mode = not self.debug_mode  # Alterna o modo debug

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

    def atualizar_fantasmas_ia(self):
        # Direções possíveis
        direcoes_possiveis = {
            "Cima": (0, -self.velocidade),
            "Baixo": (0, self.velocidade),
            "Esquerda": (-self.velocidade, 0),
            "Direita": (self.velocidade, 0)
        }

        # Alvos estratégicos para cada fantasma cercar o jogador de forma distinta
        alvos = {}
        # Blinky: Persegue diretamente a posição do Pac-Man
        alvos['blinky'] = (self.pacman_x, self.pacman_y)
        
        # Pinky: Tenta antecipar 4 tiles à frente do Pac-Man
        offset_frente = 4 * GRID_SIZE
        px, py = self.pacman_x, self.pacman_y
        if self.direcao_atual == "Cima": py -= offset_frente
        elif self.direcao_atual == "Baixo": py += offset_frente
        elif self.direcao_atual == "Esquerda": px -= offset_frente
        elif self.direcao_atual == "Direita": px += offset_frente
        alvos['pinky'] = (px, py)

        # Inky: Flanco lateral oposto
        alvos['inky'] = (self.pacman_x - (px - self.pacman_x), self.pacman_y - (py - self.pacman_y))

        # Clyde: Cerco alternativo ou recuo se muito perto
        dist_clyde = ((self.fantasmas['clyde']['x'] - self.pacman_x)**2 + (self.fantasmas['clyde']['y'] - self.pacman_y)**2)**0.5
        if dist_clyde < 4 * GRID_SIZE:
            alvos['clyde'] = (0, ALTURA)  # Canto inferior esquerdo (recuo/dispersão)
        else:
            alvos['clyde'] = (self.pacman_x, self.pacman_y)

        # Atualiza cada fantasma
        for nome, f_data in self.fantasmas.items():
            alvo_x, alvo_y = alvos[nome]
            
            # Avalia movimentos válidos
            movimentos_validos = []
            for d_nome, (dx, dy) in direcoes_possiveis.items():
                novo_x = f_data['x'] + dx
                novo_y = f_data['y'] + dy
                if self.pode_mover(novo_x, novo_y, self.tamanho):
                    # Evita o recuo imediato a menos que seja a única opção
                    oposto = {"Cima": "Baixo", "Baixo": "Cima", "Esquerda": "Direita", "Direita": "Esquerda"}
                    dist = ((novo_x - alvo_x)**2 + (novo_y - alvo_y)**2)**0.5
                    movimentos_validos.append((dist, d_nome, dx, dy))

            if movimentos_validos:
                # Ordena pelo mais próximo do alvo estratégico
                movimentos_validos.sort(key=lambda x: x[0])
                
                # Escolhe o melhor caminho ou altera se houver empate/bloqueio
                escolha = movimentos_validos[0]
                # Pequena estocasticidade para escolher entre os 2 melhores se disponíveis para diversificar caminhos
                if len(movimentos_validos) > 1 and random.random() < 0.2:
                    escolha = movimentos_validos[1]

                _, d_nome, dx, dy = escolha
                f_data['x'] += dx
                f_data['y'] += dy
                f_data['dir'] = d_nome
                f_data['estado'] = f"Cerco ({d_nome})"
            else:
                # Movimento aleatório de escape caso esteja totalmente bloqueado
                f_data['estado'] = "Aleatório (Bloqueado)"
                validos_aleatorios = [
                    (d, dx, dy) for d, (dx, dy) in direcoes_possiveis.items()
                    if self.pode_mover(f_data['x'] + dx, f_data['y'] + dy, self.tamanho)
                ]
                if validos_aleatorios:
                    d_nome, dx, dy = random.choice(validos_aleatorios)
                    f_data['x'] += dx
                    f_data['y'] += dy
                    f_data['dir'] = d_nome

    def atualizar_posicao(self):
        movendo, direcao_anterior = self.atualizar_posicao_pacman()
        self.atualizar_fantasmas_ia()

        # Salva a telemetria por frame com a posição exata de todos os elementos
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

        # Caixa semi-transparente no canto superior esquerdo
        box_width = 220
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

        # Desenhar Pac-Man
        pos_pac = (self.pacman_x / GRID_SIZE, self.pacman_y / GRID_SIZE)
        CharacterRenderer.draw_pacman(
            TELA, pygame, pos_pac, GRID_SIZE, direcao_ingles_pac, self.frame
        )

        # Desenhar os 4 fantasmas com suas respectivas cores
        for nome, f_data in self.fantasmas.items():
            pos_ghost = (f_data['x'] / GRID_SIZE, f_data['y'] / GRID_SIZE)
            dir_ghost_ingles = dir_map.get(f_data['dir'], "left")
            CharacterRenderer.draw_ghost(
                TELA, pygame, pos_ghost, GRID_SIZE, nome, dir_ghost_ingles,
                frame=self.frame,
            )

        # Desenha o log de debug se ativo
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
