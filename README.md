# Pacman com IA

Este projeto consiste em desenvolver um jogo do Pacman em Python para gerar dados próprios das partidas e aplicar técnicas de Inteligência Artificial, limpando os dados, definindo o que será previsto e treinando um modelo para antecipar as jogadas do jogador.

## Integrantes

* Leandro Lima Cardoso (202323366)
* João Vitor Afonso Damascena (202312489)
* Emanuele Gomez (202323327)
* Almir Coelho Rubim Junior (202312480)

## Visão Geral do Projeto

*   **Problema a Resolver:** Prever o movimento do jogador e antecipar sua jogada e dividindo os fantasmas entre as possiveis rotas mais provaveis com base nas variáveis dinâmicas do jogo e na posição espacial do jogador e dos fantasmas.

*   **Tecnologias Utilizadas:** 
    *   **Jogo:** Python (`Pygame` para a interface e lógica do jogo).

    *   **Análise e IA:** Jupyter Notebook, `Pandas`, `NumPy`, `Scikit-learn` e `Matplotlib`.

## Arquitetura do Sistema

A arquitetura do projeto divide-se em três grandes camadas: o **Ambiente (Geração de Dados)**, a **Camada de Dados (Pipeline)** e a **Camada de Inteligência (Machine Learning)**.

```text
 ┌────────────────────────────────────────────────────────┐
 |               1. CAMADA DE JOGO (Pygame)               |
 |  - Simulação do Pacman & Fantasmas                     |
 |  - Captura de telemetria em tempo real (Frames)        |
 └───────────────────────────┬────────────────────────────┘
                             │ Exporta histórico
                             ▼
 ┌────────────────────────────────────────────────────────┐
 |           2. CAMADA DE DADOS (CSV / Pandas)            |
 |  - Arquivo: dataset_pacman.csv                         |
 |  - Limpeza (Tratamento de nulos/duplicados)            |
 |  - Engenharia de Features (X) e Target (y)             |
 └───────────────────────────┬────────────────────────────┘
                             │ Treinamento / Teste (80/20)
                             ▼
 ┌────────────────────────────────────────────────────────┐
 |          3. CAMADA DE MACHINE LEARNING (Scikit-learn)  |
 |  - Modelo de Classificação (Árvore de Decisão / RF)    |
 |  - Avaliação de Acurácia e Matriz de Confusão          |
 |  - Previsão de Risco de Morte em Tempo de Jogo         |
 └────────────────────────────────────────────────────────┘
```

## Etapas de Desenvolvimento

Etapa 1: Jogo e a Geração de Dados:

* Criar o labirinto básico, o movimento do Pacman pelas setas do teclado e a patrulha dos fantasmas.

* Em cada loop do jogo (while running), extrair as coordenadas e salvar em uma lista que, ao fim da partida, é convertida e salva como dataset_pacman.csv.

* Otimização de Coleta: Extrair e salvar os dados apenas no intervalo de tempo em que o jogador se move (na sua velocidade de quadros/passos), evitando gerar dados repetidos de quando o jogador está parado.

---

Etapa 2: Análise Exploratória e Limpeza (Pandas):

1. Carregar o CSV com pd.read_csv().

2. Verificar dimensões, tipos de dados (df.info()) e estatísticas descritivas (df.describe()).

3. Remover eventuais linhas duplicadas ou registros corrompidos (df.drop_duplicates()).

4. Separar as variáveis preditoras ($X$) da resposta ($y$):

4. Separar as variáveis preditoras ($X$) da resposta ($y$):

    * Features ($X$): pacman_x, pacman_y, fantasma_dist_min, modo_medo, ultimas_direcoes.
    
    * Target ($y$): proxima_direcao_jogador (ex: Cima, Baixo, Esquerda, Direita).

---

Etapa 3: Modelagem e Validação (Scikit-learn)

1. Divisão de Treino e Teste: Separar 80% dos dados para treino e 20% para teste (evitando o overfitting por memorização).

2. Treinamento: Utilizar um modelo de classificação simples e eficiente, como a Árvore de Decisão (DecisionTreeClassifier) ou Random Forest, para classificar a próxima direção mais provável do Pacman.

3. Avaliação: Medir a acurácia do modelo e analisar se ele consegue antecipar com precisão as escolhas de rota do jogador para orientar a inteligência dos fantasmas.

## Build

```cmd
pip install pyinstaller
```

```cmd
pyinstaller --onefile --noconsole src/game.py
```
