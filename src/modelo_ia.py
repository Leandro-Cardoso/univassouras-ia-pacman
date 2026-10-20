import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
from pipeline_dados import PipelineDados

class ModeloIA:

  def __init__(self, caminho_csv="dataset_pacman.csv"):
    self.pipeline = PipelineDados(caminho_csv)
    self.modelo = DecisionTreeClassifier(random_state=42)
    self.le_ultimas = LabelEncoder()
    self.le_target = LabelEncoder()

  def preparar_dados_ml(self):
    X, y = self.pipeline.preparar_features_target()
    
    # Transformacão em números de 'ultimas_direcoes' e o target
    X = X.copy()
    X["ultimas_direcoes"] = self.le_ultimas.fit_transform(X["ultimas_direcoes"])
    y_encoded = self.le_target.fit_transform(y)

    return X, y_encoded

  def treinar_e_avaliar(self):
    X, y = self.preparar_dados_ml()

    if len(X) < 5:
      print("[AVISO] Poucos dados para treinar com segurança. Jogue um pouco mais!")
      return None

    # Treino e Testes (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Treinamento com Árvore de Decisão
    self.modelo.fit(X_train, y_train)

    # Métricas
    y_pred = self.modelo.predict(X_test)
    acuracia = accuracy_score(y_test, y_pred)

    print(f"\n[INFO] Treinamento concluído com sucesso!")
    print(f"Acurácia do Modelo: {acuracia * 100:.2f}%")
    print("\n--- Relatório de Classificação ---")
    print(classification_report(y_test, y_pred, zero_division=0))

    return self.modelo, acuracia

if __name__ == "__main__":
  ia = ModeloIA()
  ia.treinar_e_avaliar()
