import ast
import inspect
from dataclasses import dataclass
from typing import Optional

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
    # head_node, tail_node, sinks = collect_nodes(function_ast.body, graph)
    flow = collect_body(graph, function_ast.body, None)
    # head_node, tail_node, sinks = collect_nodes(function_ast.body, graph)
    head_node = flow.head
    tail_node = flow.tail
    sinks = flow.sinks
    graph.add_edge(Edge(start_node, head_node))

    sink_subgraph = Subgraph(rank="sink")
    if tail_node:
        stop_node = Node("stop", rank="sink")
        sink_subgraph.add_node(stop_node)
        graph.add_edge(Edge(tail_node, stop_node))

    for sink in sinks:
        sink_subgraph.add_node(sink)

    graph.add_subgraph(sink_subgraph)

    return graph


@dataclass
class Flow:
    head: Node
    tail: Optional[Node] = None
    sinks: tuple[Node, ...] = ()


def connect_nodes(graph, node1, node2, **kwargs):
    if node1 is None or node2 is None:
        return None

    edge = Edge(node1, node2, **kwargs)
    graph.add_edge(edge)
    return edge


def collect_body(graph, body, loop_flow: Flow) -> Flow:
    head, tail, sinks = None, None, ()

    for ast_object in body:
        name = f"{type(ast_object).__name__.casefold()}_{ast_object.lineno}"
        match ast_object:
            case ast.Break():
                connect_nodes(graph, head, loop_flow.tail, label="break", dir="none")
                return Flow(head or loop_flow.tail, None, sinks)
            case ast.Continue():
                connect_nodes(graph, head, loop_flow.head, label="continue", dir="none")
                return Flow(head or loop_flow.head, None, sinks)
            case ast.Return() | ast.Raise():
                sink_node = Node(name, shape="oval", label=ast.unparse(ast_object))
                connect_nodes(graph, tail, sink_node)
                return Flow(head or sink_node, None, sinks + (sink_node,))
            case _:
                next_flow = process_construct(graph, ast_object, loop_flow)
                connect_nodes(graph, tail, next_flow.head)
                tail = next_flow.tail
                sinks += next_flow.sinks

                if head is None:
                    head = next_flow.head

    return Flow(head, tail, sinks)


def create_node(graph, **kwargs):
    node = Node(**kwargs)
    graph.add_node(node)
    return node


def process_construct(graph, ast_object, loop_flow=None) -> Flow:
    name = f"{type(ast_object).__name__.casefold()}_{ast_object.lineno}"
    match ast_object:
        case ast.For(body=body, target=target_ast, iter=iter_ast, orelse=orelse):
            head_node = create_node(graph, name=f"{name}_head", shape="block", label=f"for {ast.unparse(target_ast)} in {ast.unparse(iter_ast)}")
            next_node = create_node(graph, name=f"{name}_next", shape="diamond", label=f"next {ast.unparse(target_ast)}?")
            connect_nodes(graph, head_node, next_node)
            tail_node = create_node(graph, name=f"{name}_tail", shape="point", width=0)
            sinks = ()

            if body:
                body_flow = collect_body(graph, body, Flow(head_node, tail_node))
                connect_nodes(graph, next_node, body_flow.head, label="Yes")
                connect_nodes(graph, body_flow.tail, next_node)
                sinks += body_flow.sinks
            if orelse:
                else_flow = collect_body(graph, orelse, loop_flow)
                connect_nodes(graph, next_node, else_flow.head, label="No")
                connect_nodes(graph, else_flow.tail, tail_node, dir="none")
                sinks += else_flow.sinks
            else:
                connect_nodes(graph, next_node, tail_node, label="No", dir="none")

            return Flow(head_node, tail_node, sinks)

        case ast.While(test=test_ast, body=body, orelse=orelse):
            head_node = create_node(graph, name=f"{name}_head", shape="diamond", label=ast.unparse(test_ast) + "?")
            tail_node = create_node(graph, name=f"{name}_tail", shape="point", width=0)
            sinks = ()

            if body:
                body_flow = collect_body(graph, body, Flow(head_node, tail_node))
                connect_nodes(graph, head_node, body_flow.head, label="True")
                connect_nodes(graph, body_flow.tail, head_node)
                sinks += body_flow.sinks
            if orelse:
                else_flow = collect_body(graph, orelse, loop_flow)
                connect_nodes(graph, head_node, else_flow.head, label="False")
                connect_nodes(graph, else_flow.tail, tail_node, dir="none")
                sinks += else_flow.sinks
            else:
                connect_nodes(graph, head_node, tail_node, label="False", dir="none")

            return Flow(head_node, tail_node, sinks)

        case ast.If(test=test_ast, body=body, orelse=orelse):
            head_node = create_node(graph, name=f"{name}_head", shape="diamond", label=ast.unparse(test_ast) + "?")
            tail_node = create_node(graph, name=f"{name}_tail", shape="point", width=0)
            sinks = ()

            if body:
                body_flow = collect_body(graph, body, loop_flow)
                connect_nodes(graph, head_node, body_flow.head, label="True")
                connect_nodes(graph, body_flow.tail, tail_node, dir="none")
                sinks += body_flow.sinks
            if orelse:
                else_flow = collect_body(graph, orelse, loop_flow)
                connect_nodes(graph, head_node, else_flow.head, label="False")
                connect_nodes(graph, else_flow.tail, tail_node, dir="none")
                sinks += else_flow.sinks
            else:
                connect_nodes(graph, head_node, tail_node, label="False", dir="none")

            return Flow(head_node, tail_node, sinks)

        case ast.Match(subject=subject_ast, cases=cases):
            head_node = create_node(graph, name=f"{name}_head", shape="diamond", label=ast.unparse(subject_ast))
            tail_node = create_node(graph, name=f"{name}_tail", shape="point", width=0)
            sinks = ()

            for case_ast in cases:
                body_flow = collect_body(graph, case_ast.body, loop_flow)
                connect_nodes(graph, head_node, body_flow.head, label=ast.unparse(case_ast.pattern))
                connect_nodes(graph, body_flow.tail, tail_node, dir="none")
                sinks += body_flow.sinks

            return Flow(head_node, tail_node, sinks)

        case ast.With(items, body):
            flow = collect_body(graph, body, loop_flow)
            head_node, tail_node = flow.head, flow.tail

            for i, item_ast in enumerate(items):
                enter_node = create_node(graph, name=f"item_{ast_object.lineno}_{i}_enter", shape="parallelogram", label=ast.unparse(item_ast))
                exit_node = create_node(graph, name=f"item_{ast_object.lineno}_{i}_exit", shape="parallelogram", label=f"exit {ast.unparse(item_ast.context_expr)}")
                connect_nodes(graph, enter_node, head_node)
                connect_nodes(graph, tail_node, exit_node)
                head_node, tail_node = enter_node, exit_node

            return Flow(head_node, tail_node, flow.sinks)

        case (ast.Try(body=body, handlers=handlers, orelse=orelse, finalbody=finalbody)
              | ast.TryStar(body=body, handlers=handlers, orelse=orelse, finalbody=finalbody)):
            sg = Subgraph(f"cluster_{name}")
            sg.set_graph_defaults(style="dashed")

            body_flow = collect_body(sg, body, loop_flow)
            graph.add_subgraph(sg)

            handler_node = create_node(graph, name=name + "_begin", label="exceptions?", shape="diamond")
            handler_tail = create_node(graph, name=name + "_end", shape="point", width=0)

            connect_nodes(graph, body_flow.tail, handler_node)

            sinks = ()
            for handler in handlers:
                handler_flow = collect_body(graph, handler.body, loop_flow)
                connect_nodes(graph, handler_node, handler_flow.head, label=ast.unparse(handler.type))
                connect_nodes(graph, handler_flow.tail, handler_tail, dir="none")
                sinks += handler_flow.sinks

            if orelse:
                else_flow = collect_body(graph, orelse, loop_flow)
                sinks += else_flow.sinks
                connect_nodes(graph, handler_node, else_flow.head, label="None")
                connect_nodes(graph, else_flow.tail, handler_tail, dir="none")

            if finalbody:
                final_flow = collect_body(graph, finalbody, loop_flow)
                connect_nodes(graph, handler_tail, final_flow.head)
                tail_node = final_flow.tail
                sinks += final_flow.sinks
            else:
                tail_node = handler_tail

            return Flow(body_flow.head, tail_node, sinks)

        case _:
            node = Node(name=name, shape="box", label=ast.unparse(ast_object))
            graph.add_node(node)
            return Flow(node, node, ())
