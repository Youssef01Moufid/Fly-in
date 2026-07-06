from simulator import Simulator
from graph import Graph
from parsing import Parser
from pathfinding import Pathfinding
import sys
from visualizer import Visualizer


def main() -> None:
    try:
        # file_path = "map.txt"

        capacity_info = False

        if len(sys.argv) == 2:
            file_path = sys.argv[1]

        elif len(sys.argv) == 3 and sys.argv[1] == "--capacity-info":
            capacity_info = True
            file_path = sys.argv[2]

        else:
            print("Usage:")
            print("  python3 fly-in.py map.txt")
            print("  python3 fly-in.py --capacity-info map.txt")
            raise SystemExit(1)

        graph = Graph(start_zone=None, end_zone=None)
        parser = Parser(file_path, graph)

        graph, nb_drones = parser.parsing()

        path_fin = Pathfinding(graph)

        paths = []
        for _ in range(nb_drones):
            paths.append(path_fin.get_path())

        simulator = Simulator(graph, paths, path_fin, capacity_info)
        simulator.run()
    except KeyboardInterrupt:
        print("Exit")
    expanded_paths = simulator.get_expanded_paths()

    visualizer = Visualizer(graph, expanded_paths)
    visualizer.run()


if __name__ == "__main__":
    main()
