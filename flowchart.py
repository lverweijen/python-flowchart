import ast
import inspect

from abstracttree import print_tree
from pydot import Dot

from helpers import FlowGraphBuilder, Flow


def to_flowchart(f):
    source = inspect.getsource(f)
    module_ast = ast.parse(source)
    print_tree(module_ast)
    function_ast = module_ast.body[0]

    graph = Dot("flowchart")
    graph.set_node_defaults(fontname="consolas")
    graph.set_edge_defaults(fontname="consolas")
    maker = FlowGraphBuilder(graph)

    start_node = maker.create_start()
    flow = collect_body(maker, function_ast.body, None)
    maker.create_edge(start_node, flow.head)

    terminal_maker = maker.build_subgraph(rank="sink")
    if flow.tail:
        stop_node = terminal_maker.create_node(name="stop")
        maker.create_edge(flow.tail, stop_node)

    terminal_graph = terminal_maker.graph
    for terminal in maker.terminals:
        terminal_graph.add_node(terminal)

    graph.add_subgraph(terminal_graph)

    return graph


def collect_body(maker, body, loop_flow: Flow) -> Flow:
    head, tail, sinks = None, None, ()

    for ast_object in body:
        name = f"{type(ast_object).__name__.casefold()}_{ast_object.lineno}"
        match ast_object:
            case ast.Break():
                break_node = maker.create_dummy(name=name)
                maker.create_edge(head, break_node, dir="none")
                maker.create_edge(break_node, loop_flow.tail, label="break", dir="none")
                return Flow(head or break_node, None)
            case ast.Continue():
                continue_node = maker.create_dummy(name=name)
                maker.create_edge(head, continue_node, dir="none")
                maker.create_edge(continue_node, loop_flow.head, label="continue", dir="none")
                return Flow(head or continue_node, None)
            case ast.Return() | ast.Raise():
                terminal = maker.create_terminal(name=name, label=ast.unparse(ast_object))
                maker.create_edge(tail, terminal)
                return Flow(head or terminal)
            case _:
                next_flow = process_construct(maker, ast_object, loop_flow)
                maker.create_edge(tail, next_flow.head)
                tail = next_flow.tail

                if head is None:
                    head = next_flow.head

    return Flow(head, tail)


def process_construct(maker, ast_object, loop_flow=None) -> Flow:
    name = f"{type(ast_object).__name__.casefold()}_{ast_object.lineno}"
    match ast_object:
        case ast.For(body=body, target=target_ast, iter=iter_ast, orelse=orelse):
            head_node = maker.create_action(name=f"{name}_head", label=f"for {ast.unparse(target_ast)} in {ast.unparse(iter_ast)}")
            next_node = maker.create_decision(name=f"{name}_next", label=f"next {ast.unparse(target_ast)}?")
            tail_node = maker.create_dummy(name=f"{name}_tail")
            maker.create_edge(head_node, next_node)

            if body:
                body_flow = collect_body(maker, body, Flow(head_node, tail_node))
                maker.create_edge(next_node, body_flow.head, label="Yes")
                maker.create_edge(body_flow.tail, next_node)
            if orelse:
                else_flow = collect_body(maker, orelse, loop_flow)
                maker.create_edge(next_node, else_flow.head, label="No")
                maker.create_edge(else_flow.tail, tail_node, dir="none")
            else:
                maker.create_edge(next_node, tail_node, label="No", dir="none")

            return Flow(head_node, tail_node)

        case ast.While(test=test_ast, body=body, orelse=orelse):
            head_node = maker.create_action(name=f"{name}_head", label=ast.unparse(test_ast) + "?")
            tail_node = maker.create_dummy(name=f"{name}_tail")

            if body:
                body_flow = collect_body(maker, body, Flow(head_node))
                maker.create_edge(head_node, body_flow.head, label="True")
                maker.create_edge(body_flow.tail, head_node)
            if orelse:
                else_flow = collect_body(maker, orelse, loop_flow)
                maker.create_edge(head_node, else_flow.head, label="False")
                maker.create_edge(else_flow.tail, tail_node, dir="none")
            else:
                maker.create_edge(head_node, tail_node, label="False", dir="none")

            return Flow(head_node, tail_node)

        case ast.If(test=test_ast, body=body, orelse=orelse):
            head_node = maker.create_decision(name=f"{name}_head", label=ast.unparse(test_ast) + "?")
            tail_node = maker.create_dummy(name=f"{name}_tail")

            if body:
                body_flow = collect_body(maker, body, loop_flow)
                maker.create_edge(head_node, body_flow.head, label="True")
                maker.create_edge(body_flow.tail, tail_node, dir="none")
            if orelse:
                else_flow = collect_body(maker, orelse, loop_flow)
                maker.create_edge(head_node, else_flow.head, label="False")
                maker.create_edge(else_flow.tail, tail_node, dir="none")
            else:
                maker.create_edge(head_node, tail_node, label="False", dir="none")

            return Flow(head_node, tail_node)

        case ast.Match(subject=subject_ast, cases=cases):
            head_node = maker.create_decision(name=f"{name}_head", label=ast.unparse(subject_ast))
            tail_node = maker.create_dummy(name=f"{name}_tail")

            for case_ast in cases:
                body_flow = collect_body(maker, case_ast.body, loop_flow)
                maker.create_edge(head_node, body_flow.head, label=ast.unparse(case_ast.pattern))
                maker.create_edge(body_flow.tail, tail_node, dir="none")

            return Flow(head_node, tail_node)

        case ast.With(items, body):
            flow = collect_body(maker, body, loop_flow)
            head_node, tail_node = flow.head, flow.tail

            for i, item_ast in enumerate(items):
                enter_node = maker.create_context(name=f"item_{ast_object.lineno}_{i}_enter", label=ast.unparse(item_ast))
                # exit_node = maker.create_context(name=f"item_{ast_object.lineno}_{i}_exit", label=f"exit {ast.unparse(item_ast.context_expr)}")
                maker.create_edge(enter_node, head_node)
                # maker.create_edge(tail_node, exit_node)
                # head_node, tail_node = enter_node, exit_node
                head_node = enter_node

            return Flow(head_node, tail_node)

        case (ast.Try(body=body, handlers=handlers, orelse=orelse, finalbody=finalbody)
              | ast.TryStar(body=body, handlers=handlers, orelse=orelse, finalbody=finalbody)):

            sg_maker = maker.build_subgraph(f"cluster_{name}", style="dashed", label="try")

            body_flow = collect_body(sg_maker, body, loop_flow)
            maker.graph.add_subgraph(sg_maker.graph)

            handler_node = maker.create_decision(name=name + "_begin", label="exceptions?")
            handler_tail = maker.create_dummy(name=name + "_end")

            maker.create_edge(body_flow.tail, handler_node)

            for handler in handlers:
                handler_flow = collect_body(maker, handler.body, loop_flow)
                maker.create_edge(handler_node, handler_flow.head, label=ast.unparse(handler.type))
                maker.create_edge(handler_flow.tail, handler_tail, dir="none")

            if orelse:
                else_flow = collect_body(maker, orelse, loop_flow)
                maker.create_edge(handler_node, else_flow.head, label="None")
                maker.create_edge(else_flow.tail, handler_tail, dir="none")
            else:
                maker.create_edge(handler_node, handler_tail, label="None")

            if finalbody:
                final_flow = collect_body(maker, finalbody, loop_flow)
                maker.create_edge(handler_tail, final_flow.head)
                tail_node = final_flow.tail
            else:
                tail_node = handler_tail

            return Flow(body_flow.head, tail_node)

        case _:
            node = maker.create_action(name=name, label=ast.unparse(ast_object))
            return Flow(node, node)
