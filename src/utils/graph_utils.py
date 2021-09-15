import igraph as ig

def plot_graph(igraph: ig.Graph) -> None:
    visual_style = {
        "bbox": (600, 600),
        "margin": 30,
        "vertex_label_size": 10,
        "edge_label_size": 10,
        "vertex_size": 40
    }
    layout = [(x, -y) for x, y in igraph.vs["coordinate"]]
    for v in igraph.vs:
        if v['is_centroid']:
            v['color'] = 'blue'
    
    for e in igraph.es:
        source = igraph.vs[e.source]
        target = igraph.vs[e.target]

        if not source['is_centroid'] or \
            not target['is_centroid']:
            e['width'] = 0

    centroids = igraph.vs.select(is_centroid_eq=True)
    for centroid in centroids:
        cluster = centroid['cluster']
        for location in cluster:
            edge_id = igraph.get_eid(centroid.index, location.index)
            edge = igraph.es[edge_id]
            edge['width'] = 1

    
    igraph.vs['label'] = [(int(x), int(y)) for x, y in igraph.vs['coordinate']]
    ig.plot(igraph, layout=layout, **visual_style)







