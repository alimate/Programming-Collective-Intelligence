from math import sqrt
import random

# calculate pearson correlation
def pearson(vec1, vec2):
    # number of elements
    n = len(vec1)

    # Simple sums
    sum1 = sum(vec1)
    sum2 = sum(vec2)

    # sum of the squares
    sum_sq1 = sum([pow(x, 2) for x in vec1])
    sum_sq2 = sum([pow(x, 2) for x in vec2])

    # sum of the products
    p_sum = sum([vec1[i] * vec2[i] for i in range(n)])

    # Calculate r (Pearson score)
    num = p_sum - sum1 * sum2 / n
    den = sqrt((sum_sq1 - pow(sum1, 2) / n) * (sum_sq2 - pow(sum2, 2) / n))
    if den == 0: return 0

    # transform similarity to closeness
    return 1 - num / den

class BiCluster:
    def __init__(self, vec, left=None, right=None, distance=0.0, id=None):
        self.left = left
        self.right = right
        self.vec = vec
        self.id = id
        self.distance = distance

def hierarchical_clustering(rows, distance=pearson):
    # cache previous calculations
    distances = {}

    # we'll use negative cluster ids for clusters
    # which are merged by two another clusters
    current_cluster_id = -1

    # Clusters are initially just the rows
    clusters = [BiCluster(rows[i], id=i) for i in range(len(rows))]

    # repeat until only one cluster remains
    while len(clusters) > 1:
        # populate initial best matches info
        best_pair = (0, 1)
        closest = distance(clusters[0].vec, clusters[1].vec)

        # loop through every pair looking for the smallest distance
        for i in range(len(clusters)):
            for j in range(i+1, len(clusters)):
                # distances is the cache of distance calculations
                if (clusters[i].id, clusters[j].id) not in distances:
                    distances[(clusters[i].id, clusters[j].id)] = distance(
                        clusters[i].vec, clusters[j].vec
                    )
                d = distances[(clusters[i].id, clusters[j].id)]
                if d < closest:
                    best_pair = (i, j)
                    closest = d
        # end of inner for loop
        # calculate the average of the two clusters
        merged_vec = [
        (clusters[best_pair[0]].vec[i] + clusters[best_pair[1]].vec[i])/2.0
        for i in range(len(clusters[0].vec))]

        # create the new cluster
        new_cluster = BiCluster(merged_vec,
            left=clusters[best_pair[0]],
            right=clusters[best_pair[1]],
            distance=closest,
            id=current_cluster_id
        )

        # cluster ids that weren't in the original set are negative
        current_cluster_id -= 1

        # delete the original clusters, delete the second one first
        # why should we delete the second one earlier?
        # after you delete first element earlier,
        # the clusters[best_pair[1]] no longer exists!
        # it'll shift one index back
        del clusters[best_pair[1]]
        del clusters[best_pair[0]]

        # add the merged cluster
        clusters.append(new_cluster)
    # end of outer while loop
    return clusters[0]

def kmeans_clustering(rows, k, distance=pearson, max_iterations=100):
    # Determine the minimum and maximum values for each variable
    ranges = [
        (min([row[i] for row in rows]), max([row[i] for row in rows]))
        for i in range(len(rows[0]))
    ]

    # Create k randomly placed centroids
    # inner loop generates a random value
    # for each variable in its pre-calculated range
    # outer loop is responsible for creating k
    # random clusters
    clusters = [
        [
            random.uniform(ranges[i][0], ranges[i][1])
            for i in range(len(rows[0]))
        ]
        for j in range(k)
    ]

    # we store last matches to compare them with
    # current best matches, if they were equal
    # then algorithm must halts
    last_matches = None

    for iteration in range(max_iterations):
        print 'Iteration #%s' % iteration
        # create initial best matches for each cluster
        best_matches = [[] for i in range(k)]

        # Find which centroid is the closest for each row
        for i in range(len(rows)):
            row = rows[i]
            best_match = 0
            # compare current row to all clusters
            # and find the closest
            for j in range(k):
                d = distance(clusters[j], row)
                if d < distance(clusters[best_match], row):
                    best_match = j
            # end of most inner for loop
            best_matches[best_match].append(i)
        # end of second most inner for loop
        # If the results are the same as last time
        # then algorithm must halts
        if best_matches == last_matches: break
        last_matches = best_matches

        # Move the centroids to the average of their members
        for i in range(k):
            avgs = [0.0] * len(rows[0])
            if len(best_matches[i]) > 0:
                for rowid in best_matches[i]:
                    for varid in range(len(rows[rowid])):
                        avgs[varid] += rows[rowid][varid]
                for j in range(len(avgs)):
                    avgs[j] /= len(best_matches[i])
                clusters[i] = avgs
    # end of main loop
    return best_matches

def print_clusters(cluster, labels=None, indent=0):
    # indent to make a hierarchy layout
    for i in range(indent): print ' ',

    # negative ids means that this is branch
    if cluster.id < 0:
        print '-'
    # positive ids means that this is an endpoint
    else:
        if not labels: print cluster.id
        else: print labels[cluster.id]

    # now print the right and left branches
    if cluster.left: print_clusters(cluster.left,
        labels=labels, indent=indent+1)
    if cluster.right: print_clusters(cluster.right,
        labels=labels, indent=indent+1)

def transpose_matrix(data):
    new_data = []
    for i in range(len(data[0])):
        new_data.append([data[j][i] for j in range(len(data))])
    return new_data

def scale_down(data, distance=pearson, rate=0.01, max_iterations=1000):
    n = len(data)

    # The real distances between every pair of items
    real_distances = [
        [
            distance(data[i], data[j]) for j in range(n)
        ]
        for i in range(n)
    ]

    # Randomly initialize the starting points
    # of the locations in 2D
    locations = [[random.random(), random.random()] for i in range(n)]
    fake_distances = [[0.0 for j in range(n)] for i in range(n)]

    last_error = None
    for iteration in range(max_iterations):
        # Find projected distances i.e. distances
        # between items in the chart
        for i in range(n):
            for j in range(n):
                fake_distances[i][j] = sqrt(
                    sum([
                        pow(locations[i][x] - locations[j][x], 2)
                        for x in range(len(locations[i]))
                    ])
                )
        # Move points
        gradient = [[0.0, 0.0] for i in range(n)]

        total_error = 0.0
        for i in range(n):
            for j in range(n):
                # if two items are identical, skip them
                if i == j: continue
                # The error is percent difference
                # between the distances
                error_term = (
                                 fake_distances[i][j] - real_distances[i][j]
                                 ) / real_distances[i][j]

                # Each point needs to be moved away
                # from or towards the other
                # point in proportion to
                # how much error it has
                gradient[i][0] += ((locations[i][0] - locations[j][0])
                                   / fake_distances[j][i]) * error_term
                gradient[i][1] += ((locations[i][1] - locations[j][1])
                                   / fake_distances[j][i]) * error_term
                # Keep track of the total error
                total_error += abs(error_term)
        print total_error
        # If the answer got worse by moving the points,
        # we are done
        if last_error and last_error < total_error: break
        last_error = total_error

        # Move each of the points by the
        # learning rate times the gradient
        for k in range(n):
            locations[k][0] -= gradient[k][0] * rate
            locations[k][1] -= gradient[k][1] * rate
    # end of main loop
    return locations