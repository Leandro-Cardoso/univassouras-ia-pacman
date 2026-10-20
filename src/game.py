import csv
import os
import pygame

# Inicialização do Pygame
pygame.init()

# Configurações da Tela
LARGURA, ALTURA = 600, 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Pacman com IA")

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
    "WWWWWWWWWWWWWWWWWWWWWWWWWWW",
    "W............WW............W",
    "W.WWWW.WWWWW.WW.WWWWW.WWWW.W",
    "W.WWWW.WWWWW.WW.WWWWW.WWWW.W",
    "W..........................W",
    "W.WWWW.WW.WWWWWWWW.WW.WWWW.W",
    "W......WW....WW....WW......W",
    "WWWWWW.WWWWW WW WWWWW.WWWWWW",
    "     W.WW          WW.W     ",
    "WWWWWW.WW WWWWWWWW WW.WWWWWW",
    "      .   W   P  W   .      ",
    "WWWWWW.WW WWWWWWWW WW.WWWWWW",
    "     W.WW          WW.W     ",
    "WWWWWW.WW WWWWWWWW WW.WWWWWW",
    "W............WW............W",
    "W.WWWW.WWWWW.WW.WWWWW.WWWW.W",
    "WW.WW.WW.WWWWWWWW.WW.WW.WW.W",
    "W......WW....WW....WW......W",
    "W.WWWWWWWWWW.WW.WWWWWWWWWW.W",
    "W..........................W",
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWW",
]

LARGURA = len(MAPA[0]) * GRID_SIZE
ALTURA = len(MAPA) * GRID_SIZE
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Pac-man com IA")
relogio = pygame.time.Clock()

Paredes = []
pacman_x, pacman_y = 0, 0

for  linha_idx, linha in enumerate(MAPA):
  for coluna_idx, caractere in enumerate(linha):
    x = coluna_idx * GRID_SIZE
    y = linha_idx * GRID_SIZE
    if caractere == "W":
      Paredes.append(pygame.Rect(x, y, GRID_SIZE, GRID_SIZE))
    elif caractere == ".":
      pacman_x, pacman_y = x, y

      pacman_rect = pygame.Rect(pacman_x, pacman_y, 16, 16)

dx, dy = 0, 0

def desenhar_tabuleiro(superficie):
  for linha_idx, linha in enumerate(MAPA):
    for coluna_idx, caractere in enumerate(linha):
      x = coluna_idx * GRID_SIZE
      y = linha_idx * GRID_SIZE

      if caractere == "W":
        pygame.draw.rect(
            superficie, AZUL, (x, y, GRID_SIZE, GRID_SIZE)
        )
      elif caractere == ".":
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
      elif caractere == "P":
        centro_x = x + GRID_SIZE // 2
        centro_y = y + GRID_SIZE // 2
        pygame.draw.circle(
            superficie, AMARELO, (centro_x, centro_y), 8
        )

class PacmanGame:
  def __init__(self):
    self.pacman_x = 300
    self.pacman_y = 300
    self.velocidade = 5
    self.direcao_atual = "Parado"
    self.proxima_direcao = "Parado"

    # Fantasma simulado para calcular a distância mínima
    self.fantasma_x = 100
    self.fantasma_y = 100

    # Lista para armazenar a telemetria da partida
    self.dados_telemetria = []
    self.rodando = True

  def processar_eventos(self):
    for evento in pygame.event.get():
      if evento.type == pygame.QUIT:
        self.rodando = False
      elif evento.type == pygame.KEYDOWN:
        if evento.key == pygame.K_UP:
          self.proxima_direcao = "Cima"
        elif evento.key == pygame.K_DOWN:
          self.proxima_direcao = "Baixo"
        elif evento.key == pygame.K_LEFT:
          self.proxima_direcao = "Esquerda"
        elif evento.key == pygame.K_RIGHT:
          self.proxima_direcao = "Direita"

  def atualizar_posicao(self):
    movendo = False
    direcao_anterior = self.direcao_atual

    if self.proxima_direcao == "Cima":
      self.pacman_y -= self.velocidade
      movendo = True
    elif self.proxima_direcao == "Baixo":
      self.pacman_y += self.velocidade
      movendo = True
    elif self.proxima_direcao == "Esquerda":
      self.pacman_x -= self.velocidade
      movendo = True
    elif self.proxima_direcao == "Direita":
      self.pacman_x += self.velocidade
      movendo = True

    # Garante que o Pacman permaneça dentro da tela visível
    self.pacman_x = max(10, min(LARGURA - 10, self.pacman_x))
    self.pacman_y = max(10, min(ALTURA - 10, self.pacman_y))

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
      self.direcao_atual = self.proxima_direcao

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
