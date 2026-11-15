"""Módulo de Inteligência Artificial e Pathfinding (BFS) dos Fantasmas.
Responsável por calcular os caminhos no labirinto usando o algoritmo BFS, gerenciar a saída da base, o modo de medo (fuga) e estratégias avançadas de cerco e predição de movimento baseadas no comportamento do Pac-Man.
"""

from collections import deque
import random

# Direções opostas para evitar que o fantasma recupere o caminho imediatamente
OPOSTOS = {
    "Cima": "Baixo",
    "Baixo": "Cima",
    "Esquerda": "Direita",
    "Direita": "Esquerda",
}

def calcular_proximo_passo_bfs(
    mapa,
    inicio_x,
    inicio_y,
    destino_x,
    destino_y,
    dir_atual,
    dentro_casa=False,
    grid_size=20,
    tunnel_row=14,
):
  """Calcula o passo seguinte utilizando o algoritmo de busca em largura (BFS).

  Retorna a direção ideal ('Cima', 'Baixo', 'Esquerda' ou 'Direita') para
  alcançar o destino.
  """
  inicio_col = max(0, min(len(mapa[0]) - 1, int(inicio_x // grid_size)))
  inicio_lin = max(0, min(len(mapa) - 1, int(inicio_y // grid_size)))
  dest_col = max(0, min(len(mapa[0]) - 1, int(destino_x // grid_size)))
  dest_lin = max(0, min(len(mapa) - 1, int(destino_y // grid_size)))

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

  def celula_livre_local(c, l):
    if l == tunnel_row and (c < 0 or c >= len(mapa[0])):
      return True
    if 0 <= l < len(mapa) and 0 <= c < len(mapa[0]):
      char = mapa[l][c]
      if char == "W":
        return False
      if char == "G":
        return dentro_casa
      return True
    return False

  for d_nome, dc, dl in movs:
    if d_nome == oposto:
      continue
    nc, nl = inicio_col + dc, inicio_lin + dl
    if 0 <= nl < len(mapa) and 0 <= nc < len(mapa[0]):
      if celula_livre_local(nc, nl):
        fila.append((nc, nl, d_nome))
        visitados.add((nc, nl))

  while fila:
    c, l, primeiro_passo = fila.popleft()
    if (c, l) == (dest_col, dest_lin):
      return primeiro_passo

    for d_nome, dc, dl in movs:
      nc, nl = c + dc, l + dl
      if 0 <= nl < len(mapa) and 0 <= nc < len(mapa[0]):
        if celula_livre_local(nc, nl) and (nc, nl) not in visitados:
          visitados.add((nc, nl))
          fila.append((nc, nl, primeiro_passo))
  return None


def atualizar_fantasmas_ia(JogoInstance):
  """Atualiza os estados e calcula alvos estratégicos de cerco e predição

  para cada fantasma com base na posição e histórico de movimento do Pac-Man.
  """
  if JogoInstance.modo_medo_ativo:
    JogoInstance.timer_medo -= 1
    if JogoInstance.timer_medo <= 0:
      JogoInstance.modo_medo_ativo = False
      JogoInstance.velocidade = JogoInstance.velocidade_normal

  px, py = JogoInstance.pacman_x, JogoInstance.pacman_y
  p_dir = JogoInstance.direcao_atual
  gs = JogoInstance.GRID_SIZE

  # 1. PREDIÇÃO DE TRAJETÓRIA (Antecipa para onde o Pac-Man está olhando)
  ahead_x, ahead_y = px, py
  alcance_emboscada = 4 * gs
  if p_dir == "Cima":
    ahead_y -= alcance_emboscada
  elif p_dir == "Baixo":
    ahead_y += alcance_emboscada
  elif p_dir == "Esquerda":
    ahead_x -= alcance_emboscada
  elif p_dir == "Direita":
    ahead_x += alcance_emboscada

  # 2. DEFINIÇÃO DE ALVOS INDIVIDUAIS PARA CERCO COORDENADO
  alvos_estrategicos = {}

  # Blinky (Vermelho): Perseguição direta (Calcanhar do Pac-Man)
  alvos_estrategicos["blinky"] = (px, py, "Ataque Direto 🎯")

  # Pinky (Rosa): Emboscada (Tenta cortar a frente prevendo o destino)
  alvos_estrategicos["pinky"] = (ahead_x, ahead_y, "Emboscada Frontal ⚡")

  # Inky (Ciano): Cerco Flanqueado (Usa o Blinky como pivô para fechar o ângulo)
  bx = JogoInstance.fantasmas["blinky"]["x"]
  by = JogoInstance.fantasmas["blinky"]["y"]
  flanco_x = px + (px - bx)
  flanco_y = py + (py - by)
  alvos_estrategicos["inky"] = (flanco_x, flanco_y, "Flanco Cruzado 🔄")

  # Clyde (Laranja): Cerco Inteligente (Se afasta se estiver muito perto, cerca se longe)
  cx_pos = JogoInstance.fantasmas["clyde"]["x"]
  cy_pos = JogoInstance.fantasmas["clyde"]["y"]
  dist_clyde = ((cx_pos - px) ** 2 + (cy_pos - py) ** 2) ** 0.5
  if dist_clyde < 5 * gs:
    # Recua para o canto inferior esquerdo se chegar muito perto
    alvos_estrategicos["clyde"] = (
        2 * gs,
        JogoInstance.ALTURA - 2 * gs,
        "Patrulha Tática 🛡️",
    )
  else:
    alvos_estrategicos["clyde"] = (px, py, "Cerco Retaguarda 🏴‍☠️")

  # 3. ATUALIZAÇÃO DA MOVIMENTAÇÃO DE CADA FANTASMA
  for nome, f_data in JogoInstance.fantasmas.items():
    lin_atual = int(f_data["y"] // gs)
    dentro_casa = 12 <= lin_atual <= 14

    if dentro_casa:
      if JogoInstance.frame < f_data["timer_saida"]:
        f_data["estado"] = "Aguardando Saída"
        continue
      alvo_x, alvo_y = (13 * gs + gs // 2, 11 * gs + gs // 2)
      f_data["estado"] = "Saindo da Casa"
    elif JogoInstance.modo_medo_ativo:
      alvo_x, alvo_y = JogoInstance.centro_casa_fantasmas
      f_data["estado"] = "Fuginho p/ Casa 😨"
    else:
      alvo_x, alvo_y, descricao_estado = alvos_estrategicos[nome]
      f_data["estado"] = descricao_estado

    f_data["dist_alvo"] = int(
        ((f_data["x"] - alvo_x) ** 2 + (f_data["y"] - alvo_y) ** 2) ** 0.5
    )

    # Executa o pathfinding otimizado por BFS nas interseções do labirinto
    if JogoInstance.no_centro_celula(f_data["x"], f_data["y"], tolerancia=1):
      f_data["x"], f_data["y"] = JogoInstance.alinhar_ao_centro(
          f_data["x"], f_data["y"]
      )
      proximo = calcular_proximo_passo_bfs(
          JogoInstance.mapa,
          f_data["x"],
          f_data["y"],
          alvo_x,
          alvo_y,
          f_data["dir"],
          dentro_casa,
          gs,
          JogoInstance.TUNNEL_ROW,
      )
      if proximo and JogoInstance.pode_mover(
          f_data["x"], f_data["y"], proximo, dentro_casa
      ):
        f_data["dir"] = proximo
      else:
        oposto = OPOSTOS.get(f_data["dir"])
        livres = [
            d
            for d in ("Cima", "Baixo", "Esquerda", "Direita")
            if JogoInstance.pode_mover(f_data["x"], f_data["y"], d, dentro_casa)
        ]
        escolhas = [d for d in livres if d != oposto] or livres
        if escolhas:
          f_data["dir"] = random.choice(escolhas)

    if JogoInstance.pode_mover(f_data["x"], f_data["y"], f_data["dir"], dentro_casa):
      dx, dy = JogoInstance.obter_delta(f_data["dir"])
      f_data["x"] += dx
      f_data["y"] += dy

    if (
        JogoInstance.TUNNEL_ROW * gs <= f_data["y"] < (JogoInstance.TUNNEL_ROW + 1) * gs
    ):
      f_data["x"] = f_data["x"] % JogoInstance.LARGURA
