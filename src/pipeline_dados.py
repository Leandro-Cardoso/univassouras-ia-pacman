import os
import pandas as pd

class PipelineDados:
  def __init__(self, caminho_csv="dataset_pacman.csv"):
    self.caminho_csv = caminho_csv
    self.df = None
    self.df_limpo = None

  def carregar_dados(self):
    if not os.path.exists(self.caminho_csv):
      raise FileNotFoundError(
          f"O arquivo {self.caminho_csv} não foi encontrado. Jogue um pouco"
          " primeiro!"
      )

    # Carregar o CSV
    self.df = pd.read_csv(self.caminho_csv, sep=",", encoding="utf-8")
    print(f"[INFO] Dados carregados. Dimensões originais: {self.df.shape}")
    return self.df

  def explorar_dados(self):
    if self.df is None:
      self.carregar_dados()

    # Verificacão
    print("\n--- Informações do DataFrame (df.info) ---")
    print(self.df.info())

    print("\n--- Estatísticas Descritivas (df.describe) ---")
    print(self.df.describe())

    print("\n--- Valores Ausentes (NaN) ---")
    print(self.df.isna().sum())

    print(f"Duplicatas encontradas: {self.df.duplicated().sum()}")

  def limpar_dados(self):
    # Remover linhas duplicadas
    self.df_limpo = self.df.drop_duplicates().copy()

    # Tratamento de valores ausentes
    self.df_limpo = self.df_limpo.dropna()

    print(
        f"[INFO] Limpeza concluída. Dimensões após limpeza:"
        f" {self.df_limpo.shape}"
    )
    return self.df_limpo

  def preparar_features_target(self):
    if self.df_limpo is None:
      self.limpar_dados()

    # Variáveis preditoras (X) da resposta (y)
    features = [
        "pacman_x",
        "pacman_y",
        "fantasma_dist_min",
        "modo_medo",
        "ultimas_direcoes",
    ]
    target = "proxima_direcao_jogador"

    X = self.df_limpo[features]
    y = self.df_limpo[target]

    print(f"[INFO] Features (X) shape: {X.shape}, Target (y) shape: {y.shape}")
    return X, y

if __name__ == "__main__":
  pipeline = PipelineDados()
  pipeline.carregar_dados()
  pipeline.explorar_dados()
  pipeline.limpar_dados()
  pipeline.preparar_features_target()
