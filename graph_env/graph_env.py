import networkx as nx
import random

class GraphEnv:
    def __init__(self):
        self.graph = nx.erdos_renyi_graph(n=5, p=0.6)
        self.entry_node = 0
        self.compromised = set()
        self.logs = []

    def get_state(self):
        return [1 if node in self.compromised else 0 for node in self.graph.nodes]

    def attack_node(self, node):
        if node not in self.compromised and node in self.graph.nodes:
            if random.random() < 0.7:
                self.compromised.add(node)
                self.logs.append(f"Node {node} compromised.")
                return True
        return False

    def defend_node(self, node):
        if node in self.compromised:
            self.compromised.remove(node)
            self.logs.append(f"Node {node} secured.")