import random
import math

def random_optimize(domain, costf):
    # initialize current best cost
    # with a very large value
    best_cost = 999999999
    best_result = None

    # generate 1000 random guess and find the best
    for i in range(1000):
        # create a random guess
        guess = [random.randint(domain[j][0], domain[j][1])
        for j in range(len(domain))
        ]

        # get the cost
        cost = costf(guess)

        # compare it to the best one so far
        if cost < best_cost:
            best_cost = cost
            best_result = guess

    # return the best result along with its cost
    return best_result, best_cost

def hill_climb(domain, costf):
    # create a random solution
    sol = [random.randint(domain[i][0], domain[i][1])
        for i in range(len(domain))
    ]

    # main loop
    while True:
        # create a list of neighbors
        neighbors = []
        for i in range(len(domain)):
            # one away in each direction
            # increase by one if current
            # value is less than maximum
            if sol[i] < domain[i][1]:
                neighbors.append(
                    sol[:i] + [sol[i] + 1] + sol[i+1:]
                )
            # decrease by one if current
            # value is greater than minimum
            if sol[i] > domain[i][0]:
                neighbors.append(
                    sol[:i] + [sol[i] - 1] + sol[i+1:]
                )
        # end of neighbors loop

        # See what the best solution
        # amongst the neighbors is
        current = costf(sol)
        best = current
        for j in range(len(neighbors)):
            cost = costf(neighbors[j])
            if cost < best:
                best = cost
                sol = neighbors[j]
            # If there's no improvement,
        # then we've reached the top
        if best == current:
            break
    # end of main loop
    return sol

def annealing_optimize(domain, costf, T=10000.0, cool=0.95, step=1):
    # initialize the values randomly
    current = [float(random.randint(domain[i][0], domain[i][1]))
               for i in range(len(domain))
    ]

    while T > 0.1:
        # choose one of the indices
        i = random.randint(0, len(domain) - 1)

        # choose a direction to change it
        direction = random.randint(-step, step)

        # create a new list with one of the values changed
        next = current[:]
        next[i] += direction
        if next[i] < domain[i][0]: next[i] = domain[i][0]
        elif next[i] > domain[i][1]: next[i] = domain[i][1]

        # calculate the current cost and the new cost
        current_cost = costf(current)
        next_cost = costf(next)
        prob = pow(math.e, (-next_cost - current_cost) / T)

        # is it better, or does it make the probability
        # cutoff?
        if next_cost < current_cost or random.random() < prob:
            current = next

        # decrease the temperature
        T = T * cool
    return current

def genetic_optimize(domain, costf, pop_size=50, step=1, mut_prob=0.2,
                     elite=0.2, desired_cost=None, max_iter=100):
    # mutation operation
    def mutate(vec):
        i = random.randint(0, len(domain) - 1)
        if random.random() < 0.5 and vec[i] > domain[i][0]:
            return vec[:i] + [vec[i] - step] + vec[i+1:]
        elif vec[i] < domain[i][1]:
            return vec[:i] + [vec[i] + step] + vec[i+1:]

    # crossover operation
    def crossover(vec1, vec2):
        i = random.randint(1, len(domain) - 2)
        return vec1[:i] + vec2[i:]

    # build the initial population
    pop = []
    for i in range(pop_size):
        vec = [random.randint(domain[j][0], domain[j][1])
            for j in range(len(domain))
        ]
        pop.append(vec)

    # How many survivors from each generation?
    top_elite = int(elite * pop_size)

    # main loop
    for i in range(max_iter):
        scores = [(costf(v), v) for v in pop if v]
        scores.sort()
        ranked = [v for (s, v) in scores]

        # start with pure survivors
        pop = ranked[:top_elite]

        # Add mutated and bred forms of the winners
        while len(pop) < pop_size:
            if random.random() < mut_prob:
                # mutation
                c = random.randint(0, top_elite)
                pop.append(mutate(ranked[c]))
            else:
                # crossover
                c1 = random.randint(0, top_elite)
                c2 = random.randint(0, top_elite)
                pop.append(crossover(ranked[c1], ranked[c2]))
        # end of while
        print scores[0][0]
        if desired_cost and scores[0][0] <= desired_cost:
            break
    # end of main loop
    return scores[0][1]