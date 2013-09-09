import math

def linear_classifier(rows):
    averages = {}
    counts = {}

    for row in rows:
        # get the class of this point
        category = row.match

        averages.setdefault(category, [0.0] * len(row.data))
        counts.setdefault(category, 0)

        # add this point to the averages
        for i in range(len(row.data)):
            averages[category][i] += float(row.data[i])

        # keep track of how many points in each class
        counts[category] += 1
    # end of for loop

    # calculate average points
    for category, average in averages.items():
        for i in range(len(average)):
            average[i] /= counts[category]

    return averages

def dot_product(vec1, vec2):
    return sum([vec1[i] * vec2[i] for i in range(len(vec1))])

def dot_product_classify(point, avgs):
    temp = (dot_product(avgs[1], avgs[1]) -
            dot_product(avgs[0], avgs[0])) / 2
    sign = dot_product(point, avgs[0]) - dot_product(point, avgs[1]) + temp
    if sign > 0: return 0
    return 1

def rbf(vec1, vec2, gamma=20):
    # calculate the euclidean distance squared
    squared_distance = sum(
        [
            pow(vec1[i] - vec2[i], 2)
            for i in range(len(vec1))
        ]
    )
    return math.exp(- gamma * squared_distance)

def nonlinear_classifier(point, rows, offset, gamma=10):
    # initialize some variables
    # sum and number of elements classified in first class
    sum0 = 0.0
    count0 = 0
    # sum and number of elements classified in second class
    sum1 = 0.0
    count1 = 0

    for row in rows:
        if row.match == 0:
            sum0 += rbf(point, row.data, gamma)
            count0 += 1
        else:
            sum1 += rbf(point, row.data, gamma)
            count1 += 1

    # calculate the sign
    sign = (1.0 / count0) * sum0 - (1.0 / count1) * sum1 + offset

    if sign > 0: return 0
    return 1

def get_offset(rows, gamma=10):
    # set of elements classified in
    # first and second class, respectively
    set0 = []
    set1 = []

    for row in rows:
        if row.match == 0: set0.append(row.data)
        else: set1.append(row.data)

    # calculate the offset
    sum0 = sum(sum([rbf(v1, v2, gamma) for v1 in set0]) for v2 in set0)
    sum1 = sum(sum([rbf(v1, v2, gamma) for v1 in set1]) for v2 in set1)

    offset = (1.0 / pow(len(set1), 2)) * sum1 \
             - (1.0 / pow(len(set0), 2)) * sum0
    return offset