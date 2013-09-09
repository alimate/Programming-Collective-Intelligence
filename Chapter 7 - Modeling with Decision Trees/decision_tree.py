import string
import random

class DecisionNode:
    def __init__(self, col=-1, value=None, results=None,
                 true_branch=None, false_branch=None
                 ):
        self.id = self.random_id()
        self.col = col
        self.value = value
        self.results = results
        self.true_branch = true_branch
        self.false_branch = false_branch

    def random_id(self, length=50):
        allowed_chars = string.letters + string.digits
        return ''.join([random.choice(allowed_chars)
                        for iter in range(length)])

# divides a set on a specific column
# can handle numerical or nominal data
def divide_set(rows, column, value):
    # make a function that tells us if a row is in
    # the first group (true) or the second one (false)
    split_function = None

    # numerical values
    if isinstance(value, int) or isinstance(value, float):
        split_function = lambda row: row[column] >= value

    # nominal values
    else:
        split_function = lambda row: row[column] == value

    # divide the rows into two sets and return them
    true_set = [row for row in rows if split_function(row)]
    false_set = [row for row in rows if not split_function(row)]

    return true_set, false_set

# create counts of possible results
# the last column of each row is the result
def unique_counts(rows):
    results = {}
    for row in rows:
        # the result is the last column
        result = row[len(row) - 1]
        results.setdefault(result, 0)
        results[result] += 1
    return results

# probability that a randomly placed item will
# be in the wrong category
def gini_impurity(rows):
    total = len(rows)
    counts = unique_counts(rows)

    summation = 0
    for i in counts:
        summation += pow(float(counts[i]) / total, 2)

    return 1 - summation

# Entropy is the sum of f * log(f) across all
# the different possible results
def entropy(rows):
    from math import log
    counts = unique_counts(rows)
    total = len(rows)

    # now calculate the entropy
    subtractions = 0.0
    for i in counts:
        fraction = float(counts[i]) / total
        subtractions -= fraction * log(fraction, 2)

    return subtractions

def variance(rows):
    if len(rows) == 0: return 0

    # the last column of each row is the result
    data = [float(row[len(row) - 1]) for row in rows]

    # calculate the mean
    mean = sum(data) / len(data)

    # calculate the variance
    sigma_sq = sum([pow(value - mean, 2) for value in data]) / len(data)

    return sigma_sq

# build decision tree recursively
def build_tree(rows, scoref=entropy):
    # if there isn't any data, return an empty tree
    if len(rows) == 0: return DecisionNode()

    # calculate current entropy
    current_score = scoref(rows)

    # setup some variables to track the best criteria
    best_gain = 0.0
    best_criteria = None
    best_sets = None

    column_count = len(rows[0]) - 1
    for col in range(column_count):
        # generate the list of different values in
        # this column
        column_values = {}
        for row in rows:
            column_values[row[col]] = 1
        # now try dividing the rows up for each value
        # in this column
        for value in column_values.keys():
            set1, set2 = divide_set(rows, col, value)

            # information gain
            fraction = float(len(set1)) / len(rows)
            gain = current_score - fraction * scoref(set1) - \
                   (1 - fraction) * scoref(set2)
            if gain > best_gain and len(set1) > 0 and len(set2) > 0:
                best_gain = gain
                best_criteria = (col, value)
                best_sets = (set1, set2)
        # end of inner loop
    # end of main loop
    # create the subbranches
    if best_gain > 0:
        true_branch = build_tree(best_sets[0], scoref)
        false_branch = build_tree(best_sets[1], scoref)
        return DecisionNode(
            col=best_criteria[0], value=best_criteria[1],
            true_branch=true_branch, false_branch=false_branch
        )
    else:
        return DecisionNode(results=unique_counts(rows))

def classify(observation, tree):
    # if current node is a leaf, return the results
    if tree.results:
        return tree.results

    # otherwise, first find right branch to follow
    branch = None
    value = observation[tree.col]

    # for numerical data types, the true criterion is
    # that the value in this column is greater than
    # value of current node
    if isinstance(value, int) or isinstance(value, float):
        if value >= tree.value: branch = tree.true_branch
        else: branch = tree.false_branch

    # for other data types, the true criterion is
    # that the value in this column is equal to
    # value of current node
    else:
        if value == tree.value: branch = tree.true_branch
        else: branch = tree.false_branch

    # then, run the function recursively
    return classify(observation, branch)

def prune(tree, threshold, scoref=entropy):
    # if the branches aren't leaves,
    # then prune them recursively
    if not tree.true_branch.results:
        prune(tree.true_branch, threshold, scoref)
    if not tree.false_branch.results:
        prune(tree.false_branch, threshold, scoref)

    # if both the subbranches are now leaves,
    # see if they should merged
    if tree.true_branch.results and tree.false_branch.results:
        true_branch, false_branch = [], []
        for result, count in tree.true_branch.results.items():
            true_branch += [[result]] * count
        for result, count in tree.false_branch.results.items():
            false_branch += [[result]] * count

        # test the difference in entropy
        delta = scoref(true_branch + false_branch) - \
                (scoref(true_branch) + scoref(false_branch)) / 2

        if delta < threshold:
            # merge the branches
            tree.true_branch, tree.false_branch = None, None
            tree.results = unique_counts(true_branch + false_branch)

def md_classify(observation, tree):
    if tree.results:
        return tree.results
    else:
        value = observation[tree.col]

        # if the value is missing, then follow both branches
        if not value:
            # find the final results of each branch
            true_results = md_classify(observation, tree.true_branch)
            false_results = md_classify(observation, tree.false_branch)

            # calculate sum of the frequency of each result
            true_count = sum(true_results.values())
            false_count = sum(false_results.values())

            # calculate weight factor for each branch
            true_weight = float(true_count) / (true_count + false_count)
            false_weight = float(false_count) / (true_count + false_count)

            # prepare the results
            results = {}
            for result, value in true_results.items():
                results.setdefault(result, 0)
                results[result] += value * true_weight
            for result, value in false_results.items():
                results.setdefault(result, 0)
                results[result] += value * false_weight
            return results

        # otherwise, find the right branch to follow
        else:
            branch = None
            if isinstance(value, int) or isinstance(value, float):
                if value >= tree.value: branch = tree.true_branch
                else: branch = tree.false_branch
            else:
                if value == tree.value: branch = tree.true_branch
                else: branch = tree.false_branch
            return md_classify(observation, branch)