*This project has been created as part of the 42 curriculum by ymoufid.*

# Fly-In

## Description

Fly-In is a drone routing simulator that computes collision-free paths through a network of interconnected hubs.

The program parses a map description, validates its contents, constructs a graph representation of the network, and computes a valid path for every drone while respecting all movement constraints defined by the map.

The simulator schedules drones turn by turn, ensuring that zone capacities, connection capacities, traversal times, and special zone behaviors are respected throughout the simulation.

---

# Features

* Custom map parser
* Extensive input validation
* Graph-based network representation
* Multi-drone routing
* Capacity-aware pathfinding
* Turn-by-turn simulation
* Support for:

  * Normal zones
  * Blocked zones
  * Restricted zones
  * Priority zones
* Zone capacities
* Connection capacities
* Waiting when movement is temporarily impossible

---

# Instructions

## Requirements

* Python 3.13 or newer

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python3 fly-in.py map.txt
```

or

```bash
make run
```

---

# Map Format

A map contains:

* one `nb_drones`
* one `start_hub`
* one `end_hub`
* zero or more intermediate hubs
* connections between hubs

Example:

```text
nb_drones: 2

start_hub: start 0 0 [color=green]

hub: A 1 0

hub: B 2 0

end_hub: goal 3 0 [color=red]

connection: start-A
connection: A-B
connection: B-goal
```

---

# Zone Metadata

Zones support optional metadata.

| Property     | Description                                     |
| ------------ | ----------------------------------------------- |
| `zone`       | normal, blocked, restricted or priority         |
| `color`      | Display color                                   |
| `max_drones` | Maximum number of drones allowed simultaneously |

Example:

```text
hub: checkpoint 4 2 [zone=restricted color=blue max_drones=2]
```

---

# Connection Metadata

Connections may specify their maximum capacity.

Example:

```text
connection: A-B [max_link_capacity=2]
```

If omitted, the default value is **1**.

---

# Algorithm

The routing algorithm is based on **Dijkstra's shortest path algorithm**, extended to satisfy the constraints of the Fly-In project.

Instead of considering only the shortest distance, every movement also checks:

* zone capacity
* connection capacity
* traversal duration
* restricted-zone traversal
* priority zones
* waiting when necessary

Each time a path is assigned to a drone, two reservation caches are updated:

* **Zone reservation cache**

  Stores how many drones occupy each zone at every turn.

* **Connection reservation cache**

  Stores how many drones occupy each connection at every turn.

When computing the path for the next drone, these caches are consulted before every movement. If either the destination zone or the connection has reached its capacity, the algorithm inserts a **WAIT** action instead of moving immediately.

Restricted zones require two turns to traverse. During this traversal, the drone occupies the connection until it reaches the destination zone.

Priority zones are assigned a lower routing priority cost, encouraging the algorithm to select them whenever possible.

---

# Parsing Strategy

Before simulation starts, the parser performs extensive validation.

Among the checks performed are:

* valid file syntax
* missing required fields
* duplicate zone names
* duplicate coordinates
* invalid metadata
* duplicate metadata keys
* invalid colors
* invalid zone types
* invalid capacities
* duplicate connections
* self-connections
* invalid metadata formatting
* unexpected text after metadata
* invalid start or end hubs
* existence of at least one valid path

If any validation fails, the program terminates immediately with a descriptive error message.

---

# Resources

## Documentation

* heapq — https://docs.python.org/3/library/heapq.html
* typing — https://docs.python.org/3/library/typing.html
* Dijkstra's Algorithm — https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
* Graph Theory — https://en.wikipedia.org/wiki/Graph_theory

## AI Usage

Artificial intelligence was used as a development assistant throughout this project.

It was used for:

* discussing algorithm design
* reviewing implementation ideas
* explaining Python language features
* suggesting improvements to code organization
* generating and improving documentation
* writing docstrings
* identifying edge cases for parser validation
* reviewing error handling strategies

All architectural decisions, implementation, debugging, testing, and final code were completed and verified manually.

---

# Author

**ymoufid**

42 Network
