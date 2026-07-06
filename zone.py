from enum import Enum
from typing import Optional


class ZoneType(Enum):
    """Defines the supported types of zones in the graph.

    Each zone type affects how drones are allowed to travel
    through the network.
    """
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Zone:
    """Defines the supported types of zones in the graph.

    Each zone type affects how drones are allowed to travel
    through the network.
    """
    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        zone_type: ZoneType = ZoneType.NORMAL,
        color: Optional[str] = None,
        max_drones: int = 1,
    ) -> None:
        """Initializes a zone.

        Args:
            name: Unique name of the zone.
            x: X-coordinate of the zone.
            y: Y-coordinate of the zone.
            zone_type: Type of the zone.
            color: Optional display color.
            max_drones: Maximum number of drones allowed in the zone.
        """
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.color = color
        self.max_drones = max_drones
        self.current_drones: int = 0

    def get_cost(self) -> tuple[int, int]:
        """Returns the traversal cost and priority of the zone.

        The returned values are used by the pathfinding algorithm to
        determine the most suitable route.

        Returns:
            A tuple containing:
                - The movement cost.
                - The priority adjustment.
        """
        if (self.zone_type == ZoneType.NORMAL):
            return (1, 0)
        if (self.zone_type == ZoneType.RESTRICTED):
            return (2, 0)
        if (self.zone_type == ZoneType.PRIORITY):
            return (1, -1)
        else:
            return (1, 0)

    def is_blocked(self) -> bool:
        """Checks whether drones are allowed to enter the zone.

        Returns:
            True if the zone is blocked, otherwise False.
        """
        return self.zone_type == ZoneType.BLOCKED

    def is_full(self) -> bool:
        """Checks whether the zone has reached its drone capacity.

        Returns:
            True if the zone is full, otherwise False.
        """
        return self.current_drones == self.max_drones
