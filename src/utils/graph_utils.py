import igraph as ig

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







