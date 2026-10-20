import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from game import PacmanGame
from modelo_ia import ModeloIA

def test_modelo_ia():
  # Gera um dataset para testes
  caminho_teste = "dataset_teste_modelo.csv"
  jogo = PacmanGame()
  
  # Simula várias direções para gerar linhas suficientes para o split 80/20
  direcoes = ["Cima", "Baixo", "Esquerda", "Direita", "Cima", "Direita", "Baixo", "Esquerda", "Cima", "Baixo"]
  for direcao in direcoes:
    jogo.proxima_direcao = direcao
    jogo.atualizar_posicao()
    
  jogo.salvar_dataset(caminho_teste)

  # Treinamento e a avaliação
  ia = ModeloIA(caminho_teste)
  modelo, acuracia = ia.treinar_e_avaliar()

  assert modelo is not None
  assert 0.0 <= acuracia <= 1.0

  # Limpeza
  if os.path.exists(caminho_teste):
    os.remove(caminho_teste)

  print("[SUCESSO] Todos os testes da Etapa 3 passaram com sucesso!")

if __name__ == "__main__":
  test_modelo_ia()
