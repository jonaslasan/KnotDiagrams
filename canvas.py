from utility import (
    node_intersection,
    slope,
    line_equation,
    distance,
    circle_intersections,
)

import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle
import numpy as np


def render(graph, gap_size, line_width, show_circle_packing):
    for vertex_index in graph.get_vertices():
        vertex_node = graph.get_node(vertex_index)

        if vertex_node["type"] == "crossing":
            draw_crossing(graph, vertex_index, gap_size)
        else:
            draw_vertex(graph, vertex_index)

        if show_circle_packing:
            draw_boundary(graph, vertex_index)

    for arc_index in graph.get_arcs():
        draw_arc(graph, arc_index)

        if show_circle_packing:
            draw_boundary(graph, arc_index)

    if show_circle_packing:
        for region_index in graph.get_regions():
            draw_boundary(graph, region_index)

    plt.axis("equal")
    plt.show()


def draw_arc(graph, arc_index):
    arc_node = graph.get_node(arc_index)

    vertex_neighbours = list(
        filter(
            lambda x: x[0] == "V",
            graph.get_neighbours(arc_index),
        )
    )

    node_one = graph.get_node(vertex_neighbours[0])
    node_two = graph.get_node(vertex_neighbours[1])

    center, radius, start_angle_deg, end_angle_deg = get_circular_arc(
        node_one, arc_node, node_two
    )
    draw_circular_arc(center, radius, start_angle_deg, end_angle_deg)


def draw_vertex(graph, vertex_index):
    vertex_node = graph.get_node(vertex_index)
    arc_neighbours = list(
        filter(
            lambda x: x[0] == "A",
            graph.get_neighbours(vertex_index),
        )
    )

    node_one = graph.get_node(arc_neighbours[0])
    for i in range(1, len(arc_neighbours)):
        node_next =  graph.get_node(arc_neighbours[i])
        center_next, radius_next, start_angle_deg_next, end_angle_deg_next = get_circular_arc(
            node_one, vertex_node, node_next
        )
        draw_circular_arc(center_next, radius_next, start_angle_deg_next, end_angle_deg_next)


def draw_crossing(graph, crossing_index, gap_size):
    crossing_node = graph.get_node(crossing_index)

    # Draw undercrossing
    node_one_under_index = "A" + str(crossing_node["arcs"][0])
    node_two_under_index = "A" + str(crossing_node["arcs"][2])
    node_one_under = graph.get_node(node_one_under_index)
    node_two_under = graph.get_node(node_two_under_index)
    center_under, radius_under, start_angle_deg_under, end_angle_deg_under = (
        get_circular_arc(node_one_under, crossing_node, node_two_under)
    )

    # Draw overcrossing
    node_one_over_index = "A" + str(crossing_node["arcs"][1])
    node_two_over_index = "A" + str(crossing_node["arcs"][3])
    node_one_over = graph.get_node(node_one_over_index)
    node_two_over = graph.get_node(node_two_over_index)
    center_over, radius_over, start_angle_deg_over, end_angle_deg_over = (
        get_circular_arc(node_one_over, crossing_node, node_two_over)
    )

    intersections = circle_intersections(
        center_under, radius_under, center_over, radius_over
    )
    intersection = intersections[0]

    # Chose intersection inside boundary circle
    node_position = (crossing_node["position"].real, crossing_node["position"].imag)
    if distance(intersections[1], node_position) < crossing_node["radius"]:
        intersection = intersections[1]

    # gap cant be bigger than bounding circle
    gap = min(gap_size, crossing_node["radius"])

    # Undercrossing
    draw_circular_arc(
        center_under, radius_under, start_angle_deg_under, end_angle_deg_under
    )

    # Gap
    draw_gap(intersection, gap)

    # Overcrossing
    draw_circular_arc(
        center_over, radius_over, start_angle_deg_over, end_angle_deg_over
    )


def draw_boundary(graph, node_index):
    node = graph.get_node(node_index)

    circle = plt.Circle(
        (node["position"].real, node["position"].imag),
        node["radius"],
        fill=False,
        linewidth=0.5,
    )
    plt.gca().add_patch(circle)


def get_circular_arc(prev_node, current_node, next_node):
    current_center = (current_node["position"].real, current_node["position"].imag)
    prev_intersection = node_intersection(prev_node, current_node)
    next_intersection = node_intersection(next_node, current_node)

    # Slope of prev_intersection to the center
    slope_prev = slope(prev_intersection, current_center)
    orto_slope_prev = -1 / slope_prev
    x_ortho_prev, y_ortho_prev = prev_intersection
    ortho_line_prev = line_equation(x_ortho_prev, y_ortho_prev, orto_slope_prev)

    slope_next = slope(next_intersection, current_center)
    orto_slope_next = -1 / slope_next
    x_ortho_next, y_ortho_next = next_intersection
    ortho_line_next = line_equation(x_ortho_next, y_ortho_next, orto_slope_next)

    # Orthogonal line intersection point becomes the center of our circular arc
    arc_center_x = (ortho_line_prev(0) - ortho_line_next(0)) / (
        orto_slope_next - orto_slope_prev
    )
    arc_center_y = ortho_line_prev(arc_center_x)
    arc_center = (arc_center_x, arc_center_y)

    # Calculate the vectors from the center to the two points
    arc_start = prev_intersection
    arc_end = next_intersection
    vector1 = np.array(arc_start) - np.array(arc_center)
    vector2 = np.array(arc_end) - np.array(arc_center)

    # Check if the arc should be drawn clockwise or counterclockwise
    cross_product = np.cross(vector1, vector2)
    if cross_product < 0:
        arc_end, arc_start = arc_start, arc_end

    radius = np.sqrt(
        (arc_start[0] - arc_center[0]) ** 2 + (arc_start[1] - arc_center[1]) ** 2
    )
    start_angle_deg = np.degrees(
        np.arctan2(arc_start[1] - arc_center[1], arc_start[0] - arc_center[0])
    )
    end_angle_deg = np.degrees(
        np.arctan2(arc_end[1] - arc_center[1], arc_end[0] - arc_center[0])
    )

    return ((arc_center_x, arc_center_y), radius, start_angle_deg, end_angle_deg)


def draw_circular_arc(center, radius, start_angle_deg, end_angle_deg):
    arc = Arc(
        center,
        2 * radius,
        2 * radius,
        angle=0,
        theta1=start_angle_deg,
        theta2=end_angle_deg,
        edgecolor="black",
        linewidth=1,
    )
    plt.gca().add_patch(arc)


def draw_gap(center, radius):
    arc = Circle(center, radius, color="white")
    plt.gca().add_patch(arc)
