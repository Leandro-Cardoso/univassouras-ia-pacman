"""Renderização vetorial de Pac-Man, fantasmas e efeitos de captura."""
import math

class CharacterRenderer:
    GHOST_COLORS = {
        'blinky': (235, 45, 55),
        'pinky':  (255, 145, 190),
        'inky':   (60, 220, 235),
        'clyde':  (255, 165, 45),
    }
    DIRECTIONS = {
        'Direita': 0.0,
        'Baixo':  math.pi / 2,
        'Esquerda':  math.pi,
        'Cima':    -math.pi / 2,
        'right': 0.0,
        'down':  math.pi / 2,
        'left':  math.pi,
        'up':    -math.pi / 2,
    }
    PACMAN_COLOR = (255, 220, 0)
    FRIGHTENED_COLOR = (45, 75, 245)

    @staticmethod
    def draw_pacman(surface, pygame, pos, tile, direction='left', frame=0,
                    offset_y=0, death_progress=None):
        cx = int(round(pos[0] * tile + tile // 2))
        cy = int(round(offset_y + pos[1] * tile + tile // 2))
        radius = max(1, tile // 2 - 2)

        angle = CharacterRenderer.DIRECTIONS.get(
            getattr(direction, 'value', direction), math.pi
        )

        if death_progress is not None:
            progress = max(0.0, min(1.0, death_progress))
            radius = max(1, int(radius * (1.0 - progress) ** 0.72))
            mouth = min(math.pi * 0.96, 0.08 + progress * math.pi * 0.88)
        else:
            mouth = 0.08 + 0.42 * abs(math.sin(frame * 0.28))

        start = angle + mouth
        end = angle + 2 * math.pi - mouth
        points = [(cx, cy)]
        steps = 32
        for i in range(steps + 1):
            a = start + (end - start) * i / steps
            points.append((cx + math.cos(a) * radius, cy + math.sin(a) * radius))

        pygame.draw.polygon(surface, CharacterRenderer.PACMAN_COLOR, points)

    @staticmethod
    def draw_ghost(surface, pygame, pos, tile, name, direction='left',
                   frightened=False, eaten=False, frame=0, offset_y=0):
        cx = int(round(pos[0] * tile + tile // 2))
        cy = int(round(offset_y + pos[1] * tile + tile // 2))
        r = tile // 2 - 2

        color = (
            CharacterRenderer.FRIGHTENED_COLOR if frightened
            else CharacterRenderer.GHOST_COLORS.get(name, (235, 45, 55))
        )

        if not eaten:
            pygame.draw.circle(surface, color, (cx, cy - 2), r)
            pygame.draw.rect(surface, color, (cx - r, cy - 2, 2 * r, r))

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

        eye_y = cy - 2
        eye_dx = max(4, tile // 6)
        pupil_offset = {
            'Direita': (2, 0), 'right': (2, 0),
            'Esquerda':  (-2, 0), 'left': (-2, 0),
            'Cima':    (0, -2), 'up': (0, -2),
            'Baixo':  (0, 2), 'down': (0, 2),
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

        if frightened and not eaten and (frame // 8) % 2:
            pygame.draw.arc(
                surface, (255, 255, 255),
                (cx - 7, cy + 4, 14, 7), 0, math.pi, 2,
            )
