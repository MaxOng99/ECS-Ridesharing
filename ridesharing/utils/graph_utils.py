import igraph as ig
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from models.graph import Graph

def plot_graph(graph: Graph, path: str) -> None:
    
    data = dict()
    igraph = graph.igraph
    centroids = list(igraph.vs.select(is_centroid_eq=True))

    for centroid_id, centroid in enumerate(centroids):
        x, y = centroid['coordinate']
        locations = centroid['cluster']

        data[centroid['location_id']] = {
            "x": x,
            "y": y,
            "cluster": centroid_id,
            "is_cluster": True
        }

        for location in locations:
            x, y = location['coordinate']
            data[location['location_id']] = {
                "x": x,
                "y": y,
                "cluster": centroid_id,
                "is_cluster": False
            }

    sns.set_style("whitegrid")
    fig, ax = plt.subplots()
    df = pd.DataFrame.from_dict(data, orient='index')

    for _, point in df.iterrows():
        if point['is_cluster']:
            ax.text(point['x'], point['y'], point['cluster'])
    colors = sns.color_palette("deep", len(centroids))

    sns.scatterplot(data=df , x="x", y="y", hue="cluster", palette=colors, ax=ax)
    fig.savefig(path)

def plot_beta_distribution(distribution, path):
    sns.displot(distribution, kind="hist")
    plt.xlabel("beta")
    plt.subplots_adjust(bottom=0.1)
    plt.savefig(path)

def plot_preference_distribution(dist, path):

    # Convert unit time to hours
    depart_times = []
    arrive_times = []

    for x, y in dist:
        depart_times.append(x/60)
        arrive_times.append(y/60)


    df = pd.concat(axis=0, ignore_index=True, objs=[
        pd.DataFrame.from_dict({'hours': depart_times, 'journey_type': 'depart_times'}),
        pd.DataFrame.from_dict({'hours': arrive_times, 'journey_type': 'arrive_times'})
    ])
    fig, ax = plt.subplots()
    sns.histplot(data=df, x='hours', hue='journey_type', multiple='dodge', ax=ax)
    plt.savefig(path)









