import ast
import inspect
import random

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
                print("Fizz")
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
    head_node, tail_nodes = collect_nodes(function_ast, graph)
    graph.add_edge(Edge(start_node, head_node))
    if tail_nodes:
        stop_node = Node("stop", rank="sink")
        graph.add_node(stop_node)
        for tail in tail_nodes:
            graph.add_edge(Edge(tail, stop_node))
    return graph


def collect_nodes(ast_object, graph):
    head_node = None
    previous_tail_nodes = []

    for statement in ast_object.body:
        name = f"{type(statement).__name__.casefold()}_{statement.lineno}"

        match statement:
            case ast.For(target=target_ast, iter=iter_ast):
                node = Node(name=name, shape="diamond",
                            label=f"for {ast.unparse(target_ast)} in {ast.unparse(iter_ast)}")
                end_loop = Node(name=f"{name}_end", shape="point")

                next_node, back_nodes = collect_nodes(statement, graph)
                graph.add_edge(Edge(node, next_node, label="next"))
                for back_node in back_nodes:
                    graph.add_edge(Edge(back_node, end_loop))
                tail_nodes = [end_loop]  #[node]
                graph.add_node(end_loop)
                graph.add_edge(Edge(end_loop, node))
            case ast.Match(subject=subject_ast, cases=cases_ast):
                node = Node(name=name, shape="diamond",
                            label=ast.unparse(subject_ast))
                tail_node = Node(name=f"{name}_tail", shape="point", width=0.01, height=0.01)
                graph.add_node(tail_node)
                for case_ast in cases_ast:
                    case_head, case_tail = collect_nodes(case_ast, graph)
                    graph.add_edge(Edge(node, case_head, label=ast.unparse(case_ast.pattern)))
                    # tail_nodes.extend(case_tail)
                    for tail in case_tail:
                        graph.add_edge(Edge(tail, tail_node, dir="none"))
                tail_nodes = [tail_node]

            #     node = Node("match", label=f"{ast.unparse(subject_ast)}", shape="diamond")
            #     for case in cases_ast:
            #         next_node, tail_nodes = collect_nodes(case.body, graph)
            case _:
                node = Node(name=name, label=ast.unparse(statement), shape="box")
                tail_nodes = [node]

        graph.add_node(node)
        if head_node is None:
            head_node = node

        print(f"{previous_tail_nodes=}")
        for tail in previous_tail_nodes:
            print("hola")
            graph.add_edge(Edge(tail, node))

        previous_tail_nodes = tail_nodes

        return head_node, tail_nodes

# def to_flowchart2(f):
#     source = inspect.getsource(f)
#     module_ast = ast.parse(source)
#     print_tree(module_ast)
#     function_ast = module_ast.body[0]
#
#     graph = Dot("flowchart")
#     start_node = Node("start")
#     collect_nodes(function_ast.body, graph, start_node)
#     return graph
#
# def collect_nodes2(ast_objects, graph, exit_node=None):
#     last_node = exit_node
#     for statement in ast_objects:
#         match statement:
#             case ast.For(target=target_ast, iter=iter_ast):
#                 label = f"for {ast.unparse(target_ast)} in {ast.unparse(iter_ast)}"
#                 node = Node("for", label=label, shape="diamond")
#                 collect_nodes(statement.body, graph, node)
#             case ast.Match(subject=subject_ast, cases=cases_ast):
#                 node = Node("match", label=f"{ast.unparse(subject_ast)}", shape="diamond")
#                 for case in cases_ast:
#                     # case_str = ast.unparse(case.pattern)
#                     # print(f"{ast.unparse(case.pattern)=}")
#                     # subnode = Node(name=random_name(), label=ast.unparse(case.pattern))
#                     # graph.add_node(subnode)
#                     collect_nodes(case.body, graph, node)
#             case _:
#                 node = Node(random_name(), label=ast.unparse(statement))
#
#         graph.add_node(node)
#         graph.add_edge(Edge(last_node, node))
#         last_node = node


def random_name():
    return str(random.randrange(1000))


graph = to_flowchart(fizzbuzz)
# graph = to_flowchart(other_function)
print(graph.to_string())
