from dataclasses import dataclass
from typing import Optional

from pydot import Node, Edge, Subgraph, Graph


class FlowGraphBuilder:
    def __init__(self, graph: Graph | Subgraph = None):
        if graph is None:
            graph = Graph()
        self.graph = graph
        self.terminals = []

    def create_node(self, **kwargs):
        node = Node(**kwargs)
        self.graph.add_node(node)
        return node

    def create_start(self, name="start", **kwargs):
        return self.create_node(name=name, **kwargs, shape="block", style="rounded")

    def create_action(self, **kwargs):
        return self.create_node(**kwargs, shape="block")

    def create_setup(self, **kwargs):
        # In my opinion a loop is both an action (spit out elements) and a decision (decide if continue).
        return self.create_node(**kwargs, shape="hexagon")

    def create_decision(self, **kwargs):
        return self.create_node(**kwargs, shape="diamond")

    def create_dummy(self, **kwargs):
        return self.create_node(**kwargs, shape="point", width=0)

    def create_context(self, **kwargs):
        return self.create_node(**kwargs, shape="parallelogram")

    def create_terminal(self, **kwargs):
        terminal = Node(**kwargs, shape="block", style="rounded")
        self.terminals.append(terminal)
        return terminal

    def create_edge(self, node1, node2, **kwargs):
        if node1 is None or node2 is None:
            return None

        edge = Edge(node1, node2, **kwargs)
        self.graph.add_edge(edge)
        return edge

    def build_subgraph(self, name=None, **kwargs):
        sg = Subgraph(name, **kwargs)
        return FlowGraphBuilder(sg)


@dataclass
class Flow:
    head: Node
    tail: Optional[Node] = None
