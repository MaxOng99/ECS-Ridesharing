import csv
from typing import Counter

import igraph as ig
import numpy as np
from haversine import haversine, Unit

class Graph:
    def __init__(self, igraph) -> None:
        self.igraph = igraph

    def locations(self):
        return [vertex['location_id'] for vertex in self.igraph.vs]
        
    def find_edge(self, source_id, target_id) -> ig.Edge:
        source_vertex = self.igraph.vs.find(location_id_eq=source_id)
        target_vertex = self.igraph.vs.find(location_id_eq=target_id)

        if source_id == target_id:
            return None
        else:
            eid = self.igraph.get_eid(source_vertex.index, target_vertex.index)
            return self.igraph.es[eid]

    def find_vertex(self, loc_id) -> ig.Vertex:
        return self.igraph.vs.find(location_id_eq=loc_id)

    def travel_time(self, source_id, target_id) -> int:
        edge = self.find_edge(source_id, target_id)
        return 0 if edge is None else edge['travel_time']

    def distance(self, source_id, target_id) -> int:
        edge = self.find_edge(source_id, target_id)
        return 0 if edge is None else edge['distance']

class DatasetGraphGenerator:

    def __init__(self, graph_seed, graph_params) -> None:
        self.avg_vehicle_speed = graph_params['avg_vehicle_speed']
        self.num_locations = graph_params['num_locations']
        self.locality = graph_params['locality']
        self.seed = graph_seed
        np.random.seed(100)
        self.graph = Graph(self.__generate_graph())

    def __generate_graph(self):
        with open(f"./dataset/westminster_hackney_stops.csv", "r", encoding='utf-8-sig') as file:
            records = list(csv.DictReader(file))

            # filter duplicates by ATCOCode
            codes = [record['ATCOCode'] for record in records]
            counter = Counter(codes)
            duplicate_records = \
                list(filter(lambda pair: pair[1] > 1, counter.items()))
            duplicate_codes = [key for key, val in duplicate_records]

            filtered_records = [record for record in records if record['ATCOCode'] not in duplicate_codes]
            igraph = ig.Graph.Full(n=self.num_locations)
            self.__generate_vertex_props(igraph, filtered_records)
            self.__generate_edge_props(igraph)

        return igraph

    def __generate_vertex_props(self, igraph, records):

        locality_info = {
            "Westminster": {
                "ATCOCode": "490003384SA",
                "Coordinate": (-0.13663328, 51.49742493),
                "max_stations": 66
            },
            "Hackney": {
                "ATCOCode": "490009644E",
                "Coordinate": (-0.056845911, 51.54654249),
                "max_stations": 60
            }
        }

        loc_ids = []
        coordinates = []
        info = locality_info[self.locality]
        records_by_locality = \
            list(filter(
                lambda record: record.get("LocalityName") == self.locality and not record.get("ATCOCode") == info['ATCOCode'],
                records)
            )
        records_indices = np.random.choice(len(records_by_locality), size=self.num_locations-1, replace=False)
        records_by_locality = [records_by_locality[index] for index in records_indices]
        for record in records_by_locality:
            loc_ids.append(record.get("ATCOCode"))
            coordinates.append((float(record.get("Latitude")), float(record.get("Longitude"))))

        loc_ids.append(info['ATCOCode'])
        coordinates.append(info['Coordinate'])

        igraph.vs['location_id'] = loc_ids
        igraph.vs['coordinate'] = coordinates

    def __generate_edge_props(self, igraph):

        for edge in igraph.es:
            source_vertex = igraph.vs[edge.source]
            target_vertex = igraph.vs[edge.target]
            
            source_coordinates = source_vertex["coordinate"]
            target_coordinate = target_vertex["coordinate"]
            distance = haversine(source_coordinates, target_coordinate, unit=Unit.METERS)

            speed = self.avg_vehicle_speed * 1000 / 60

            travel_time = round(distance / speed, 2)
            edge["distance"] = int(distance)
            edge["travel_time"] = int(travel_time)
