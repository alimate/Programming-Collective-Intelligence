import math
import random
from matplotlib.pylab import *

def euclidean(vec1, vec2):
    distance = 0.0
    for i in range(len(vec1)):
        distance += pow(vec1[i] - vec2[i], 2)

    return math.sqrt(distance)

def get_distances(data, item, distance=euclidean):
    distance_list = []
    for i in range(len(data)):
        vec = data[i]['input']
        distance_list.append((distance(item, vec), i))
    distance_list.sort()
    return distance_list

def knn_estimate(data, item, k=3):
    # get sorted distances
    distance_list = get_distances(data, item)

    # take the average of top k results
    avg = 0.0
    for i in range(k):
        idx = distance_list[i][1]
        avg += data[idx]['output']

    avg /= k
    return avg

def inverse_weight(distance, num=1.0, const=1.0):
    return num / (distance + const)

def subtract_weight(distance, const=1.0):
    if distance > const:
        return 0
    return const - distance

def gaussian_weight(distance, mu=0.0, sigma=1.0):
    sim = 1 / math.sqrt(2 * math.pi) * sigma
    sim *= math.exp(-pow(distance - mu, 2) / 2 * pow(sigma, 2))
    return sim

def weighted_knn(data, item, k=5, weightf=gaussian_weight):
    # get distances
    distance_list = get_distances(data, item)

    # get weighted average
    avg = 0.0
    total_weight = 0.0
    for i in range(k):
        distance = distance_list[i][0]
        idx = distance_list[i][1]
        # convert distance to weight
        weight = weightf(distance)
        avg += weight * data[idx]['output']
        total_weight += weight

    if total_weight == 0: return 0
    avg /= total_weight
    return avg

def divide_data(data, test=0.05):
    train_set = []
    test_set = []
    for row in data:
        if random.random() < test:
            test_set.append(row)
        else:
            train_set.append(row)
    return train_set, test_set

def test_algorithm(algf, train_set, test_set):
    error = 0.0
    for row in test_set:
        guess = algf(train_set, row['input'])
        error += pow(guess - row['output'], 2)
    return error / len(test_set)

def cross_validate(algf, data, trials=100, test=0.05):
    error = 0.0
    for i in range(trials):
        train_set, test_set = divide_data(data, test)
        error += test_algorithm(algf, train_set, test_set)
    return error / trials

def rescale(data, scale):
    scaled_data = []
    for row in data:
        scaled = [scale[i] * row['input'][i]
        for i in range(len(scale))]
        scaled_data.append({'input':scaled, 'output':row['output']})
    return scaled_data

def cost_wrapper(algf, data, trials=10):
    def costf(scale):
        scaled_data = rescale(data, scale)
        return cross_validate(algf, scaled_data, trials=trials)
    return costf

def probability_guess(data, item, low, high, k=5, weightf=gaussian_weight):
    distance_list = get_distances(data, item)
    in_range_weights = 0.0
    total_weights = 0.0

    for i in range(k):
        distance = distance_list[i][0]
        idx = distance_list[i][1]
        # convert distance to weight
        weight = weightf(distance)
        value = data[idx]['output']

        # is this point falls in the range?
        if low <= value <= high:
            in_range_weights += weight
        total_weights += weight

    if total_weights == 0: return 0

    # the probability is the weights in the range
    # divided by all the weights
    return in_range_weights / total_weights

def cumulative_graph(data, item, high, k=5, weightf=gaussian_weight):
    prices = arange(0.0, high, 0.1)
    probs = array([
            probability_guess(data, item, 0, price, k, weightf)
            for price in prices])
    plot(prices, probs)
    show()

def probability_graph(data, item, high, k=5, weightf=gaussian_weight,
                      ss=5.0):
    # ss stands for Spatial Smoothing
    # make a range for the prices
    prices = arange(0.0, high, 0.1)

    # get the probabilities for the entire range
    probs = [probability_guess(data, item, price, price + 0.1, k, weightf)
        for price in prices]

    # smooth them by adding the gaussian of the nearby probabilities
    smoothed = []
    for i in range(len(probs)):
        smoothed_value = 0.0
        for j in range(len(probs)):
            distance = abs(i - j) * 0.1
            weight = gaussian_weight(distance, sigma=ss)
            smoothed_value += weight * probs[j]
        smoothed.append(smoothed_value)
    smoothed = array(smoothed)
    plot(prices, smoothed)
    show()