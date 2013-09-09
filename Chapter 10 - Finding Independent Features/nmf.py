import random
from numpy import *

def costf(a, b):
    diff = 0
    # loop over every row and column in the matrix
    for i in range(shape(a)[0]):
        for j in range(shape(a)[1]):
            # add together the differences
            diff += pow(a[i, j] - b[i, j], 2)
    return diff

def factorize(v, dimension=10, iteration=50):
    # dimension determines number of features for extraction
    # rows and cols are the number of rows and columns of original matrix
    # in other words, number of items and features, respectively
    rows = shape(v)[0]
    cols = shape(v)[1]

    # initialize the weight and feature matrices with random variables
    w = matrix([[random.random() for j in range(dimension)]
                for i in range(rows)])
    h = matrix([[random.random() for j in range(cols)]
                for i in range(dimension)])

    # perform operation a maximum of iter times
    for i in range(iteration):
        wh = w * h

        # calculate the current difference
        cost = costf(v, wh)

        if i % 10 == 0: print cost

        # terminate if the matrix has been fully factorized
        if cost == 0: break

        # update feature matrix
        num = transpose(w) * v
        den = transpose(w) * w * h

        h = matrix(array(h) * array(num) / array(den))

        # update weights matrix
        num = v * transpose(h)
        den = w * h * transpose(h)

        w = matrix(array(w) * array(num) / array(den))
    return w, h