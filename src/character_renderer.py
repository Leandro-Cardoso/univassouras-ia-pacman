"""Renderização vetorial de Pac-Man, fantasmas e efeitos de captura.

Só depende de `math`; o módulo `pygame` é passado como argumento em cada
método, o que mantém o arquivo reutilizável em qualquer variação do jogo
(mapas 28×31 do game.py modular, mapas 28×21 do protótipo com CSV, etc.).

Convenção de coordenadas: `pos` é sempre (coluna, linha) em unidades de
célula (float), e `tile` é o tamanho da célula em pixels. Isso permite
interpolar a posição (ex.: 13.4 → 13.5) para animação suave em 60 FPS.
"""
import math


class CharacterRenderer:
    GHOST_COLORS = {
        'blinky': (235, 45, 55),
        'pinky':  (255, 145, 190),
        'inky':   (60, 220, 235),
        'clyde':  (255, 165, 45),
    }
    DIRECTIONS = {
        'right': 0.0,
        'down':  math.pi / 2,
        'left':  math.pi,
        'up':    -math.pi / 2,
    }
    PACMAN_COLOR = (255, 220, 0)
    FRIGHTENED_COLOR = (45, 75, 245)

    # ------------------------------------------------------------------ Pac-Man

    @staticmethod
    def draw_pacman(surface, pygame, pos, tile, direction='left', frame=0,
                    offset_y=0, death_progress=None):
        """Desenha o Pac-Man como um polígono com boca animada.

        `death_progress` (0..1) fecha a boca e encolhe o personagem até
        desaparecer — usado durante a animação de morte.
        """
        cx = int(round(pos[0] * tile + tile // 2))
        cy = int(round(offset_y + pos[1] * tile + tile // 2))
        radius = max(1, tile // 2 - 2)

        # Aceita strings ('left') ou objetos com .value (Direction.LEFT).
        angle = CharacterRenderer.DIRECTIONS.get(
            getattr(direction, 'value', direction), math.pi
        )

        if death_progress is not None:
            progress = max(0.0, min(1.0, death_progress))
            radius = max(1, int(radius * (1.0 - progress) ** 0.72))
            mouth = min(math.pi * 0.96, 0.08 + progress * math.pi * 0.88)
        else:
            # Ciclo independente do FPS — baseado no contador de quadros.
            mouth = 0.08 + 0.42 * abs(math.sin(frame * 0.28))

        start = angle + mouth
        end = angle + 2 * math.pi - mouth
        points = [(cx, cy)]
        steps = 32
        for i in range(steps + 1):
            a = start + (end - start) * i / steps
            points.append((cx + math.cos(a) * radius, cy + math.sin(a) * radius))

        pygame.draw.polygon(surface, CharacterRenderer.PACMAN_COLOR, points)

    # ------------------------------------------------------------------ Fantasma

    @staticmethod
    def draw_ghost(surface, pygame, pos, tile, name, direction='left',
                   frightened=False, eaten=False, frame=0, offset_y=0):
        """Desenha um fantasma com base ondulada animada e olhos direcionais.

        `eaten=True` desenha apenas os olhos (fantasma voltando para a casa).
        `frightened=True` pinta de azul e adiciona a boca trêmula.
        """
        cx = int(round(pos[0] * tile + tile // 2))
        cy = int(round(offset_y + pos[1] * tile + tile // 2))
        r = tile // 2 - 2

        color = (
            CharacterRenderer.FRIGHTENED_COLOR if frightened
            else CharacterRenderer.GHOST_COLORS.get(name, (235, 45, 55))
        )

        if not eaten:
            # Corpo: semicírculo superior + retângulo central
            pygame.draw.circle(surface, color, (cx, cy - 2), r)
            pygame.draw.rect(surface, color, (cx - r, cy - 2, 2 * r, r))

            # Base ondulada (dois estados alternados)
            wave = max(2, tile // 6)
            base = [(cx - r, cy + r - 2)]
            count = 4
            for i in range(count + 1):
                x = cx - r + (2 * r * i / count)
                y = cy + r - 2 + (wave if (i + frame // 7) % 2 else 0)
                base.append((x, y))
            base.extend([
                (cx + r, cy + r - 2),
                (cx + r, cy - 2),
                (cx - r, cy - 2),
            ])
            pygame.draw.polygon(surface, color, base)

        # Olhos (sempre visíveis, mesmo quando "eaten")
        eye_y = cy - 2
        eye_dx = max(4, tile // 6)
        pupil_offset = {
            'right': (2, 0),
            'left':  (-2, 0),
            'up':    (0, -2),
            'down':  (0, 2),
        }.get(getattr(direction, 'value', direction), (0, 0))

        for ex in (cx - eye_dx, cx + eye_dx):
            pygame.draw.ellipse(
                surface, (250, 250, 250), (ex - 4, eye_y - 6, 8, 12)
            )
            pygame.draw.circle(
                surface, (20, 35, 90),
                (ex + pupil_offset[0], eye_y + pupil_offset[1]),
                2,
            )

        # Boca trêmula do modo assustado
        if frightened and not eaten and (frame // 8) % 2:
            pygame.draw.arc(
                surface, (255, 255, 255),
                (cx - 7, cy + 4, 14, 7), 0, math.pi, 2,
            )

    # ------------------------------------------------------------- Efeito visual

    @staticmethod
    def draw_capture_effect(surface, pygame, pos, tile, points, progress,
                            offset_y=0):
        """Efeito curto de captura: anel expansivo + pontuação flutuante.

        `progress` vai de 0 (início) a 1 (desapareceu). É usado quando o
        Pac-Man come um fantasma no modo assustado.
        """
        progress = max(0.0, min(1.0, progress))
        cx = int(round(pos[0] * tile + tile // 2))
        cy = int(round(offset_y + pos[1] * tile + tile // 2))

        radius = max(2, int(5 + progress * tile * 0.72))
        alpha = int(220 * (1.0 - progress))

        layer = pygame.Surface((tile * 3, tile * 2), pygame.SRCALPHA)
        center = (tile * 3 // 2, tile)
        pygame.draw.circle(
            layer, (120, 210, 255, alpha), center, radius, 2
        )

        font = pygame.font.Font(None, 19)
        label = font.render(str(points), True, (255, 255, 255))
        label.set_alpha(alpha)
        layer.blit(
            label,
            label.get_rect(
                center=(center[0], center[1] - 12 - int(progress * 16))
            ),
        )
        surface.blit(layer, (cx - center[0], cy - center[1]))


# ---------------------------------------------------------------------------
# Demonstração isolada: `python character_renderer.py` abre uma janela com
# os 4 fantasmas (normal, assustado, comido, em movimento) e o Pac-Man em 4
# direções + animação de morte.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import pygame

    pygame.init()
    TILE = 40
    screen = pygame.display.set_mode((9 * TILE, 3 * TILE))
    pygame.display.set_caption("CharacterRenderer — teste")
    clock = pygame.time.Clock()

    running = True
    frame = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((5, 5, 18))
        frame += 1

        # Pac-Man nas quatro direções
        for i, d in enumerate(("right", "down", "left", "up")):
            CharacterRenderer.draw_pacman(
                screen, pygame, (i + 0.5, 0.5), TILE, d, frame
            )

        # Fantasmas: normal, assustado, comido, boca trêmula
        for i, name in enumerate(("blinky", "pinky", "inky", "clyde")):
            CharacterRenderer.draw_ghost(
                screen, pygame, (i + 0.5, 1.5), TILE, name, "down",
                frightened=(i == 1),
                eaten=(i == 2),
                frame=frame,
            )

        # Efeito de captura progredindo no tempo
        prog = (frame % 120) / 120.0
        CharacterRenderer.draw_capture_effect(
            screen, pygame, (4.5, 2.5), TILE, 200, prog
        )

        # Animação de morte do Pac-Man no canto
        CharacterRenderer.draw_pacman(
            screen, pygame, (8.0, 2.5), TILE, "left", frame,
            death_progress=prog,
        )

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()