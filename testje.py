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

def to_flowchart(f):
    source = inspect.getsource(f)
    module_ast = ast.parse(source)
    print_tree(module_ast)
    function_ast = module_ast.body[0]

    graph = Dot("flowchart")
    start_node = Node("start")
    collect_nodes(function_ast.body, graph, start_node)
    return graph


def collect_nodes(ast_objects, graph, exit_node=None):
    last_node = exit_node
    for statement in ast_objects:
        match statement:
            case ast.For(target=target_ast, iter=iter_ast):
                label = f"for {ast.unparse(target_ast)} in {ast.unparse(iter_ast)}"
                node = Node("for", label=label, shape="diamond")
                collect_nodes(statement.body, graph, node)
            case ast.Match(subject=subject_ast, cases=cases_ast):
                node = Node("match", label=f"{ast.unparse(subject_ast)}", shape="diamond")
                for case in cases_ast:
                    # case_str = ast.unparse(case.pattern)
                    # print(f"{ast.unparse(case.pattern)=}")
                    # subnode = Node(name=random_name(), label=ast.unparse(case.pattern))
                    # graph.add_node(subnode)
                    collect_nodes(case.body, graph, node)
            case _:
                node = Node(random_name(), label=ast.unparse(statement))

        graph.add_node(node)
        graph.add_edge(Edge(last_node, node))
        last_node = node


def random_name():
    return str(random.randrange(1000))


graph = to_flowchart(fizzbuzz)
print(graph.to_string())
