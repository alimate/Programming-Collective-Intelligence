import math
import random

# The dorms, each of which has two available spaces
dorms = ['Zeus', 'Athena', 'Hercules', 'Bacchus', 'Pluto']

# People, along with their first and second choices
prefs = [
       ('Toby', ('Bacchus', 'Hercules')),
       ('Steve', ('Zeus', 'Pluto')),
       ('Andrea', ('Athena', 'Zeus')),
       ('Sarah', ('Zeus', 'Pluto')),
       ('Dave', ('Athena', 'Bacchus')),
       ('Jeff', ('Hercules', 'Pluto')),
       ('Fred', ('Pluto', 'Athena')),
       ('Suzie', ('Bacchus', 'Hercules')),
       ('Laura', ('Bacchus', 'Hercules')),
       ('Neil', ('Hercules', 'Athena'))
]

# [(0,9),(0,8),(0,7),(0,6),...,(0,0)]
domain = [
    (0, 2 * len(dorms) - i - 1)
    for i in range(2 * len(dorms))
]

def print_solution(sol):
    slots = []
    # create two slots for each dorm
    for i in range(len(dorms)): slots += [i, i]

    # loop over each students assignment
    for i in range(len(sol)):
        value = int(sol[i])

        # choose the slot from the remaining ones
        dorm = dorms[slots[value]]

        # show the student and assigned dorm
        print prefs[i][0] + ' goes to ' + dorm

        # remove this slot
        del slots[value]

def dorm_cost(sol):
    cost = 0

    # create list of slots
    slots = []
    for i in range(len(dorms)): slots += [i, i]

    # loop over each student
    for i in range(len(sol)):
        value = int(sol[i])
        dorm = dorms[slots[value]]

        # get the student's top choices
        pref = prefs[i][1]

        # first choice costs 0, second one costs 1
        if pref[0] == dorm: cost += 0
        elif pref[1] == dorm: cost += 1
        # not on the list costs 3
        else: cost += 3

        # remove selected slot
        del slots[value]
    return cost