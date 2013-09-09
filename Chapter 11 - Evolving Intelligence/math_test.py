from random import randint

def hidden_function(x, y):
    return pow(x, 2) + 2 * y + 3 * x + 5

def build_hidden_set(trials=200):
    rows = []
    for i in range(trials):
        x = randint(0, 40)
        y = randint(0, 40)
        rows.append([x, y, hidden_function(x, y)])
    return rows

def score_function(tree, dataset):
    diff = 0
    for data in dataset:
        value = tree.evaluate([data[0], data[1]])
        diff += abs(value - data[2])
    return diff