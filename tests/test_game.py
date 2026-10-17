import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from game import PacmanGame

def test_coleta_e_salvamento_dataset():
  # Instancia o jogo sem abrir a janela gráfica para testes automatizados headless
  os.environ["SDL_VIDEODRIVER"] = "dummy"

  jogo = PacmanGame()
  jogo.proxima_direcao = "Direita"
  jogo.atualizar_posicao()

  # Garante que gerou pelo menos 1 registro de telemetria ao se mover
  assert len(jogo.dados_telemetria) == 1
  registro = jogo.dados_telemetria[0]
  assert registro["proxima_direcao_jogador"] == "Direita"
  assert "pacman_x" in registro
  assert "fantasma_dist_min" in registro

  # Testa a exportação do arquivo CSV
  caminho_teste = "dataset_teste.csv"
  jogo.salvar_dataset(caminho_teste)

  assert os.path.exists(caminho_teste)

  # Limpeza do arquivo de teste
  if os.path.exists(caminho_teste):
    os.remove(caminho_teste)

  print("[SUCESSO] Todos os testes da Etapa 1 passaram com sucesso!")

if __name__ == "__main__":
  test_coleta_e_salvamento_dataset()
