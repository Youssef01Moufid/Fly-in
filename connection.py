from zone import Zone


class Connection:

    """Represents a bidirectional connection between two zones.

    A connection links two zones and defines the maximum number of
    drones that can simultaneously travel through it.
    """
    def __init__(
        self,
        zone_a: Zone,
        zone_b: Zone,
        max_link_capacity: int
    ) -> None:
        self.zone_a = zone_a
        self.zone_b = zone_b
        self.max_link_capacity = max_link_capacity
        self.current_drones: int = 0
        """Initializes a connection between two zones.

        Args:
            zone_a: First endpoint of the connection.
            zone_b: Second endpoint of the connection.
            max_link_capacity: Maximum number of drones that can
                use the connection simultaneously.
        """

    def is_full(self) -> bool:
        """Checks whether the connection has reached its capacity.

        Returns:
            True if the connection is full, otherwise False.
        """
        return self.current_drones >= self.max_link_capacity

    def involves(self, zone: Zone) -> bool:
        """Checks whether the connection is attached to a given zone.

        Args:
            zone: Zone to test.

        Returns:
            True if the zone is one of the connection's endpoints,
            otherwise False.
        """
        return self.zone_a == zone or self.zone_b == zone

    def other_end(self, zone: Zone) -> Zone:
        """Returns the opposite endpoint of the connection.

        Args:
            zone: One endpoint of the connection.

        Returns:
            The zone at the opposite end of the connection.
        """
        if zone == self.zone_a:
            return self.zone_b
        return self.zone_a
