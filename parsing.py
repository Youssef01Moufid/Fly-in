from zone import Zone, ZoneType
from connection import Connection
from graph import Graph
from typing import Optional
from pathfinding import Pathfinding
import webcolors


class Parser:
    """Parses a map file and builds the graph representation.

    The parser validates the input format, creates zones and
    connections, and initializes the simulation graph.
    """

    def __init__(self, file_path: str, graph: Graph) -> None:
        """Initializes the parser.
        Args:
            file_path: Path to the map file.
            graph: Graph instance to populate.
        """
        self.graph = graph
        self.file_path = file_path

    def parse_nb_drones(self, line: str, line_number: int) -> int:
        """Parses the number of drones from the input file.

        Validates that the value is a positive integer.

        Args:
            line: Raw line containing the ``nb_drones`` definition.
            line_number: Line number in the input file.

        Returns:
            The number of drones specified in the file.

        Raises:
            SystemExit: If the value is missing, not an integer,
                or less than or equal to zero.
        """

        parts = line.strip().split(":")

        try:
            value = int(parts[1].strip().strip().split("#")[0].strip())
        except ValueError:
            raise SystemExit(
                f"Error line {line_number} "
                f"nb_drones must be a valid integer"
            )

        if value <= 0:
            raise SystemExit(
                f"Error line {line_number}: "
                f"nb_drones must be a positive integer"
            )

        return value

    def _check_metadata_format(self, line: str, line_number: int) -> None:

        """Validates the syntax of a metadata block.

        Ensures that metadata is enclosed in a single pair of square
        brackets, that the brackets are properly ordered, and that
        no extra text appears after the closing bracket.

        Args:
            line: Raw input line containing optional metadata.
            line_number: Line number in the input file.

        Raises:
            SystemExit: If the metadata format is invalid.
        """

        if line.count("[") != line.count("]"):
            raise SystemExit(
                f"Error line {line_number}: "
                "Unmatched '[' or ']'"
            )

        if line.count("[") > 1 or line.count("]") > 1:
            raise SystemExit(
                f"Error line {line_number}: "
                "Only one metadata block is allowed"
            )

        if "[" in line:

            open_bracket = line.index("[")
            close_bracket = line.index("]")

            if open_bracket > 0 and not line[open_bracket - 1].isspace():
                raise SystemExit(
                    f"Error line {line_number}: "
                    "Expected a space before '['"
                )

            if close_bracket < open_bracket:
                raise SystemExit(
                    f"Error line {line_number}: "
                    "Invalid metadata format"
                )

            if line[close_bracket + 1:].strip():
                raise SystemExit(
                    f"Error line {line_number}: "
                    "Unexpected text after metadata"
                )

    def parse_zone(
        self,
        line: str,
        line_number: int,
        default_max_drones: int
    ) -> Zone:
        """Parses a zone definition from the map file.

        The function validates the zone syntax, coordinates, zone type,

        color, and maximum drone capacity before creating a Zone

        instance.

        Supported metadata options:

        zone: Zone type (normal, blocked, restricted, priority).

        color: CSS color name.

        max_drones: Maximum number of drones allowed.

        Args:

        line: Raw zone definition line.

        line_number: Line number in the input file.

        default_max_drones: Default capacity assigned when

        max_drones is not specified.

        Returns:

        A validated Zone object.

        Raises:

        SystemExit: If the zone definition is invalid.

        """

        self._check_metadata_format(line, line_number)

        main_part = line.split("[")
        parts = main_part[0].strip().split()
        zone_seen = False
        color_seen = False
        max_drones_seen = False

        if len(parts) != 4:
            raise SystemExit(
                f"Error line {line_number}"
                f"Invalid number of arrgument"
            )

        name = parts[1]

        if "-" in name or " " in name:
            raise SystemExit(
                f"Error line {line_number}: "
                f"The name should not contain dash or space "
                )

        try:
            x = int(parts[2])
            y = int(parts[3])
        except (ValueError):
            raise SystemExit(
                    f"Error line {line_number}: "
                    f"coordinates must be valid integers"
                )

        zone_type: ZoneType = ZoneType.NORMAL
        color: Optional[str] = None
        max_drones: int = default_max_drones

        if len(main_part) > 1:

            opt_part = main_part[1].strip().strip("]").split(" ")

            if len(opt_part) > 3:
                raise SystemExit(
                    f"Error line {line_number}"
                    f"Invalid number of arrgument"
                )

            for opt in opt_part:

                obj = opt.split("=")

                if obj[0] == "zone":

                    if zone_seen:
                        raise SystemExit(
                            f"Error line {line_number}:"
                            f"'zone' specified more than once"
                        )
                    zone_seen = True

                    valid_types = [zt.value for zt in ZoneType]

                    if obj[1] not in valid_types:
                        raise SystemExit(
                            f"Error line {line_number}: "
                            f"Invalid zone type '{obj[1]}'"
                        )

                    zone_type = ZoneType(obj[1])

                elif obj[0] == "color":
                    try:
                        webcolors.name_to_rgb(obj[1])
                    except ValueError:
                        raise SystemExit(
                            f"Error line {line_number}: "
                            f"Unknown color '{obj[1]}'"
                        )
                    if color_seen:
                        raise SystemExit(
                            f"Error line {line_number}"
                            f"'color' specified more than once"
                        )
                    color_seen = True
                    color = obj[1]

                elif obj[0] == "max_drones":

                    if max_drones_seen:
                        raise SystemExit(
                            f"Error line {line_number}"
                            f"'max_drones' specified more than once"
                        )
                    max_drones_seen = True
                    try:
                        max_drones = int(obj[1])
                    except ValueError:
                        raise SystemExit(
                            f"Error line {line_number}: "
                            f"max drone must be integer"
                        )

                else:
                    raise SystemExit(
                        f"Error line {line_number}"
                        f"Invalid input"
                    )

        return Zone(name, x, y, zone_type, color, max_drones)

    def parse_connection(self, line: str, line_number: int) -> Connection:
        """Parses a connection definition from the map file.

        Validates the connection syntax, ensures both referenced zones
        exist, checks for duplicate or self-connections, and parses the
        optional maximum link capacity.

        Args:
            line: Raw connection definition line.
            line_number: Line number in the input file.

        Returns:
            A validated Connection object.

        Raises:
            SystemExit: If the connection definition is invalid.
        """
        self._check_metadata_format(line, line_number)

        main_part = line.split("[")
        parts = main_part[0].strip().split(":")

        if len(parts) != 2:
            raise SystemExit(
                f"Error line {line_number}: "
                f"Invalid connection format"
            )

        if "-" not in parts[1]:
            raise SystemExit(
                f"Error line {line_number}: "
                f"Invalid connection format"
            )

        zones = parts[1].strip().split("-")
        zone_a = self.graph.get_zone(zones[0].strip())

        if zone_a is None:
            raise SystemExit(
                f"Error line {line_number}: "
                f"Zone '{zones[0].strip()}' not found"
            )

        zone_b = self.graph.get_zone(zones[1].strip())

        if zone_b is None:
            raise SystemExit(
                f"Error line {line_number}: "
                f"Zone '{zones[1].strip()}' not found"
            )

        if self.graph.has_connection(zone_a, zone_b):
            raise SystemExit(
                f"Error line {line_number}: "
                f"Duplicate connection between "
                f"'{zone_a.name}' and '{zone_b.name}'"
            )

        if zone_a == zone_b:
            raise SystemExit(
                f"Error line {line_number} "
                f"Connection must be between two different zones"
            )

        max_link_capacity: int = 1

        if len(main_part) > 1:

            metadata = main_part[1].strip().strip("]")

            if metadata == "":
                raise SystemExit(
                    f"Error line {line_number}: "
                    "Empty metadata is not allowed"
                )

            cap = metadata.split("=")

            if len(cap) != 2 or cap[0] != "max_link_capacity":
                raise SystemExit(
                    f"Error line {line_number}: "
                    "Invalid connection metadata"
                )

            try:
                max_link_capacity = int(cap[1])

                if max_link_capacity <= 0:
                    raise SystemExit(
                        f"Error line {line_number}: "
                        "max_link_capacity must be a positive integer"
                    )

            except ValueError:
                raise SystemExit(
                    f"Error line {line_number}: "
                    "max_link_capacity must be a valid integer"
                )

        return Connection(zone_a, zone_b, max_link_capacity)

    def _check_unique_name(self, name: str, line_number: int) -> None:
        """Ensures that a zone name is unique.

        Args:
            name: Name of the zone to validate.
            line_number: Line number in the input file.

        Raises:
            SystemExit: If another zone already uses the same name.
        """
        if self.graph.get_zone(name) is not None:
            raise SystemExit(
                f"Error line {line_number}: "
                f"Zone name '{name}' already exists"
            )

    def _check_unique_coordinates(
        self,
        x: int,
        y: int,
        line_number: int
    ) -> None:
        """Ensures that zone coordinates are unique.

        Prevents multiple zones from being created at the same
        coordinates.

        Args:
            x: X-coordinate of the zone.
            y: Y-coordinate of the zone.
            line_number: Line number in the input file.

        Raises:
            SystemExit: If another zone already exists at the specified
                coordinates.
        """

        for zone in self.graph.zones:
            if zone.x == x and zone.y == y:
                raise SystemExit(
                    f"Error line {line_number}: "
                    f"Coordinates ({x}, {y}) are already "
                    f"used by zone '{zone.name}'"
                )

    def parsing(self) -> tuple[Graph, int]:
        """Parses and validates the entire map file.

        Reads the input file line by line, validates its contents,
        constructs the graph by creating zones and connections, and
        performs final consistency checks on the resulting map.

        The function ensures that:
            - ``nb_drones`` is defined exactly once and is the first entry.
            - Exactly one start hub and one end hub are defined.
            - Zone names and coordinates are unique.
            - Start and end hubs satisfy their constraints.
            - A valid path exists between the start and end hubs.

        Returns:
            A tuple containing:
                - The populated graph.
                - The number of drones.

        Raises:
            SystemExit: If the input file is invalid or no valid path
                exists between the start and end hubs.
        """

        nb_drones_found: bool = False
        start_zone: Zone | None = None
        end_zone: Zone | None = None
        line_count: int = 0

        with open(self.file_path, "r") as file:

            for line_number, line in enumerate(file, start=1):

                line = line.strip()
                if not line:
                    continue

                if line.startswith("#"):
                    continue

                line = line.split("#")[0].strip()
                if not line:
                    continue
                line_count += 1
                keyword = line.split(":")[0].strip()

                if keyword == "nb_drones":
                    if line_count != 1:
                        raise SystemExit(
                            f"Error line {line_number}"
                            f"nb_drones must be the first line"
                        )
                    if nb_drones_found:
                        raise SystemExit(
                            f"Error line {line_number}"
                            f"Error nb_drones already defined"
                        )
                    nb_drones_found = True
                    value: int = self.parse_nb_drones(
                        line,
                        line_number,
                    )

                elif keyword == "start_hub":

                    if start_zone is not None:
                        raise SystemExit(
                            f"Error line {line_number}: "
                            f"start_hub already defined"
                        )
                    zone: Zone = self.parse_zone(
                        line,
                        line_number,
                        value,
                    )
                    self._check_unique_name(zone.name, line_number)
                    self._check_unique_coordinates(zone.x, zone.y, line_number)
                    start_zone = zone
                    self.graph.add_zone(start_zone)

                elif keyword == "end_hub":

                    if end_zone is not None:
                        raise SystemExit(
                            f"Error line {line_number}: "
                            f"end_hub already defined"
                        )
                    zone = self.parse_zone(line, line_number, value)
                    self._check_unique_name(zone.name, line_number)
                    self._check_unique_coordinates(zone.x, zone.y, line_number)
                    end_zone = zone
                    self.graph.add_zone(end_zone)

                elif keyword == "hub":

                    zone = self.parse_zone(line, line_number, 1)
                    self._check_unique_name(zone.name, line_number)
                    self._check_unique_coordinates(zone.x, zone.y, line_number)
                    self.graph.add_zone(zone)

                elif keyword == "connection":

                    connection: Connection = self.parse_connection(
                        line,
                        line_number,
                    )
                    self.graph.add_connection(connection)

                else:
                    raise SystemExit(
                        f"Error line {line_number}: "
                        f"Invalid input"
                    )

            if not nb_drones_found:
                raise SystemExit("Error: nb_drones is missing from the file")

            if start_zone is None:
                raise SystemExit(
                    "Error: start_hub is missing from the file"
                )

            if end_zone is None:
                raise SystemExit(
                    "Error: end_zone is missing from the file"
                )

            if start_zone.zone_type == ZoneType.RESTRICTED:
                raise SystemExit(
                    "Error: start_hub cannot be restricted"
                )

            if start_zone.zone_type == ZoneType.BLOCKED:
                raise SystemExit(
                    "Error: start_hub cannot be blocked"
                )

            if end_zone.zone_type == ZoneType.BLOCKED:
                raise SystemExit(
                    "Error: end_hub cannot be blocked"
                )

            if start_zone.max_drones < value:
                raise SystemExit(
                    "Error: start_hub max_drones must be "
                    "greater than or equal to nb_drones"
                )

            if end_zone.max_drones < value:
                raise SystemExit(
                    "Error: end_hub max_drones must be "
                    "greater than or equal to nb_drones"
                )

        self.graph.start_zone = start_zone
        self.graph.end_zone = end_zone

        # self.graph.end_zone.max_drones = value
        # self.graph.start_zone.max_drones = value

        pathfinder = Pathfinding(self.graph)

        if pathfinder.get_path() == []:
            raise SystemExit(
                "Error: no valid path exists between start_hub and end_hub"
            )

        return self.graph, value
