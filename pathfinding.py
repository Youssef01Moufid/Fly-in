from graph import Graph
import heapq
from zone import ZoneType, Zone
from typing import TypeAlias


class Pathfinding:
    """
    Finds drone paths through the graph while respecting zone and
    connection capacity constraints.

    This class uses a modified Dijkstra-based search to compute a path
    from the start hub to the end hub. After each path is found, it
    records the occupancy of zones and connections at each turn so that
    subsequent drones avoid exceeding their capacities.
    """
    def __init__(self, graph: Graph) -> None:
        """
        Initialize the pathfinding algorithm.

        Args:
            graph: Graph containing all zones and connections.
        """
        self.graph = graph
        self.max_drones_cache: dict[tuple[str, int], int] = {}
        self.link_capacity_cache: dict[tuple[str, str, int], int] = {}

    def _register_path(self, path: list[str]) -> None:
        """
        Register a computed path in the capacity caches.

        Updates the zone and connection occupancy caches for every turn of
        the path. These caches are later used to prevent future drones from
        exceeding zone or connection capacities.

        Args:
            path: The path assigned to a drone.
        """
        cost = -1
        old_hub = ""
        for zone_name in path:
            hub = zone_name
            if zone_name == "WAIT":
                hub = old_hub
            else:
                old_hub = zone_name
                zone = self.graph.get_zone(hub)
                if zone is None:
                    raise ValueError(f"Unknown zone: {hub}")
                if (zone.zone_type == ZoneType.RESTRICTED):
                    cost += 1
            cost += 1
            max_d = self.max_drones_cache.get((hub, cost), 0)
            self.max_drones_cache[(hub, cost)] = max_d + 1

        cost = 0
        last_zone = ""
        for zone_name in path:
            if zone_name == "WAIT":
                cost += 1
                continue

            if last_zone != "":
                cost += 1
                link = (last_zone, zone_name, cost)
                max_l_c = self.link_capacity_cache.get(link, 0)
                self.link_capacity_cache[link] = max_l_c + 1
                zone_t = self.graph.get_zone(zone_name)

                if zone_t is None:
                    raise ValueError(f"Unknown zone: {zone_name}")

                if (zone_t.zone_type == ZoneType.RESTRICTED):
                    cost += 1
                    link = (last_zone, zone_name, cost)
                    max_l_c = self.link_capacity_cache.get(link, 0)
                    self.link_capacity_cache[link] = max_l_c + 1

            last_zone = zone_name

    def can_move(
        self,
        current: Zone,
        neighbor: Zone,
        current_turn: int,
    ) -> bool:

        duration, _ = neighbor.get_cost()

        connection = self.graph.get_connection(current, neighbor)

        if connection is None:
            return False

        for t in range(1, duration + 1):

            used = self.link_capacity_cache.get(
                (current.name, neighbor.name, current_turn + t),
                0
            )

            if used >= connection.max_link_capacity:
                return False

        arrival = current_turn + duration

        used = self.max_drones_cache.get(
            (neighbor.name, arrival),
            0
        )

        if used >= neighbor.max_drones:
            return False

        return True

    # def propagate_goal_occupancy(self) -> None:

    #     goal = self.graph.end_zone
    #     if goal is None:
    #         return

    #     last_turn = max(
    #         turn for (_, turn) in self.max_drones_cache.keys()
    #     )

    #     current = 0
    #     for turn in range(last_turn + 1):
    #         current += self.max_drones_cache.get((goal.name, turn), 0)
    #         self.max_drones_cache[(goal.name, turn)] = current

    def get_path(self) -> list[str]:
        """
        Compute the best available path for a drone.

        Uses a priority queue to search for the lowest-cost path while
        respecting zone capacities, connection capacities, and zone
        traversal costs. If a move is temporarily impossible due to
        capacity limits, a WAIT action is inserted into the path.

        Returns:
            A list of zone names (and optional "WAIT" steps) representing
            the selected path. Returns an empty list if no valid path exists.
        """
        heapItem: TypeAlias = tuple[int, int, str, list[str]]
        heap: list[heapItem] = []
        start_zone = self.graph.start_zone
        if start_zone is None:
            raise ValueError(f"Unkown start zone: {start_zone}")
        heapq.heappush(heap, (0, 0, start_zone.name, [start_zone.name]))
        visited = []
        # res_drone = 0
        # res_link = 0

        while heap:
            cost, p, name, path = heapq.heappop(heap)

            end_zone = self.graph.end_zone
            if end_zone is None:
                raise ValueError(f"Unkown end_zone: {end_zone}")
            if name == end_zone.name:
                self._register_path(path)
                return path

            zone = self.graph.get_zone(name)
            if zone is None:
                raise ValueError(f"Unkown zone: {zone}")
            neighbors = self.graph.get_neighbors(zone)

            v = (name, cost)
            if v in visited:
                continue
            visited.append(v)

            for neighbor in neighbors:

                if neighbor.name in path:
                    continue

                n_cost, n_p = neighbor.get_cost()
                c = cost + n_cost
                p1 = p + n_p

                # zone_reserve = self.max_drones_cache.get(
                #     (neighbor.name, c), res_drone
                # )

                # link_reserve = self.link_capacity_cache.get(
                #     (name, neighbor.name, c), res_link
                # )

                connection = self.graph.get_connection(zone, neighbor)
                if connection is None:
                    raise ValueError(f"Unkown connection: {connection}")

                if not self.can_move(zone, neighbor, cost):

                    heapq.heappush(heap, (cost + 1, p, name, path + ['WAIT']))
                    continue

                heapq.heappush(
                    heap, (c, p1, neighbor.name, path + [neighbor.name])
                    )
        return []
