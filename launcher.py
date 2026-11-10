"""Ponto de entrada para o PyInstaller.

Roda o jogo como pacote, preservando os imports relativos de src/.
"""
from src.game import main

if __name__ == "__main__":
    main()