"""Módulo de Telemetria, Registro de Dataset e HUD de Depuração da IA.
Este módulo gerencia duas responsabilidades principais:
1. Salvar os dados de telemetria em formato CSV (`dataset_pacman.csv`) para treinamento e análise dos modelos de Machine Learning.
2. Renderizar o painel HUD (Heads-Up Display) estilizado na tela do jogo, exibindo em tempo real as decisões da IA, pontuação e estados dinâmicos destacados com as cores correspondentes a cada fantasma.
"""

import csv
import os
from menu import salvar_ranking

class IALogger:
    def __init__(self, nome_jogador, caminho_csv="dataset_pacman.csv"):
        self.nome_jogador = nome_jogador
        self.caminho_csv = caminho_csv

    def salvar_dataset(self, dados_telemetria, morreu, pos_morte_x, pos_morte_y, pontuacao, frame, fps):
        """Salva o dataset acumulado em CSV e atualiza o ranking de pontuações."""
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

    def desenhar_hud_ia(self, tela, pygame, largura, altura, frame, fps, pontuacao, fase, modo_medo, timer_medo, fantasmas, pacman_y, pausado):
        """Renderiza um painel HUD flutuante avançado na tela do jogo.

        Utiliza cores exclusivas para cada fantasma (Blinky em vermelho, Pinky em rosa,
        Inky em ciano e Clyde em laranja), além de destacar a pontuação e os estados
        de modo com tamanhos de fonte maiores para melhor legibilidade.
        """
        # Inicializa fontes de tamanhos diferentes se ainda não existirem
        if not hasattr(self, '_font_titulo'):
            self._font_titulo = pygame.font.Font(None, 17)
            self._font_corpo = pygame.font.Font(None, 15)
            self._font_destaque = pygame.font.Font(None, 19)

        tempo_seg = round(frame / fps, 1)
        
        COR_FUNDO = (10, 10, 30, 235)
        COR_BORDA = (65, 135, 255)
        
        # Cores características dos fantasmas para identificação visual imediata
        CORES_FANTASMAS = {
            'blinky': (235, 45, 55),   # Vermelho
            'pinky':  (255, 145, 190), # Rosa
            'inky':   (60, 220, 235),  # Ciano
            'clyde':  (255, 165, 45)   # Laranja
        }

        # Estrutura de blocos para gerenciar espaçamentos e separações limpas
        blocos_hud = []

        # Bloco 1: Identificação, Tempo, Fase e Estado do Jogo (separados)
        bloco_jogador = []
        bloco_jogador.append((f"JOGADOR: {self.nome_jogador.upper()}", (245, 245, 245), self._font_titulo))
        bloco_jogador.append((f"TEMPO: {tempo_seg}s    |    FASE: {fase}", (200, 210, 235), self._font_corpo))
        if pausado:
            bloco_jogador.append(("ESTADO: PAUSADO", (255, 100, 100), self._font_destaque))
        else:
            bloco_jogador.append(("ESTADO: JOGANDO", (100, 255, 150), self._font_corpo))
        blocos_hud.append(bloco_jogador)

        # Bloco 2: Pontuação Destacada
        bloco_pontos = []
        bloco_pontos.append((f"PONTUACAO: {pontuacao} PONTOS", (255, 220, 0), self._font_destaque))
        if modo_medo:
            tempo_medo_seg = round(timer_medo / fps, 1)
            bloco_pontos.append((f"MODO MEDO ATIVO: {tempo_medo_seg}s", (45, 120, 255), self._font_destaque))
        blocos_hud.append(bloco_pontos)

        # Bloco 3: Estados e Táticas da IA dos Fantasmas
        bloco_ia = []
        bloco_ia.append(("--- TATICAS E ESTADOS DA IA ---", (160, 170, 210), self._font_titulo))
        for nome, f_data in fantasmas.items():
            cor_fantasma = CORES_FANTASMAS.get(nome, (245, 245, 245))
            txt_fantasma = f"{nome.capitalize()}: {f_data['estado']} | Dist: {f_data['dist_alvo']}px"
            bloco_ia.append((txt_fantasma, cor_fantasma, self._font_corpo))
        blocos_hud.append(bloco_ia)

        # Cálculo dinâmico da altura total considerando os espaçamentos entre blocos
        padding_vertical = 10
        espaco_entre_blocos = 10
        altura_conteudo = 0
        
        for bloco in blocos_hud:
            for _, _, fonte in bloco:
                altura_conteudo += 18 if fonte == self._font_corpo else 22
            altura_conteudo += espaco_entre_blocos # margem inferior de cada bloco

        box_width = 440
        box_height = (padding_vertical * 2) + altura_conteudo
        
        hud_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        hud_surface.fill(COR_FUNDO)
        pygame.draw.rect(hud_surface, COR_BORDA, hud_surface.get_rect(), 1, border_radius=6)

        # Renderização organizada dos blocos com espaçamento limpo
        y_offset = padding_vertical
        for bloco_idx, bloco in enumerate(blocos_hud):
            for texto, cor, fonte in bloco:
                txt_surface = fonte.render(texto, True, cor)
                hud_surface.blit(txt_surface, (12, y_offset))
                y_offset += 18 if fonte == self._font_corpo else 22
            
            # Adiciona respiro visual extra entre blocos distintos (exceto no último)
            if bloco_idx < len(blocos_hud) - 1:
                y_offset += 6

        # Posicionamento inteligente (evita cobrir o Pac-Man)
        pos_x = 10
        pos_y = altura - box_height - 10 if pacman_y < (altura / 2) else 10
        
        tela.blit(hud_surface, (pos_x, pos_y))
