import Image, ImageDraw

def create_graph(cluster, labels, graph, parent=None):
    # if cluster id is negative, then this is a branch
    if cluster.id < 0:
        graph.add_node(cluster.id, label='')
        # if this node has parent, then draw an
        # edge from parent to child
        if parent:
            graph.add_edge(parent.id, cluster.id)

        # add left and right branches recursively
        if cluster.left: create_graph(cluster.left, labels, graph, cluster)
        if cluster.right: create_graph(cluster.right, labels, graph, cluster)
    # otherwise, this is an endpoint and has a label
    else:
        graph.add_node(labels[cluster.id])
        if parent:
            graph.add_edge(parent.id, labels[cluster.id])
    return graph

def kmeans_graph(clusters, labels, graph):
    for clusterid in range(len(clusters)):
        cluster = clusters[clusterid]
        if cluster:
            # add root node
            graph.add_node(clusterid, label='')

            # loop over all items in this cluster
            for item in cluster:
                graph.add_edge(clusterid, labels[item])
    return graph

def draw_2d(data, labels, output='mds2d.jpeg'):
    img = Image.new('RGB', (2000, 2000), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    for i in range(len(data)):
        x = (data[i][0] + 0.5) * 1000
        y = (data[i][1] + 0.5) * 1000
        draw.text((x, y), labels[i], (0, 0, 0))
    img.save(output, 'JPEG')