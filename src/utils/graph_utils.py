import igraph as ig

def get_node(node_id, igraph):
    return igraph.vs.find(identifier_eq=node_id)

def get_edge(source_node_id, target_node_id, igraph):
    source_index = igraph.vs.find(identifier_eq=source_node_id)
    target_index = igraph.vs.find(identifier_eq=target_node_id)
    edge_id = igraph.get_eid(source_index, target_index)
    return igraph.es[edge_id]

def travel_time(source_id, target_id, igraph):
    edge = get_edge(source_id, target_id, igraph)
    return edge["travel_time"]

def plot_graph(igraph):
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







