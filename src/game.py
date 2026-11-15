import pygame
from character_renderer import CharacterRenderer
from ghost_ai import atualizar_fantasmas_ia
from ia_logger import IALogger
from menu import menu_principal

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
ROSA_PORTAO = (255, 170, 210)
VERDE = (46, 204, 113)

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
pygame.display.set_caption("Pac-Man — Jogo, IA Modular e Gráficos Vetoriais")

TUNNEL_ROW = 14
OPOSTOS = {
    "Cima": "Baixo",
    "Baixo": "Cima",
    "Esquerda": "Direita",
    "Direita": "Esquerda",
}

class PacmanGame:

  def __init__(self, nome_jogador):
    self.nome_jogador = nome_jogador
    self.pontuacao = 0
    self.fase = 1
    self.GRID_SIZE = GRID_SIZE
    self.LARGURA = LARGURA
    self.ALTURA = ALTURA
    self.TUNNEL_ROW = TUNNEL_ROW
    self.reiniciar_posicoes_e_mapa()

    self.velocidade_normal = 2
    self.velocidade_turbo = 3
    self.velocidade = self.velocidade_normal
    self.tamanho = 18
    self.direcao_atual = "Parado"
    self.proxima_direcao = "Parado"

    self.modo_medo_ativo = False
    self.timer_medo = 0
    self.pausado = False
    self.morreu = False
    self.pos_morte_x = 0
    self.pos_morte_y = 0

    self.posicoes_iniciais_fantasmas = {
        "blinky": (
            13 * GRID_SIZE + GRID_SIZE // 2,
            11 * GRID_SIZE + GRID_SIZE // 2,
        ),
        "pinky": (
            13 * GRID_SIZE + GRID_SIZE // 2,
            14 * GRID_SIZE + GRID_SIZE // 2,
        ),
        "inky": (
            12 * GRID_SIZE + GRID_SIZE // 2,
            14 * GRID_SIZE + GRID_SIZE // 2,
        ),
        "clyde": (
            15 * GRID_SIZE + GRID_SIZE // 2,
            14 * GRID_SIZE + GRID_SIZE // 2,
        ),
    }

    self.fantasmas = {
        "blinky": {
            "x": self.posicoes_iniciais_fantasmas["blinky"][0],
            "y": self.posicoes_iniciais_fantasmas["blinky"][1],
            "dir": "Esquerda",
            "estado": "Iniciando",
            "timer_saida": 0,
            "dist_alvo": 0,
        },
        "pinky": {
            "x": self.posicoes_iniciais_fantasmas["pinky"][0],
            "y": self.posicoes_iniciais_fantasmas["pinky"][1],
            "dir": "Cima",
            "estado": "Na Casa",
            "timer_saida": 15,
            "dist_alvo": 0,
        },
        "inky": {
            "x": self.posicoes_iniciais_fantasmas["inky"][0],
            "y": self.posicoes_iniciais_fantasmas["inky"][1],
            "dir": "Cima",
            "estado": "Na Casa",
            "timer_saida": 30,
            "dist_alvo": 0,
        },
        "clyde": {
            "x": self.posicoes_iniciais_fantasmas["clyde"][0],
            "y": self.posicoes_iniciais_fantasmas["clyde"][1],
            "dir": "Cima",
            "estado": "Na Casa",
            "timer_saida": 45,
            "dist_alvo": 0,
        },
    }

    self.cantos_dispersao = {
        "blinky": (LARGURA - 2 * GRID_SIZE, GRID_SIZE),
        "pinky": (2 * GRID_SIZE, GRID_SIZE),
        "inky": (LARGURA - 2 * GRID_SIZE, ALTURA - GRID_SIZE),
        "clyde": (2 * GRID_SIZE, ALTURA - GRID_SIZE),
    }

    self.centro_casa_fantasmas = (
        13 * GRID_SIZE + GRID_SIZE // 2,
        14 * GRID_SIZE + GRID_SIZE // 2,
    )

    self.dados_telemetria = []
    self.rodando = True
    self.retornar_menu = True
    self.frame = 0
    self.debug_mode = True
    self.logger = IALogger(nome_jogador)

  def reiniciar_posicoes_e_mapa(self):
    self.mapa = [list(linha) for linha in MAPA_ORIGINAL]
    self.pacman_x = 13 * GRID_SIZE + GRID_SIZE // 2
    self.pacman_y = 23 * GRID_SIZE + GRID_SIZE // 2
    for l_idx, linha in enumerate(self.mapa):
      for c_idx, char in enumerate(linha):
        if char == "P":
          self.pacman_x = c_idx * GRID_SIZE + GRID_SIZE // 2
          self.pacman_y = l_idx * GRID_SIZE + GRID_SIZE // 2
          self.mapa[l_idx][c_idx] = " "

  def verificar_fim_de_bolinhas(self):
    for linha in self.mapa:
      if "." in linha or "O" in linha:
        return False
    return True

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
    nx, ny = x + dx, y + dy
    raio = GRID_SIZE // 2 - 1
    if direcao == "Cima":
      check_x, check_y = nx, ny - raio
    elif direcao == "Baixo":
      check_x, check_y = nx, ny + raio
    elif direcao == "Esquerda":
      check_x, check_y = nx - raio, ny
    else:
      check_x, check_y = nx + raio, ny
    return self.celula_livre(
        int(check_x // GRID_SIZE), int(check_y // GRID_SIZE), fantasma_dentro_casa
    )

  def no_centro_celula(self, x, y, tolerancia=2):
    col, lin = int(x // GRID_SIZE), int(y // GRID_SIZE)
    return (
        abs(x - (col * GRID_SIZE + GRID_SIZE // 2)) <= tolerancia
        and abs(y - (lin * GRID_SIZE + GRID_SIZE // 2)) <= tolerancia
    )

  def alinhar_ao_centro(self, x, y):
    col, lin = int(x // GRID_SIZE), int(y // GRID_SIZE)
    return col * GRID_SIZE + GRID_SIZE // 2, lin * GRID_SIZE + GRID_SIZE // 2

  def verificar_coleta_pontos(self):
    col, lin = int(self.pacman_x // GRID_SIZE), int(self.pacman_y // GRID_SIZE)

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
          f_data["dir"] = OPOSTOS.get(f_data["dir"], f_data["dir"])

    if self.verificar_fim_de_bolinhas():
      self.pontuacao += 1000
      self.fase += 1
      self.reiniciar_posicoes_e_mapa()
      self.direcao_atual = "Parado"
      self.proxima_direcao = "Parado"
      for nome, f_data in self.fantasmas.items():
        f_data["x"], f_data["y"] = self.posicoes_iniciais_fantasmas[nome]
        f_data["dir"] = "Cima"

  def verificar_colisoes_fantasmas(self):
    for nome, f_data in self.fantasmas.items():
      if (
          (self.pacman_x - f_data["x"]) ** 2
          + (self.pacman_y - f_data["y"]) ** 2
      ) ** 0.5 < GRID_SIZE * 0.8:
        if self.modo_medo_ativo:
          self.pontuacao += 200
          f_data["x"], f_data["y"] = self.posicoes_iniciais_fantasmas[nome]
          f_data["dir"] = "Cima"
          f_data["timer_saida"] = self.frame + 10
          f_data["estado"] = "Comido (Respawn)"
        else:
          self.morreu = True
          self.pos_morte_x, self.pos_morte_y = self.pacman_x, self.pacman_y
          self.rodando = False
          self.retornar_menu = True

  def atualizar_posicao_pacman(self):
    if (
        self.proxima_direcao != "Parado"
        and self.proxima_direcao != self.direcao_atual
    ):
      if (
          OPOSTOS.get(self.direcao_atual) == self.proxima_direcao
          and self.pode_mover(
              self.pacman_x, self.pacman_y, self.proxima_direcao
          )
      ):
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
        self.pacman_x, self.pacman_y = self.alinhar_ao_centro(
            self.pacman_x, self.pacman_y
        )
        self.direcao_atual = "Parado"

    if TUNNEL_ROW * GRID_SIZE <= self.pacman_y < (TUNNEL_ROW + 1) * GRID_SIZE:
      self.pacman_x = self.pacman_x % LARGURA

    self.verificar_coleta_pontos()
    if self.rodando:
      self.verificar_colisoes_fantasmas()

  def atualizar_posicao(self):
    if self.pausado:
      return
    self.atualizar_posicao_pacman()
    if not self.rodando:
      return

    # Delega o cálculo de IA dos fantasmas para a função externa importada
    atualizar_fantasmas_ia(self)

    self.frame += 1

    self.dados_telemetria.append({
        "frame": self.frame,
        "jogador": self.nome_jogador,
        "pontuacao": self.pontuacao,
        "modo_medo": self.modo_medo_ativo,
        "pacman_x": self.pacman_x,
        "pacman_y": self.pacman_y,
        "blinky_x": self.fantasmas["blinky"]["x"],
        "blinky_y": self.fantasmas["blinky"]["y"],
        "pinky_x": self.fantasmas["pinky"]["x"],
        "pinky_y": self.fantasmas["pinky"]["y"],
        "inky_x": self.fantasmas["inky"]["x"],
        "inky_y": self.fantasmas["inky"]["y"],
        "clyde_x": self.fantasmas["clyde"]["x"],
        "clyde_y": self.fantasmas["clyde"]["y"],
        "ia_sucesso_captura": 0,
        "pos_morte_x": "",
        "pos_morte_y": "",
    })

  def desenhar_tabuleiro(self, superficie):
    for linha_idx, linha in enumerate(self.mapa):
      for coluna_idx, caractere in enumerate(linha):
        x, y = coluna_idx * GRID_SIZE, linha_idx * GRID_SIZE
        if caractere == "W":
          rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
          pygame.draw.rect(superficie, AZUL, rect)
          pygame.draw.rect(
              superficie,
              AZUL_BRILHO,
              rect.inflate(-4, -4),
              width=1,
              border_radius=4,
          )
        elif caractere == ".":
          pygame.draw.circle(
              superficie,
              AMARELO,
              (x + GRID_SIZE // 2, y + GRID_SIZE // 2),
              max(2, GRID_SIZE // 10),
          )
        elif caractere == "O":
          pygame.draw.circle(
              superficie,
              (255, 255, 245),
              (x + GRID_SIZE // 2, y + GRID_SIZE // 2),
              max(4, GRID_SIZE // 4),
          )
        elif caractere == "G":
          pygame.draw.line(
              superficie,
              ROSA_PORTAO,
              (x + 2, y + GRID_SIZE // 2),
              (x + GRID_SIZE - 2, y + GRID_SIZE // 2),
              3,
          )

  def desenhar_debug(self):
    if not self.debug_mode:
      return
    # Chama o HUD moderno, colorido e customizado por fantasma do IALogger
    self.logger.desenhar_hud_ia(
        TELA, pygame, LARGURA, ALTURA, self.frame, FPS,
        self.pontuacao, self.fase, self.modo_medo_ativo,
        self.timer_medo, self.fantasmas, self.pacman_y, self.pausado
    )

  def desenhar(self):
    TELA.fill(PRETO)
    self.desenhar_tabuleiro(TELA)

    pac_cell_x = (self.pacman_x - GRID_SIZE // 2) / GRID_SIZE
    pac_cell_y = (self.pacman_y - GRID_SIZE // 2) / GRID_SIZE
    CharacterRenderer.draw_pacman(
        TELA,
        pygame,
        (pac_cell_x, pac_cell_y),
        GRID_SIZE,
        direction=self.direcao_atual,
        frame=self.frame,
    )

    for nome, f_data in self.fantasmas.items():
      f_cell_x = (f_data["x"] - GRID_SIZE // 2) / GRID_SIZE
      f_cell_y = (f_data["y"] - GRID_SIZE // 2) / GRID_SIZE
      CharacterRenderer.draw_ghost(
          TELA,
          pygame,
          (f_cell_x, f_cell_y),
          GRID_SIZE,
          name=nome,
          direction=f_data["dir"],
          frightened=self.modo_medo_ativo,
          frame=self.frame,
      )

    self.desenhar_debug()
    pygame.display.flip()

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
      self.logger.salvar_dataset(
          self.dados_telemetria,
          self.morreu,
          self.pos_morte_x,
          self.pos_morte_y,
          self.pontuacao,
          self.frame,
          FPS,
      )
      return self.retornar_menu

def main():
  while True:
    nome_jogador = menu_principal(TELA, LARGURA)
    jogo = PacmanGame(nome_jogador)
    voltar = jogo.executar()
    if not voltar:
      break

if __name__ == "__main__":
  main()
