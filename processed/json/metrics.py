import json
import networkx as nx
from community import community_louvain


def calculate_metrics(file_path):
    G = nx.Graph()

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        relations = data.get("relations", [])
        for rel in relations:
            G.add_edge(rel["object1"], rel["object2"])

        if G.number_of_nodes() > 0:
            partition = community_louvain.best_partition(G)
            modularity = community_louvain.modularity(partition, G)
        else:
            modularity = 0

        print(f"Кількість вузлів: {G.number_of_nodes()}")
        print(f"Кількість ребер: {G.number_of_edges()}")
        print(f"Модулярність: {modularity:.4f}")

    except Exception:
        pass


if __name__ == "__main__":
    calculate_metrics("versalskidogovir.json")