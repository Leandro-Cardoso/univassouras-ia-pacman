import csv
import os
import pygame

# Inicialização do Pygame
pygame.init()

# Cores
PRETO = (0, 0, 0)
AMARELO = (255, 255, 0)
VERMELHO = (255, 0, 0)
BRANCO = (255, 255, 255)
AZUL = (0, 0, 255)
GOLD = (255, 215, 0)

# Configurações do Grid
GRID_SIZE = 20

# Relógio para controlar os FPS
CLOCK = pygame.time.Clock()
FPS = 30

MAPA = [
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWW",
    "W............WW............W",
    "W.WWWW.WWWWW.WW.WWWWW.WWWW.W",
    "W.WWWW.WWWWW.WW.WWWWW.WWWW.W",
    "W..........................W",
    "W.WWWW.WW.WWWWWWWW.WW.WWWW.W",
    "W......WW....WW....WW......W",
    "WWWWWW.WWWWW WW WWWWW.WWWWWW",
    "     W.WW          WW.W     ",
    "WWWWWW.WW WWWWWWWW WW.WWWWWW",
    "      .   W      W   .      ",
    "WWWWWW.WW WWWWWWWW WW.WWWWWW",
    "     W.WW          WW.W     ",
    "WWWWWW.WW WWWWWWWW WW.WWWWWW",
    "W.....P......WW............W",
    "W.WWWW.WWWWW.WW.WWWWW.WWWW.W",
    "WW.WW.WW.WWWWWWWW.WW.WW.WW.W",
    "W......WW....WW....WW......W",
    "W.WWWWWWWWWW.WW.WWWWWWWWWW.W",
    "W..........................W",
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWW",
]

# Configurações da Tela baseadas no Mapa
LARGURA = len(MAPA[0]) * GRID_SIZE
ALTURA = len(MAPA) * GRID_SIZE
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Pacman com IA")

# Construção das paredes a partir do mapa
Paredes = []
for linha_idx, linha in enumerate(MAPA):
  for coluna_idx, caractere in enumerate(linha):
    x = coluna_idx * GRID_SIZE
    y = linha_idx * GRID_SIZE
    if caractere == "W":
      Paredes.append(pygame.Rect(x, y, GRID_SIZE, GRID_SIZE))

def desenhar_tabuleiro(superficie):
  for linha_idx, linha in enumerate(MAPA):
    for coluna_idx, caractere in enumerate(linha):
      x = coluna_idx * GRID_SIZE
      y = linha_idx * GRID_SIZE

      if caractere == "W":
        pygame.draw.rect(
            superficie, AZUL, (x, y, GRID_SIZE, GRID_SIZE)
        )
      elif caractere in (".", "P"):
        centro_x = x + GRID_SIZE // 2
        centro_y = y + GRID_SIZE // 2
        pygame.draw.circle(
            superficie, AMARELO, (centro_x, centro_y), 2
        )
      elif caractere == "O":
        centro_x = x + GRID_SIZE // 2
        centro_y = y + GRID_SIZE // 2
        pygame.draw.circle(
            superficie, GOLD, (centro_x, centro_y), 6
        )

class PacmanGame:
  def __init__(self):
    # Procura a posição inicial do Pacman no mapa ('P') ou usa valor padrão seguro
    self.pacman_x = 130
    self.pacman_y = 290
    for l_idx, linha in enumerate(MAPA):
      for c_idx, char in enumerate(linha):
        if char == "P":
          self.pacman_x = c_idx * GRID_SIZE + GRID_SIZE // 2
          self.pacman_y = l_idx * GRID_SIZE + GRID_SIZE // 2
          break

    self.velocidade = 5
    self.tamanho = 16  # Hitbox de colisão (16x16)
    self.direcao_atual = "Parado"
    self.proxima_direcao = "Parado"
    self.paredes = Paredes

    # Fantasma simulado posicionado na casa dos fantasmas
    self.fantasma_x = 14 * GRID_SIZE + GRID_SIZE // 2
    self.fantasma_y = 10 * GRID_SIZE + GRID_SIZE // 2

    # Lista para armazenar a telemetria da partida
    self.dados_telemetria = []
    self.rodando = True

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
    elif direcao == "Baixo":
      return 0, self.velocidade
    elif direcao == "Esquerda":
      return -self.velocidade, 0
    elif direcao == "Direita":
      return self.velocidade, 0
    return 0, 0

  def pode_mover(self, dx, dy):
    novo_x = self.pacman_x + dx
    novo_y = self.pacman_y + dy
    offset = self.tamanho // 2
    novo_rect = pygame.Rect(
        novo_x - offset, novo_y - offset, self.tamanho, self.tamanho
    )

    # Limites da tela (permite wrap no túnel da linha 10)
    eh_tunel = 9 * GRID_SIZE <= novo_y <= 11 * GRID_SIZE
    if not eh_tunel and (
        novo_rect.left < 0
        or novo_rect.right > LARGURA
        or novo_rect.top < 0
        or novo_rect.bottom > ALTURA
    ):
      return False

    # Colisão com as paredes do labirinto
    if novo_rect.collidelist(self.paredes) != -1:
      return False

    return True

  def atualizar_posicao(self):
    movendo = False
    direcao_anterior = self.direcao_atual

    # Tenta mover na próxima direção solicitada pelo jogador
    dx, dy = self.obter_delta(self.proxima_direcao)
    if (dx != 0 or dy != 0) and self.pode_mover(dx, dy):
      self.pacman_x += dx
      self.pacman_y += dy
      self.direcao_atual = self.proxima_direcao
      movendo = True
    elif self.direcao_atual != "Parado":
      # Se a próxima direção estiver bloqueada por parede, tenta continuar na direção atual
      dx, dy = self.obter_delta(self.direcao_atual)
      if self.pode_mover(dx, dy):
        self.pacman_x += dx
        self.pacman_y += dy
        movendo = True
      else:
        self.direcao_atual = "Parado"
    else:
      self.direcao_atual = "Parado"

    # Wrap horizontal do túnel (linha 10)
    if 9 * GRID_SIZE <= self.pacman_y <= 11 * GRID_SIZE:
      if self.pacman_x < 0:
        self.pacman_x = LARGURA
      elif self.pacman_x > LARGURA:
        self.pacman_x = 0

    if movendo:
      # Coleta de telemetria apenas quando o jogador se move (Otimização da Etapa 1)
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

    # Desenhar Pacman
    pygame.draw.circle(
        TELA, AMARELO, (int(self.pacman_x), int(self.pacman_y)), 10
    )

    # Desenhar Fantasma
    pygame.draw.circle(
        TELA, VERMELHO, (int(self.fantasma_x), int(self.fantasma_y)), 10
    )

    pygame.display.flip()

  def salvar_dataset(self, caminho_arquivo="dataset_pacman.csv"):
    if not self.dados_telemetria:
      return
    chaves = self.dados_telemetria[0].keys()
    
    # Corrige o caminho do arquivo
    diretorio = os.path.dirname(caminho_arquivo)
    if diretorio:
      os.makedirs(diretorio, exist_ok=True)
      
    with open(
        caminho_arquivo, mode="w", newline="", encoding="utf-8"
    ) as f:
      writer = csv.DictWriter(f, fieldnames=chaves)
      writer.writeheader()
      writer.writerows(self.dados_telemetria)
    print(
        f"[INFO] Dataset salvo com sucesso com"
        f" {len(self.dados_telemetria)} registros em {caminho_arquivo}"
    )

  def executar(self):
    while self.rodando:
      self.processar_eventos()
      self.atualizar_posicao()
      self.desenhar()
      CLOCK.tick(FPS)
    pygame.quit()
    self.salvar_dataset()

if __name__ == "__main__":
  jogo = PacmanGame()
  jogo.executar()
