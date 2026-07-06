import pygame
from graph import Graph
from zone import ZoneType

WIDTH = 1400
HEIGHT = 900

FPS = 60

BACKGROUND = (245, 245, 245)
BLACK = (25, 25, 25)
GRAY = (170, 170, 170)

BLUE = (70, 130, 255)
GREEN = (40, 180, 40)
RED = (220, 70, 70)
YELLOW = (255, 220, 0)
PURPLE = (170, 70, 255)


class Visualizer:

    def __init__(
        self,
        graph: Graph,
        paths: list[list[str]]
    ) -> None:

        pygame.init()

        self.graph = graph
        self.paths = paths

        self.screen = pygame.display.set_mode(
            (WIDTH, HEIGHT)
        )

        pygame.display.set_caption("Fly-In")

        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont(
            "Arial",
            18
        )

        self.big_font = pygame.font.SysFont(
            "Arial",
            24,
            bold=True
        )

        self.turn = 0
        self.running = True

        self.turn_duration = 900
        self.last_turn = pygame.time.get_ticks()

        self.zoom = 1.0

        self.pan_x = 0
        self.pan_y = 0

        self.dragging = False

        self.compute_camera()
        self.paused = True
        self.turn = 0

    def compute_camera(self) -> None:

        xs = [z.x for z in self.graph.zones]
        ys = [z.y for z in self.graph.zones]

        self.min_x = min(xs)
        self.max_x = max(xs)

        self.min_y = min(ys)
        self.max_y = max(ys)

        world_w = max(1, self.max_x - self.min_x)
        world_h = max(1, self.max_y - self.min_y)

        margin = 120

        self.scale = min(
            (WIDTH - margin * 2) / world_w,
            (HEIGHT - margin * 2) / world_h,
        )

        self.offset_x = (
            WIDTH - world_w * self.scale
        ) / 2

        self.offset_y = (
            HEIGHT - world_h * self.scale
        ) / 2

    def world_to_screen(
        self,
        x: float,
        y: float
    ) -> tuple[int, int]:

        sx = (
            (x - self.min_x)
            * self.scale
            * self.zoom
            + self.offset_x
            + self.pan_x
        )

        sy = (
            (y - self.min_y)
            * self.scale
            * self.zoom
            + self.offset_y
            + self.pan_y
        )

        return int(sx), int(sy)

    def draw_connections(self) -> None:

        for connection in self.graph.connections:

            x1, y1 = self.world_to_screen(
                connection.zone_a.x,
                connection.zone_a.y
            )

            x2, y2 = self.world_to_screen(
                connection.zone_b.x,
                connection.zone_b.y
            )

            pygame.draw.line(
                self.screen,
                GRAY,
                (x1, y1),
                (x2, y2),
                3
            )
    
    def draw_zones(self) -> None:

        radius = max(
            12,
            min(
                24,
                int(20 * self.zoom)
            )
        )

        for zone in self.graph.zones:

            x, y = self.world_to_screen(
                zone.x,
                zone.y
            )

            color = BLUE

            if zone == self.graph.start_zone:
                color = GREEN

            elif zone == self.graph.end_zone:
                color = YELLOW

            elif zone.zone_type == ZoneType.RESTRICTED:
                color = RED

            pygame.draw.circle(
                self.screen,
                color,
                (x, y),
                radius
            )

            pygame.draw.circle(
                self.screen,
                BLACK,
                (x, y),
                radius,
                2
            )

            txt = self.font.render(
                zone.name,
                True,
                BLACK
            )

            rect = txt.get_rect(
                center=(x, y - radius - 18)
            )

            pygame.draw.rect(
                self.screen,
                BACKGROUND,
                rect.inflate(6, 4)
            )

            self.screen.blit(
                txt,
                rect
            )
    
    def draw_hud(self) -> None:

        txt = self.big_font.render(
            f"Turn : {self.turn}",
            True,
            BLACK
        )

        self.screen.blit(txt, (20, 20))

        txt = self.font.render(
            "← Previous   → Next   SPACE Play/Pause   R Reset   ESC Quit",
            True,
            BLACK
        )

        self.screen.blit(txt, (20, 55))
    
    def draw(self) -> None:

        self.screen.fill(
            BACKGROUND
        )

        self.draw_connections()

        self.draw_zones()

        self.draw_drones()

        self.draw_hud()

        pygame.display.flip()
    
    def draw_drones(self) -> None:

        offsets = [
            (0, 0),
            (-12, -12),
            (12, -12),
            (-12, 12),
            (12, 12),
            (-18, 0),
            (18, 0),
            (0, -18),
            (0, 18),
        ]

        occupied = {}

        for i, path in enumerate(self.paths):

            if self.turn >= len(path):
                index = len(path) - 1
            else:
                index = self.turn

            zone_name = path[index]

            # Stay in the previous hub while waiting
            while zone_name == "WAIT" and index > 0:
                index -= 1
                zone_name = path[index]

            zone = self.graph.get_zone(zone_name)

            if zone is None:
                continue

            x, y = self.world_to_screen(
                zone.x,
                zone.y
            )

            count = occupied.get(zone.name, 0)
            occupied[zone.name] = count + 1

            dx, dy = offsets[count % len(offsets)]

            x += dx
            y += dy

            pygame.draw.circle(
                self.screen,
                PURPLE,
                (x, y),
                7
            )

            txt = self.font.render(
                str(i + 1),
                True,
                BLACK
            )

            self.screen.blit(
                txt,
                (x + 8, y - 8)
            )

    def update(self) -> None:

        now = pygame.time.get_ticks()

        if now - self.last_turn >= self.turn_duration:

            self.turn += 1

            self.last_turn = now

            max_turn = max(
                len(path)
                for path in self.paths
            )

            if self.turn >= max_turn:
                self.turn = 0

    def run(self) -> None:

        # paused = False

        while self.running:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_RIGHT:
                        self.turn += 1

                        max_turn = max(len(path) for path in self.paths)
                        if self.turn >= max_turn:
                            self.turn = max_turn - 1

                    elif event.key == pygame.K_LEFT:
                        self.turn -= 1
                        if self.turn < 0:
                            self.turn = 0

                    elif event.key == pygame.K_SPACE:
                        self.paused = not self.paused

                    elif event.key == pygame.K_r:
                        self.turn = 0

                    elif event.key == pygame.K_ESCAPE:
                        self.running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:

                    if event.button == 1:
                        self.dragging = True
                        self.last_mouse = event.pos

                    elif event.button == 4:
                        self.zoom *= 1.1

                    elif event.button == 5:
                        self.zoom /= 1.1

                elif event.type == pygame.MOUSEBUTTONUP:

                    if event.button == 1:
                        self.dragging = False

                elif event.type == pygame.MOUSEMOTION:

                    if self.dragging:

                        dx = event.pos[0] - self.last_mouse[0]
                        dy = event.pos[1] - self.last_mouse[1]

                        self.pan_x += dx
                        self.pan_y += dy

                        self.last_mouse = event.pos

            if not self.paused:
                self.update()

            self.draw()

            self.clock.tick(FPS)

        pygame.quit()
