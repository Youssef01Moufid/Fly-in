from simulator import Simulator
from graph import Graph
from parsing import Parser
from pathfinding import Pathfinding
# import pygame
# from visualizer import Visualizer


def main() -> None:
    try:
        file_path = "map.txt"

        graph = Graph(start_zone=None, end_zone=None)
        parser = Parser(file_path, graph)

        graph, nb_drones = parser.parsing()

        path_fin = Pathfinding(graph)

        paths = []
        for _ in range(nb_drones):
            paths.append(path_fin.get_path())

        # path_fin.propagate_goal_occupancy()

        simulator = Simulator(graph, paths, path_fin)
        simulator.run()

    except KeyboardInterrupt:
        print("Exit")
    # expanded_paths = simulator.get_expanded_paths()

    # visualizer = Visualizer(graph, expanded_paths)
    # visualizer.run()


if __name__ == "__main__":
    main()
