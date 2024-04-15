import planar_diagram
import codes

# Theta-curve
planar_diagram.render(codes.PD["t4_1.2"])

# Knot
planar_diagram.render(codes.PD["4_1"])

# Composite link
planar_diagram.render(codes.PD["2^2_1#2^2_1"], show_circle_packing=True)
