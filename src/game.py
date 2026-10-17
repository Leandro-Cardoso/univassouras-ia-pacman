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

# Relógio para controlar os FPS
CLOCK = pygame.time.Clock()
FPS = 30

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
    x_antigo, y_antigo = self.pacman_x, self.pacman_y

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

    if movendo:
      self.direcao_atual = self.proxima_direcao

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
          "ultimas_direcoes": self.direcao_atual,
          "proxima_direcao_jogador": self.proxima_direcao,
      })

  def desenhar(self):
    TELA.fill(PRETO)

    # Desenhar Pacman
    pygame.draw.circle(
        TELA, AMARELO, (self.pacman_x, self.pacman_y), 20
    )

    # Desenhar Fantasma
    pygame.draw.circle(
        TELA, VERMELHO, (self.fantasma_x, self.fantasma_y), 20
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
