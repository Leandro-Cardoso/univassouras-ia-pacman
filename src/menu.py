import csv
import os
import pygame

PRETO = (5, 5, 18)
AMARELO = (255, 220, 0)
BRANCO = (245, 245, 245)
CIANO = (0, 255, 255)
VERDE = (46, 204, 113)
CINZA_INPUT = (35, 35, 60)
BORDA_INPUT = (65, 135, 255)

def carregar_ranking(arquivo="scores.csv"):
    ranking = []
    if os.path.exists(arquivo):
        try:
            with open(arquivo, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    ranking.append(row)
        except Exception:
            pass
    return ranking


def salvar_ranking(nome, pontuacao, tempo, arquivo="scores.csv"):
    ranking = carregar_ranking(arquivo)
    ranking.append({"Nome": nome, "Pontuacao": str(pontuacao), "Tempo": str(tempo)})
    ranking = sorted(ranking, key=lambda x: int(x["Pontuacao"]), reverse=True)[:5]
    
    with open(arquivo, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Nome", "Pontuacao", "Tempo"])
        writer.writeheader()
        writer.writerows(ranking)


def menu_principal(tela, largura):
    font_titulo = pygame.font.Font(None, 44)
    font_texto = pygame.font.Font(None, 22)
    
    nome_jogador = "Player1"
    ativo_input = True  # Começa focado no input de nome

    rodando_menu = True
    while rodando_menu:
        tela.fill(PRETO)
        
        # Título
        titulo = font_titulo.render("PAC-MAN — MENU PRINCIPAL", True, AMARELO)
        tela.blit(titulo, (largura // 2 - titulo.get_width() // 2, 25))

        # Caixa de Digitação do Nome
        label_nome = font_texto.render("Digite seu Nome:", True, BRANCO)
        tela.blit(label_nome, (largura // 2 - 140, 75))

        input_rect = pygame.Rect(largura // 2 - 140, 100, 280, 36)
        pygame.draw.rect(tela, CINZA_INPUT, input_rect, border_radius=6)
        pygame.draw.rect(tela, BORDA_INPUT if ativo_input else BRANCO, input_rect, 2, border_radius=6)

        txt_surface = font_texto.render(nome_jogador, True, AMARELO if ativo_input else BRANCO)
        tela.blit(txt_surface, (input_rect.x + 10, input_rect.y + 8))

        # Instrução para iniciar
        instrucao = font_texto.render("Pressione [ENTER] para Jogar | [ESC] para Sair", True, VERDE)
        tela.blit(instrucao, (largura // 2 - instrucao.get_width() // 2, 150))

        # Quadro de Pontuações (Leaderboard)
        rank_titulo = font_texto.render("--- MELHORES PONTUAÇÕES (RANKING) ---", True, CIANO)
        tela.blit(rank_titulo, (largura // 2 - rank_titulo.get_width() // 2, 195))

        ranking = carregar_ranking()
        if not ranking:
            vazio = font_texto.render("Nenhuma partida registrada ainda.", True, BRANCO)
            tela.blit(vazio, (largura // 2 - vazio.get_width() // 2, 235))
        else:
            header = font_texto.render(f"{'Pos':<4} {'Nome':<12} {'Pontos':<10} {'Tempo'}", True, AMARELO)
            tela.blit(header, (70, 230))
            for i, r in enumerate(ranking):
                linha_txt = font_texto.render(f"{i+1}º   {r['Nome']:<12} {r['Pontuacao']:<10} {r['Tempo']}", True, BRANCO)
                tela.blit(linha_txt, (70, 260 + i * 26))

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    if nome_jogador.strip():
                        rodando_menu = False
                elif evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
                elif evento.key == pygame.K_BACKSPACE:
                    if ativo_input:
                        nome_jogador = nome_jogador[:-1]
                else:
                    if ativo_input and len(nome_jogador) < 12:
                        nome_jogador += evento.unicode

    return nome_jogador.strip() if nome_jogador.strip() else "Player1"
