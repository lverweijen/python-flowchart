import ast
import inspect

from abstracttree import print_tree
from pydot import Dot, Node, Edge


def fizzbuzz():
    for i in range(100):
        match (i % 3 == 0, i % 5 == 0):
            case True, True:
                print("FizzBuzz")
            case True, False:
                print("Fizz")
            case False, True:
                print("Buzz")
            case False, False:
                print(i)

def other_function(lo=0, l=[0, 2, 3, 4]):
    keep_running = True
    while (keep_running):
        lo += 1
        for i in range(len(l)):
            if not l[i] < 3:
                # this will effectively
                # stop the while loop:
                keep_running = False
                break
            print(lo)

def to_flowchart(f):
    source = inspect.getsource(f)
    module_ast = ast.parse(source)
    print_tree(module_ast)
    function_ast = module_ast.body[0]

    graph = Dot("flowchart")
    start_node = Node("start", rank="source")
    graph.add_node(start_node)
    head_node, tail_node = collect_nodes(function_ast, graph)
    graph.add_edge(Edge(start_node, head_node))

    stop_node = Node("stop", rank="sink")
    graph.add_edge(Edge(tail_node, stop_node))
    # if tail_nodes:
    #     stop_node = Node("stop", rank="sink")
    #     graph.add_node(stop_node)
    #     for tail in tail_nodes:
    #         graph.add_edge(Edge(tail, stop_node))
    return graph


def collect_nodes(ast_object, graph):
    head_node, tail_node = None, None

    for statement in ast_object.body:
        next_node, next_tail = handle_node(statement, graph)
        if not head_node:
            head_node = next_node
        if tail_node:
            graph.add_edge(Edge(tail_node, next_node))
        tail_node = next_tail

    return head_node, tail_node


def handle_node(ast_object, graph):
    name = f"{type(ast_object).__name__.casefold()}_{ast_object.lineno}"
    match ast_object:
        case ast.For(target=target_ast, iter=iter_ast):
            node = Node(name=name, shape="diamond",
                        label=f"for {ast.unparse(target_ast)} in {ast.unparse(iter_ast)}")
            inner_head, inner_tail = collect_nodes(ast_object, graph)
            graph.add_node(node)
            graph.add_edge(Edge(node, inner_head, label="next"))
            graph.add_edge(Edge(inner_tail, node))
            return node, node# , "StopIteration"

        case ast.While(test=test_ast):
            node = Node(name=name, shape="diamond", label=ast.unparse(test_ast))
            inner_head, inner_tail = collect_nodes(ast_object, graph)
            graph.add_node(node)
            graph.add_edge(Edge(node, inner_head, label="True"))
            graph.add_edge(Edge(inner_tail, node))
            return node, node

        case ast.If(test=test_ast, orelse=else_ast):
            head_node = Node(name=f"{name}_head", shape="diamond", label=ast.unparse(test_ast))
            tail_node = Node(name=f"{name}_tail", shape="point", width=0.01, height=0.01)

            graph.add_node(head_node)
            graph.add_node(tail_node)

            inner_head, inner_tail = collect_nodes(ast_object, graph)
            graph.add_edge(Edge(head_node, inner_head, label="True"))
            graph.add_edge(Edge(head_node, tail_node, label="False"))
            return head_node, tail_node

        case ast.Match(subject=subject_ast, cases=cases_ast):
            head_node = Node(name=f"{name}_head", shape="diamond", label=ast.unparse(subject_ast))
            tail_node = Node(name=f"{name}_tail", shape="point", width=0.01, height=0.01)

            graph.add_node(head_node)
            graph.add_node(tail_node)

            for case_ast in cases_ast:
                case_head, case_tail = collect_nodes(case_ast, graph)
                graph.add_edge(Edge(head_node, case_head, label=ast.unparse(case_ast.pattern)))
                graph.add_edge(Edge(case_tail, tail_node, dir="none"))

            return head_node, tail_node

        case _:
            node = Node(name=name, shape="box", label=ast.unparse(ast_object))
            graph.add_node(node)
            return node, node


# graph = to_flowchart(fizzbuzz)
graph = to_flowchart(other_function)
print(graph.to_string())
