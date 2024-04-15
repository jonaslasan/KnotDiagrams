import math
import copy
from collections import defaultdict
from utility import norm


class CirclePack:
    def __init__(self, graph):
        self.graph = graph

        self.tolerance_radii = 1e-12
        self.tolerance_positions = 0.003

        # Infinite region = region with the most adjacent nodes
        regions = [(x, len(graph.adjacency[x])) for x in graph.get_regions()]
        self.outer_region = max(regions, key=lambda x: x[1])[0]

        self.get_anchors()

        self.neighbors_lists_sizes = {}

        for key, adjacencyList in graph.adjacency.items():
            self.neighbors_lists_sizes[key] = len(adjacencyList)

        self.compute_radii()
        self.compute_positions()

        # Remove the infinite region
        self.graph.remove_node(self.outer_region)

        self.apply_mobius(complex(0, 0), complex(1, 0), complex(1, 0), complex(0, 0))

        self.original_packing = copy.deepcopy(self.graph)

        optimal_mobius = self.optimal_mobius()
        self.optimal_mobius = optimal_mobius

        self.apply_mobius(
            optimal_mobius[0], optimal_mobius[1], optimal_mobius[2], optimal_mobius[3]
        )

    # Initial circles to pack around = outer regions with first two neighbours
    def get_anchors(self):
        neighbours = self.graph.get_neighbours(self.outer_region)
        self.one = neighbours[0]
        self.two = neighbours[-1]

    def compute_radii(self):
        k = 0
        counter = 0
        tol = self.tolerance_radii
        error = 1000

        while error > tol:
            counter += 1
            self.update_radii()
            k += 1

            if k == 128:
                error = self.compute_error()
                k = 0

    def update_radii(self):
        new_radii = {}

        for key in self.graph.get_keys():
            if key != self.one and key != self.two and key != self.outer_region:
                new_radii[key] = self.radius_update(key)
            else:
                new_radii[key] = 1

        for key, value in new_radii.items():
            self.graph.get_node(key)["radius"] = value

    def radius_update(self, key):
        n = len(self.graph.get_neighbours(key))
        s = math.sin(self.total_neighbors_angle(key) * 0.5 / n)
        rv = self.graph.get_node(key)["radius"] * s / (1 - s)
        s = math.sin(math.pi / n)
        return (1 - s) * rv / s

    def total_neighbors_angle(self, key):
        neighbours = []
        res = 0
        a = 0
        b = 0
        c = 0
        t = 0

        neighbours = self.graph.get_neighbours(key)
        v = len(neighbours)

        for i in range(len(neighbours)):
            first = neighbours[i]
            second = neighbours[(i + 1) % v]

            a = (
                self.graph.get_node(first)["radius"]
                + self.graph.get_node(key)["radius"]
            )
            b = (
                self.graph.get_node(second)["radius"]
                + self.graph.get_node(key)["radius"]
            )
            c = (
                self.graph.get_node(first)["radius"]
                + self.graph.get_node(second)["radius"]
            )

            t = (a * a + b * b - c * c) / (2 * a * b)

            if t > 1:
                print("Can't take acos of " + str(t))
            elif t < -1:
                print("Can't take acos of " + str(t))
                res += math.pi
            else:
                res += math.acos(t)

        return res

    def compute_error(self):
        res = 0
        temp = 0
        i = 1

        for key in self.graph.get_keys():
            if key != self.one and key != self.two and key != self.outer_region:
                temp = 2 * math.pi - self.total_neighbors_angle(key)
                res += temp * temp

        return math.sqrt(res)

    def compute_next_position(
        self, pivot_affix, neighbour_affix, pivot_radius, neighbour_radius, next_radius
    ):
        a = pivot_radius + neighbour_radius
        b = pivot_radius + next_radius
        c = neighbour_radius + next_radius
        x = (a * a + b * b - c * c) / (2 * a)
        y = math.sqrt(b * b - x * x)
        u = neighbour_affix - pivot_affix

        res = pivot_affix + (complex(x, y) * (u / abs(u)))
        return res

    def compute_positions(self):
        oneX = (
            self.graph.get_node(self.outer_region)["radius"]
            + self.graph.get_node(self.one)["radius"]
        )
        self.graph.get_node(self.outer_region)["position"] = complex(0, 0)
        self.graph.get_node(self.one)["position"] = complex(oneX, 0)

        placements = defaultdict(lambda: False)
        placements[self.outer_region] = True
        placements[self.one] = True

        nb_positioned = 2
        j = 0

        neighbours = self.graph.get_neighbours(self.outer_region)

        k = 0

        for k in range(1, len(neighbours), 1):
            positionZero = self.graph.get_node(self.outer_region)["position"]
            radiusZero = self.graph.get_node(self.outer_region)["radius"]
            positionNext = self.graph.get_node(neighbours[k - 1])["position"]
            radiusNext = self.graph.get_node(neighbours[k - 1])["radius"]
            radiusK = self.graph.get_node(neighbours[k])["radius"]

            self.graph.get_node(neighbours[k])["position"] = self.compute_next_position(
                positionZero, positionNext, radiusZero, radiusNext, radiusK
            )

            placements[neighbours[k]] = True
            nb_positioned += 1

        i = -1

        node_keys = list(self.graph.get_keys())
        n = len(node_keys)

        while nb_positioned < n:
            i += 1
            i %= n
            key = node_keys[i]
            if not placements[key]:
                continue

            neighbours = self.graph.get_neighbours(key)
            j = 1
            while j < len(neighbours) and not placements[neighbours[j]]:
                j += 1
            if j == len(neighbours):
                continue

            for k in range(1, len(neighbours), 1):
                if placements[neighbours[(j + k) % len(neighbours)]]:
                    continue

                a = self.graph.get_node(key)["position"]
                b = self.graph.get_node(neighbours[(j + k - 1) % len(neighbours)])[
                    "position"
                ]
                c = self.graph.get_node(key)["radius"]
                d = self.graph.get_node(neighbours[(j + k - 1) % len(neighbours)])[
                    "radius"
                ]
                e = self.graph.get_node(neighbours[(j + k) % len(neighbours)])["radius"]
                self.graph.get_node(neighbours[(j + k) % len(neighbours)])[
                    "position"
                ] = self.compute_next_position(a, b, c, d, e)

                placements[neighbours[(j + k) % len(neighbours)]] = True
                nb_positioned += 1

    def optimal_mobius(self):
        A = 0
        C = 0
        S = 0

        for k in self.graph.nodes:
            z_k = self.graph.get_node(k)["position"]
            r_k = self.graph.get_node(k)["radius"]
            rho_k = abs(z_k)
            cos_k = (z_k / rho_k).real
            sin_k = (z_k / rho_k).imag
            b_k = rho_k / r_k
            C += b_k * cos_k
            S += b_k * sin_k
            A += (rho_k * rho_k - r_k * r_k + 1.0) / r_k

        theta = math.atan(S / C)
        cos_theta = math.cos(theta)
        sin_theta = math.sin(theta)

        u = -(C * cos_theta + S * sin_theta)
        B = 0.5 * A / u
        discrim_reduit = B * B - 1

        if discrim_reduit < 0:
            print("Negative discriminant")
            return (complex(1), complex(0), complex(1), complex(0))

        rac = math.sqrt(discrim_reduit)
        rho = -B - rac

        res = complex(rho * cos_theta, rho * sin_theta)
        first = -res
        second = -res.conjugate()
        return (complex(1), first, second, complex(1))

    def apply_mobius(self, a, b, c, d):
        for vertexKey, vertex in self.graph.nodes.items():
            z = vertex["position"]
            r = vertex["radius"]

            newCenter = (
                (a * z + b) * (c * z + d).conjugate() - r * r * a * c.conjugate()
            ) / (norm(c * z + d) - r * r * norm(c))
            newRadius = r * abs(a * d - b * c) / abs(norm(c * z + d) - r * r * norm(c))
            vertex["position"] = newCenter
            vertex["radius"] = newRadius

    def mobius(self, a, b, c, d):
        new_graph = copy.deepcopy(self.original_packing)
        self.graph = new_graph

        self.apply_mobius(a, b, c, d)
