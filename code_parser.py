from collections import defaultdict
import numpy as np
from graph import Graph


def arc_id(arc: int):
    return "A" + str(arc)


def region_id(region: int):
    return "R" + str(region)


def vertex_id(vertex: int):
    return "V" + str(vertex)


def corner_id(first: int, second: int):
    return (min(first, second), max(first, second))


def get_meta_graph(pd_code):
    end_buffer = pd_code

    graph = Graph()

    input_offset = 0
    vertex_counter = 0

    while end_buffer != "":
        arcs_string = end_buffer[2 : end_buffer.index("]")]
        arcs = np.fromstring(arcs_string, dtype=int, sep=",").tolist()

        for arc in arcs:
            if not arc in graph.nodes:
                graph.add_node(arc_id(arc), {"arcId": arc, "type": "arc"})

        data = {
            "arcs": arcs,
            "corners": defaultdict(lambda: None),
        }

        if end_buffer[0] == "V":
            data["type"] = "vertex"
        else:
            data["type"] = "crossing"

        graph.add_node("V" + str(vertex_counter), data)
        vertex_counter += 1

        input_offset = end_buffer.index("]") + 2
        end_buffer = end_buffer[input_offset:]

    vertex_to_remove = []
    arc_to_remove = []
    arc_map = []

    # Convert 2-degree vertices (2 arcs) to one arc
    for vertex_key, vertex in graph.get_vertices().items():
        if len(vertex["arcs"]) == 2:
            first = vertex["arcs"][0]
            second = vertex["arcs"][1]

            vertex_to_remove.append(vertex_key)
            arc_to_remove.append(arc_id(first))
            arc_map.append((first, second))

    for vertex in vertex_to_remove:
        graph.remove_node(vertex)

    for arc in arc_to_remove:
        graph.remove_node(arc)

    for map in arc_map:
        for vertex_key, vertex in graph.get_vertices().items():
            try:
                old_index = vertex["arcs"].index(map[0])

                if old_index >= 0:
                    vertex["arcs"][old_index] = map[1]
            except:
                pass

    # Populate corners and regions
    region_index = 0
    for vertex_key, vertex in graph.get_vertices().items():
        arcs = vertex["arcs"]

        for i in range(len(arcs)):
            origin = arcs[i]
            finish = arcs[(i + 1) % len(arcs)]

            # Region is already assigned to this corner
            if vertex["corners"][corner_id(origin, finish)] is not None:
                continue

            region_index += 1

            vertex["corners"][corner_id(origin, finish)] = region_id(region_index)

            graph.add_node(region_id(region_index))

            graph.add_edge(region_id(region_index), vertex_key)
            graph.add_edge(region_id(region_index), arc_id(origin))

            # Triangulate region by turning counter clockwise on every corner
            direction = origin
            neighbour_vertex = vertex
            while direction != finish:
                neighbour_vertex_id, neighbour_vertex = next(
                    (key, value)
                    for key, value in graph.get_vertices().items()
                    if value["id"] != neighbour_vertex["id"]
                    and direction in value["arcs"]
                )
                source = direction
                direction = neighbour_vertex["arcs"][
                    neighbour_vertex["arcs"].index(direction) - 1
                ]
                neighbour_vertex["corners"][corner_id(source, direction)] = region_id(
                    region_index
                )
                graph.add_edge(region_id(region_index), neighbour_vertex_id)
                graph.add_edge(region_id(region_index), arc_id(direction))

    # Calculate vertex adjenecy
    for vertex_key, vertex in graph.get_vertices().items():
        for i in range(len(vertex["arcs"])):
            first = vertex["arcs"][i]
            second = vertex["arcs"][(i + 1) % len(vertex["arcs"])]

            graph.add_edge(vertex_key, arc_id(first))
            graph.add_edge(vertex_key, vertex["corners"][corner_id(first, second)])
            graph.add_edge(vertex_key, arc_id(second))

    # Calculate arc adjacency
    for arcKey, arc in graph.get_arcs().items():
        arc_num = int(arcKey[1:])
        # Get connected nodes
        connected_nodes = [
            (vertexKey, vertex)
            for vertexKey, vertex in graph.get_vertices().items()
            if arc_num in vertex["arcs"]
        ]
        first_vertex_key, first_vertex = connected_nodes[0]
        second_vertex_key, second_vertex = connected_nodes[1]

        vertex_arcs = first_vertex["arcs"]
        arc_index = vertex_arcs.index(arc_num)

        arc_left = vertex_arcs[arc_index - 1]
        arc_right = vertex_arcs[(arc_index + 1) % len(vertex_arcs)]

        corner_left_region = first_vertex["corners"][corner_id(arc_left, arc_num)]
        corner_right_region = first_vertex["corners"][corner_id(arc_right, arc_num)]

        graph.add_edge(arcKey, first_vertex_key)
        graph.add_edge(arcKey, corner_left_region)
        graph.add_edge(arcKey, second_vertex_key)
        graph.add_edge(arcKey, corner_right_region)

    return graph
