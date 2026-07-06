from graph import Graph
from zone import ZoneType
import webcolors
from pathfinding import Pathfinding


RESET = "\033[0m"


class Simulator:

    def __init__(
        self,
        graph: Graph,
        paths: list[list[str]],
        path_fin: Pathfinding,
        capacity_info: bool,
    ) -> None:
        self.graph = graph
        self.paths = paths
        self.path_fin = path_fin
        self.capacity_info = capacity_info

    def _expand_path(self) -> list[list[str]]:

        paths_c = []
        for path in self.paths:
            array = []
            last_zone = ""
            for zone_name in path:
                if zone_name == "WAIT":
                    array.append(zone_name)
                    continue
                zone = self.graph.get_zone(zone_name)
                if zone is None:
                    raise ValueError(f"Unknown zone: {zone_name}")
                if (zone.zone_type == ZoneType.RESTRICTED):
                    array.append(f"<{last_zone}-{zone_name}>")
                array.append(zone_name)
                last_zone = zone_name
            paths_c.append(array)

        return paths_c

    def get_expanded_paths(self) -> list[list[str]]:
        return self._expand_path()

    def color_text(self, text: str, color: str | None) -> str:

        if color is None:
            return text

        try:
            rgb = webcolors.name_to_rgb(color)
            return (
                f"\033[38;2;{rgb.red};{rgb.green};{rgb.blue}m"
                f"{text}"
                f"{RESET}"
            )
        except ValueError:
            return text

    def run(self) -> None:

        paths_c = self._expand_path()

        index = 1
        while True:
            line = ""
            for i, path in enumerate(paths_c):
                try:
                    if path[index] == "WAIT":
                        continue
                    if '-' in path[index]:
                        line += f"D{i + 1}-{path[index]} "
                    else:
                        zone = self.graph.get_zone(path[index])

                        if zone is None:
                            raise ValueError(f"Unknown zone: {path[index]}")

                        line += (
                            f"D{i + 1}-"
                            f"{self.color_text(zone.name, zone.color)} "
                        )
                except Exception:
                    pass
            if line == "":
                break
            print()
            print(f"Turn {index}: {line}")
            if self.capacity_info:
                for zone in self.graph.zones:
                    current = self.path_fin.max_drones_cache.get(
                        (zone.name, index),
                        0
                    )
                    print(
                        f"Zone {zone.name}: "
                        f"{current}/{zone.max_drones} drones"
                    )
                print()
                for connection in self.graph.connections:

                    current = self.path_fin.link_capacity_cache.get(
                        (
                            connection.zone_a.name,
                            connection.zone_b.name,
                            index,
                        ),
                        0,
                    )
                    print(
                        f"Connection {connection.zone_a.name}-{connection.zone_b.name}: "
                        f"{current}/{connection.max_link_capacity} used"
                    )
            index += 1
