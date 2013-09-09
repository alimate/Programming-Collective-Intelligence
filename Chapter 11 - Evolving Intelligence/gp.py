from random import random, randint, choice
from copy import deepcopy
from math import log
import string

def generate_node_id(length=50):
    allowed_chars = string.letters + string.digits
    return ''.join([choice(allowed_chars) for iter in range(length)])

class FunctionWrapper:
    def __init__(self, function, child_count, name):
        self.function = function
        self.child_count = child_count
        self.name = name

class Node:
    def __init__(self, function_wrapper, children):
        self.id = generate_node_id()
        self.function = function_wrapper.function
        self.name = function_wrapper.name
        self.children = children

    def evaluate(self, params):
        results = [child.evaluate(params) for child in self.children]
        return self.function(results)

class ParamNode:
    def __init__(self, idx):
        self.id = generate_node_id()
        self.idx = idx

    def evaluate(self, params):
        return params[self.idx]

class ConstNode:
    def __init__(self, value):
        self.id = generate_node_id()
        self.value = value

    def evaluate(self, params):
        return self.value

# add 'add' wrapper function
add_wrapper = FunctionWrapper(
    lambda params: params[0] + params[1], 2, 'add')

# add 'subtract' wrapper function
subtract_wrapper = FunctionWrapper(
    lambda params: params[0] - params[1], 2, 'subtract')

# add 'multiply' wrapper function
multiply_wrapper = FunctionWrapper(
    lambda params: params[0] * params[1], 2, 'multiply')

# add 'if' wrapper
def if_structure(params):
    if params[0] > 0: return params[1]
    return params[2]
if_wrapper = FunctionWrapper(if_structure, 3, 'if')

# add 'is_greater_than' wrapper
def is_greater_than(params):
    if params[0] > params[1]: return 1
    return 0
gt_wrapper = FunctionWrapper(is_greater_than, 2, 'is greater')

function_list = [add_wrapper, subtract_wrapper,
                 multiply_wrapper, if_wrapper, gt_wrapper]

def example_tree():
    return Node(
        # wrapper function
        if_wrapper,
        # list of children
        [
            Node(gt_wrapper, [ParamNode(0), ConstNode(3)]),
            Node(add_wrapper, [ParamNode(1), ConstNode(5)]),
            Node(subtract_wrapper, [ParamNode(1), ConstNode(2)])
        ]
    )

def make_random_tree(params_count, max_depth=4, function_prob=0.5,
                     params_prob=0.6):
    # params_count is the number of parameters
    # that the tree will take as input
    # function_prob is the probability that the
    # new node created will be a function node
    # params_prob is the probability that it will be a
    # parameter node if it is not a function node
    # otherwise, it'll be constant node
    if random() < function_prob and max_depth > 0:
        function = choice(function_list)
        children = [
            make_random_tree(
                params_count, max_depth-1, function_prob, params_prob)
            for i in range(function.child_count)
        ]
        return Node(function, children)
    elif random() < params_prob:
        return ParamNode(randint(0, params_count-1))
    else:
        return ConstNode(randint(0, 10))

def mutate(tree, params_count, prob_change=0.1):
    # if the random number is lower than mutation probability,
    # then mutate the current node
    if random() < prob_change:
        return make_random_tree(params_count)

    # otherwise, mutate its children recursively
    result = deepcopy(tree)
    if isinstance(tree, Node):
        result.children = [
            mutate(child, params_count, prob_change)
            for child in tree.children
        ]
    return result

def crossover(tree1, tree2, prob_swap=0.7, top=True):
    # if a randomly selected threshold is reached
    if random() < prob_swap and not top:
        return deepcopy(tree2)

    # otherwise
    result = deepcopy(tree1)
    if isinstance(tree1, Node) and isinstance(tree2, Node):
        # crossover between each branch from first tree and
        # one randomly chosen branch from second tree
        result.children = [
            crossover(child, choice(tree2.children), prob_swap, False)
            for child in tree1.children]
    return result

def evolve(params_count, pop_size, rank_function, max_generations=500,
           mutate_rate=0.1, breeding_rate=0.4, prob_exp=0.7, prob_new=0.05):
    # returns a random number, tending towards lower number.
    # the lower the prob_exp is, more lower numbers you get
    def select_index():
        return int(log(random()) / log(prob_exp))

    # create a random initial population
    population  = [make_random_tree(params_count) for i in range(pop_size)]

    for i in range(max_generations):
        scores = rank_function(population)
        print scores[0][0]
        if scores[0][0] == 0: break

        # the two best always make it
        new_pop = [scores[0][1], scores[1][1]]

        # build the next generation
        while len(new_pop) < pop_size:
            if random() > prob_new:
                new_pop.append(
                    mutate(
                        crossover(
                            scores[select_index()][1],
                            scores[select_index()][1],
                            prob_swap=breeding_rate
                        ),
                        params_count,
                        prob_change=mutate_rate
                    )
                )
            else:
                # add a random node to mix things up
                new_pop.append(make_random_tree(params_count))
        # end of while
        population = new_pop
    # end of for loop
    return scores[0][1]

def get_rank_function(dataset, scoref):
    def rank_function(population):
        scores = [(scoref(individual, dataset), individual)
                    for individual in population]
        scores.sort()
        return scores
    return rank_function