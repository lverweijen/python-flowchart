import ast
import inspect

from abstracttree import print_tree
from pydot import Dot, Node, Edge, Subgraph


def to_flowchart(f):
    source = inspect.getsource(f)
    module_ast = ast.parse(source)
    print_tree(module_ast)
    function_ast = module_ast.body[0]

    graph = Dot("flowchart")
    graph.set_node_defaults(fontname="consolas")
    graph.set_edge_defaults(fontname="consolas")

    start_node = Node("start", rank="source")
    graph.add_node(start_node)
    head_node, tail_node = collect_nodes(function_ast.body, graph)
    graph.add_edge(Edge(start_node, head_node))

    sink_subgraph = Subgraph(rank="sink")
    stop_node = Node("stop", rank="sink")
    sink_subgraph.add_node(stop_node)
    graph.add_subgraph(sink_subgraph)
    graph.add_edge(Edge(tail_node, stop_node))

    return graph


def collect_nodes(body, graph, loop_head=None, loop_tail=None):
    head_node, tail_node = None, None

    for ast_object in body:
        if isinstance(ast_object, ast.Break):
            next_node, next_tail = loop_tail, None
            label, dir = "break", "none"
        elif isinstance(ast_object, ast.Continue):
            next_node, next_tail = loop_head, None
            label, dir = "continue", "none"
        else:
            next_node, next_tail = handle_node(ast_object, graph, loop_head, loop_tail)
            label, dir = "", "forward"

        if not head_node:
            head_node = next_node
        if tail_node:
            graph.add_edge(Edge(tail_node, next_node, label=label, dir=dir))
        tail_node = next_tail

    return head_node, tail_node


def handle_node(ast_object, graph, loop_head=None, loop_tail=None):
    name = f"{type(ast_object).__name__.casefold()}_{ast_object.lineno}"
    match ast_object:
        case ast.For(target=target_ast, iter=iter_ast):
            head_node = Node(name=name, shape="diamond",
                        label=f"for {ast.unparse(target_ast)} in {ast.unparse(iter_ast)}")
            tail_node = Node(name=f"{name}_tail", shape="point", width=0.01, height=0.01)
            inner_head, inner_tail = collect_nodes(ast_object.body, graph, head_node, tail_node)
            graph.add_node(head_node)
            graph.add_node(tail_node)
            graph.add_edge(Edge(head_node, inner_head, label="next"))
            graph.add_edge(Edge(inner_tail, head_node))
            graph.add_edge(Edge(head_node, tail_node, label="StopIteration", dir="none"))
            return head_node, tail_node

        case ast.While(test=test_ast):
            head_node = Node(name=name, shape="diamond", label=ast.unparse(test_ast))
            tail_node = Node(name=f"{name}_tail", shape="point", width=0.01, height=0.01)
            inner_head, inner_tail = collect_nodes(ast_object.body, graph, head_node, tail_node)

            graph.add_node(head_node)
            graph.add_node(tail_node)
            graph.add_edge(Edge(head_node, tail_node, label="False", dir="none"))
            graph.add_edge(Edge(head_node, inner_head, label="True"))
            graph.add_edge(Edge(inner_tail, head_node))
            return head_node, tail_node

        case ast.If(test=test_ast, orelse=else_ast):
            head_node = Node(name=f"{name}_head", shape="diamond", label=ast.unparse(test_ast))
            tail_node = Node(name=f"{name}_tail", shape="point", width=0.01, height=0.01)

            graph.add_node(head_node)
            graph.add_node(tail_node)

            inner_head, inner_tail = collect_nodes(ast_object.body, graph, loop_head, loop_tail)
            graph.add_edge(Edge(head_node, inner_head, label="True"))

            if inner_tail:  # or break
                graph.add_edge(Edge(inner_tail, tail_node, dir="none"))

            if else_ast:
                inner_head, inner_tail = collect_nodes(else_ast, graph, loop_head, loop_tail)
                graph.add_edge(Edge(head_node, inner_head, label="False"))
                if inner_tail:  # or break
                    graph.add_edge(Edge(inner_tail, tail_node, dir="none"))
            else:
                graph.add_edge(Edge(head_node, tail_node, label="False", dir="none"))

            return head_node, tail_node

        case ast.Match(subject=subject_ast, cases=cases_ast):
            head_node = Node(name=f"{name}_head", shape="diamond", label=ast.unparse(subject_ast))
            tail_node = Node(name=f"{name}_tail", shape="point", width=0.01, height=0.01)

            graph.add_node(head_node)
            graph.add_node(tail_node)

            for case_ast in cases_ast:
                case_head, case_tail = collect_nodes(case_ast.body, graph, loop_head, loop_tail)
                graph.add_edge(Edge(head_node, case_head, label=ast.unparse(case_ast.pattern)))

                if case_tail:  # or break/continue
                    graph.add_edge(Edge(case_tail, tail_node, dir="none"))

            return head_node, tail_node

        case _:
            node = Node(name=name, shape="box", label=ast.unparse(ast_object))
            graph.add_node(node)
            return node, node
