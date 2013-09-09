def create_graph(tree, graph):
    # create root node
    graph.add_node(tree.id, label='%d:%s' % (tree.col, tree.value))

    # if false branch has results, draw them directly
    if tree.false_branch.results:
        node_id = tree.random_id()
        graph.add_node(node_id,
            label=str(tree.false_branch.results)[1:-1], shape='rect')
        graph.add_edge(tree.id, node_id, label=' no')

    # otherwise, draw them recursively
    else:
        # draw false branch
        label = '%d:%s' % (tree.false_branch.col, tree.false_branch.value)
        graph.add_node(tree.false_branch.id, label=label)
        graph.add_edge(tree.id, tree.false_branch.id, label=' no')

        # traverse the branch recursively
        create_graph(tree.false_branch, graph)

    # if true branch has results, draw them directly
    if tree.true_branch.results:
        node_id = tree.random_id()
        graph.add_node(node_id,
            label=str(tree.true_branch.results)[1:-1], shape='rect')
        graph.add_edge(tree.id, node_id, label=' yes')

    # otherwise, draw them recursively
    else:
        # draw true branch
        label = '%d:%s' % (tree.true_branch.col, tree.true_branch.value)
        graph.add_node(tree.true_branch.id, label=label)
        graph.add_edge(tree.id, tree.true_branch.id, label=' yes')

        # traverse branches recursively
        create_graph(tree.true_branch, graph)

    return graph