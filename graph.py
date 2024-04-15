from collections import defaultdict


class Graph:
    def __init__(self):
        self.adjacency = defaultdict(list)
        self.nodes = dict()
        self.id_counter = 1

    def add_node(self, key, data = None):
        if key in self.nodes:
            return

        if data == None:
            data = {}

        data["id"] = self.id_counter
        self.id_counter += 1
        data["neighbours"] = []
        data["radius"] = 1
        data["position"] = complex(0, 0)
        data["visited"] = False

        self.nodes[key] = data

    def add_edge(self, u, v):
        if not v in self.adjacency[u]:
            self.adjacency[u].append(v)

    def remove_node(self, u):
        for v in self.adjacency[u]:
            self.adjacency[v].remove(u)

        del self.adjacency[u]
        del self.nodes[u]

    def get_neighbours(self, u):
        return self.adjacency[u]

    def get_vertices(self):
        vertices = {k: v for k, v in self.nodes.items() if k.startswith("V")}
        return vertices

    def get_arcs(self):
        arcs = {k: v for k, v in self.nodes.items() if k.startswith("A")}
        return arcs

    def get_regions(self):
        regions = {k: v for k, v in self.nodes.items() if k.startswith("R")}
        return regions

    def get_keys(self):
        return self.nodes.keys()

    def get_node(self, key):
        return self.nodes[key]
