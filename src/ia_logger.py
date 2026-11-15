import csv
import os
from menu import salvar_ranking

class IALogger:
    def __init__(self, nome_jogador, caminho_csv="dataset_pacman.csv"):
        self.nome_jogador = nome_jogador
        self.caminho_csv = caminho_csv

    def salvar_dataset(self, dados_telemetria, morreu, pos_morte_x, pos_morte_y, pontuacao, frame, fps):
        if not dados_telemetria:
            return
        
        if morreu and dados_telemetria:
            dados_telemetria[-1]["ia_sucesso_captura"] = 1
            dados_telemetria[-1]["pos_morte_x"] = pos_morte_x
            dados_telemetria[-1]["pos_morte_y"] = pos_morte_y

        existe = os.path.exists(self.caminho_csv)
        chaves = dados_telemetria[0].keys()
        
        with open(self.caminho_csv, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=chaves)
            if not existe:
                writer.writeheader()
            writer.writerows(dados_telemetria)
        
        tempo_total = round(frame / fps, 1)
        salvar_ranking(self.nome_jogador, pontuacao, f"{tempo_total}s")
        print(f"[INFO] Dataset atualizado e pontuação salva!")
