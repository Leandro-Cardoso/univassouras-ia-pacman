import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import pandas as pd
from game import PacmanGame
from pipeline_dados import PipelineDados

def test_pipeline_dados():
  # Gera um dataset para testes
  caminho_teste = "dataset_teste_pipeline.csv"
  jogo = PacmanGame()
  jogo.proxima_direcao = "Cima"
  jogo.atualizar_posicao()
  jogo.proxima_direcao = "Esquerda"
  jogo.atualizar_posicao()
  jogo.salvar_dataset(caminho_teste)

  # Pipeline de carregamento e limpeza
  pipeline = PipelineDados(caminho_teste)
  df = pipeline.carregar_dados()
  assert not df.empty

  df_limpo = pipeline.limpar_dados()
  assert len(df_limpo) > 0

  X, y = pipeline.preparar_features_target()
  assert "pacman_x" in X.columns
  assert len(X) == len(y)

  # Limpeza
  if os.path.exists(caminho_teste):
    os.remove(caminho_teste)

  print("[SUCESSO] Todos os testes da Etapa 2 passaram com sucesso!")

if __name__ == "__main__":
  test_pipeline_dados()
