import igraph as ig

def get_node(location_id: int, graph: ig.Graph) -> ig.Vertex:
    return graph.vs.find(location_id_eq=location_id)

def get_edge(source_location_id: int, target_location_id: int, graph: ig.Graph) -> ig.EdgeSeq:
    source_index = graph.vs.find(location_id_eq=source_location_id)
    target_index = graph.vs.find(location_id_eq=target_location_id)
    edge_id = graph.get_eid(source_index, target_index)
    return graph.es[edge_id]

def travel_time(source_location_id: int, target_location_id: int, graph: ig.Graph) -> float:
    edge = get_edge(source_location_id, target_location_id, graph)
    return edge["travel_time"]

def plot_graph(igraph: ig.Graph) -> None:
    visual_style = {
        "bbox": (600, 600),
        "margin": 30,
        "vertex_label_size": 10,
        "edge_label_size": 10,
        "vertex_size": 40
    }
    layout = [(x, -y) for x, y in igraph.vs["coordinate"]]
    igraph.vs['label'] = igraph.vs['coordinate']
    ig.plot(igraph, layout=layout, **visual_style)







