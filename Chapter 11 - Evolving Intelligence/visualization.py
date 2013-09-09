from gp import *

def create_graph(nodes, graph):
    add_node(nodes, graph)
    # if current node is a function node,
    # then loop over its children
    if isinstance(nodes, Node):
        for child in nodes.children:
            add_node(child, graph)
            graph.add_edge(nodes.id, child.id)
            create_graph(child, graph)

    return graph

def add_node(node, graph):
    # if node is a function node
    if isinstance(node, Node):
        graph.add_node(node.id, label=node.name)

    # if node is a parameter node
    elif isinstance(node, ParamNode):
        graph.add_node(node.id, label='Param %d' % node.idx , shape='rect')

    # if node is a constant node
    elif isinstance(node, ConstNode):
        graph.add_node(node.id, label=node.value, shape='rect')
