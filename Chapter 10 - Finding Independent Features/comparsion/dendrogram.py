import Image, ImageDraw

def get_height(tree):
    # Is this an endpoint? Then the height is just 1
    if not tree.left and not tree.right: return 1

    # otherwise, the height is the sum of
    # the heights of each branch
    return get_height(tree.left) + get_height(tree.right)

def get_depth(tree):
    # The distance of an endpoint is 0.0
    if not tree.left and not tree.right: return 0

    # otherwise, The distance of a branch is the
    # greater of its two sides plus its own distance
    return max(get_depth(tree.left), get_depth(tree.right)) + tree.distance

def draw_dendrogram(cluster, labels, output='clusters.jpeg'):
    # height and width
    height = get_height(cluster) * 20
    width = 1200
    depth = get_depth(cluster)

    # width is fixed, so scale distances accordingly
    scaling = float(width - 150) / depth

    # create a new image with a white background
    img = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    draw.line((0, height / 2, 10, height / 2), fill=(255, 0, 0))

    # draw the first node
    draw_node(draw, cluster, 10, height / 2, scaling, labels)
    img.save(output, 'JPEG')

def draw_node(draw, cluster, x, y, scaling, labels):
    if cluster.id < 0:
        left_height = get_height(cluster.left) * 20
        right_height = get_height(cluster.right) * 20
        top = y - (left_height + right_height) / 2
        bottom = y + (left_height + right_height) / 2
        # line length
        line_len = cluster.distance * scaling
        # Vertical line from this cluster to children
        draw.line((x, top + left_height / 2, x, bottom - right_height / 2),
        fill=(255, 0, 0))

        # Horizontal line to left item
        draw.line((x, top + left_height / 2,
                   x + line_len, top + left_height / 2),
        fill=(255, 0, 0))

        # Horizontal line to right item
        draw.line((x, bottom - right_height / 2,
                   x + line_len, bottom - right_height / 2),
        fill=(255, 0, 0))

        # Call the function to draw the left and right nodes
        draw_node(draw, cluster.left, x + line_len,
            top + left_height / 2, scaling, labels)
        draw_node(draw, cluster.right, x + line_len,
            bottom - right_height / 2, scaling, labels)
    else:
        # If this is an endpoint, draw the item label
        draw.text((x + 5, y -7), labels[cluster.id], (0, 0, 0))