import math
import numpy as np

def node_intersection(node1, node2):
    x1 = node1["position"].real
    y1 = node1["position"].imag
    r1 = node1["radius"]
    x2 = node2["position"].real
    y2 = node2["position"].imag

    vector = (x2 - x1, y2 - y1)
    magnitude = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
    unit_vector = (vector[0] / magnitude, vector[1] / magnitude)

    intersection = (x1 + unit_vector[0] * r1, y1 + unit_vector[1] * r1)

    return intersection

def norm(z):
    return z.real * z.real + z.imag * z.imag

def slope(point1, point2):
    return (point2[1] - point1[1]) / (point2[0] - point1[0])

def line_equation(x, y, m):
    b = y - m * x
    return lambda x: m * x + b

def circle_intersections(center0, r0, center1, r1):
        x0 = center0[0]
        y0 = center0[1]
        x1 = center1[0]
        y1 = center1[1]

        c0 = np.array([x0, y0])
        c1 = np.array([x1, y1])
        v = c1 - c0
        d = np.linalg.norm(v)
    
        if d > r0 + r1 or d == 0:
            return None
        
        u = v/np.linalg.norm(v)
        xvec = c0 + (d**2 - r1**2 + r0**2)*u/(2*d)
    
        uperp = np.array([u[1], -u[0]])
        a = ((-d+r1-r0)*(-d-r1+r0)*(-d+r1+r0)*(d+r1+r0))**0.5/d
        return (xvec + a*uperp/2, xvec - a*uperp/2)

def distance(p1, p2):
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)