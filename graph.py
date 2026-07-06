from zone import Zone
from connection import Connection


class Graph:
    """Represents the drone network as an undirected graph.

    The graph stores all zones and connections, along with the
    designated start and end zones. It provides helper methods
    for adding elements and querying the graph structure.
    """
    def __init__(
        self,
        start_zone: Zone | None,
        end_zone: Zone | None,
        zones: list[Zone] | None = None,
        connections: list[Connection] | None = None,
    ) -> None:
        """Initializes a graph.

        Args:
            start_zone: The starting zone of the graph.
            end_zone: The destination zone of the graph.
            zones: Optional list of zones.
            connections: Optional list of connections.
        """
        self.start_zone = start_zone
        self.end_zone = end_zone
        self.zones = zones if zones is not None else []
        self.connections = connections if connections is not None else []

    def add_zone(self, zone: Zone) -> None:
        """Adds a zone to the graph if it is not already present.

        Args:
            zone: The zone to add.
        """
        if zone not in self.zones:
            self.zones.append(zone)

    def get_zone(self, name: str) -> Zone | None:
        """Finds a zone by its name.

        Args:
            name: Name of the zone to search for.

        Returns:
            The matching zone if found, otherwise None.
        """
        for zone in self.zones:
            if zone.name == name:
                return zone
        return None

    def get_neighbors(self, zone: Zone) -> list[Zone]:
        """Returns the accessible neighboring zones.

        Blocked zones are excluded from the returned list.

        Args:
            zone: The zone whose neighbors are requested.

        Returns:
            A list of neighboring zones that can be entered.
        """
        neighbors_zone: list[Zone] = []
        for con in self.connections:
            if con.involves(zone):
                neighbor = con.other_end(zone)
                if not neighbor.is_blocked():
                    neighbors_zone.append(neighbor)
        return neighbors_zone

    def get_connection(self, zone_a: Zone, zone_b: Zone) -> Connection | None:
        """Returns the connection between two zones.

        Args:
            zone_a: First zone.
            zone_b: Second zone.

        Returns:
            The connection linking the two zones if it exists,
            otherwise None.
        """
        for con in self.connections:WAIT
            if con.involves(zone_a) and con.involves(zone_b):
                return con
        return None

    def has_connection(self, zone_a: Zone, zone_b: Zone) -> bool:
        """Checks whether two zones are directly connected.

        Args:
            zone_a: First zone.
            zone_b: Second zone.

        Returns:
            True if a connection exists, otherwise False.
        """
        for con in self.connections:
            if con.involves(zone_a) and con.involves(zone_b):
                return True
        return False

    def add_connection(self, connection: Connection) -> None:
        """Adds a connection to the graph if it does not already exist.

        Args:
            connection: The connection to add.
        """
        if not self.has_connection(connection.zone_a, connection.zone_b):
            self.connections.append(connection)
