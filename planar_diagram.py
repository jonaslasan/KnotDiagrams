import code_parser
import circle_packing
import canvas


def render(
    pd_code: str,
    gap_size: float = 0.02,
    line_width: float = 1,
    show_circle_packing: bool = False,
):
    meta_graph = code_parser.get_meta_graph(pd_code)
    meta_circle_packing = circle_packing.CirclePack(meta_graph)
    canvas.render(meta_circle_packing.graph, gap_size, line_width, show_circle_packing)
