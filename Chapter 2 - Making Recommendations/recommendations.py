from math import sqrt

# Returns a distance-based similarity score for person1 and person2
def sim_distance(prefs, person1, person2):
    # Get the list of shared items
    si = {}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item] = 1

    # if they have no ratings in common, return 0
    if len(si) == 0:
        return 0

    # Add up the squares of all the differences
    sum_of_squares = sum([
        pow(prefs[person1][item]-prefs[person2][item], 2)
        for item in prefs[person1] if item in prefs[person2]
    ])

    # return the similarity score
    return 1.0 / (1 + sqrt(sum_of_squares))

# Returns the Pearson correlation coefficient for person1 and person2
def sim_pearson(prefs, person1, person2):
    # Get the list of shared_items
    si = {}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item] = 1

    # Find the number of elements
    n = len(si)

    # if they are no ratings in common, return 0
    if n == 0: return 0

    # Add up all the preferences
    sum1 = sum([prefs[person1][item] for item in si])
    sum2 = sum([prefs[person2][item] for item in si])

    # Sum up the squares
    sum_sq1 = sum([pow(prefs[person1][item], 2) for item in si])
    sum_sq2 = sum([pow(prefs[person2][item], 2) for item in si])

    # Sum up the products
    p_sum = sum([prefs[person1][item] * prefs[person2][item]
    for item in si])

    # Calculate Pearson score
    num = p_sum - (sum1 * sum2) / n
    den = sqrt((sum_sq1 - pow(sum1, 2) / n) * (sum_sq2 - pow(sum2, 2) / n))
    if den == 0: return 0

    coeff = num / den
    return coeff

# Returns the best matches for person from the prefs dictionary.
# Number of results and similarity function are optional params.
def top_matches(prefs, person, n=5, similarity=sim_pearson):
    scores = [(similarity(prefs, person, other), other)
        for other in prefs if other != person]

    # Sort the list so the highest scores appear at the top
    scores.sort()
    scores.reverse()
    return scores[:n]

# Gets recommendations for a person by using a weighted average
# of every other user's rankings
def get_recommendations(prefs, person, similarity=sim_pearson):
    totals = {}
    similarity_sums = {}
    for other in prefs:
        # don't compare me to myself
        if other == person: continue
        sim = similarity(prefs, person, other)

        # ignore scores of zero or lower
        if sim <= 0: continue
        for item in prefs[other]:
            # only score items I haven't seen yet
            if item not in prefs[person] or prefs[person][item] == 0:
                # Similarity * Score
                totals.setdefault(item, 0)
                totals[item] += sim * prefs[other][item]
                # Sum of similarities
                similarity_sums.setdefault(item, 0)
                similarity_sums[item] += sim
        # end of inner for loop
    # end of outer for loop
    # Create the normalized list
    rankings = [(total / similarity_sums[item], item)
                for item, total in totals.items()]

    # Return the sorted list
    rankings.sort()
    rankings.reverse()
    return rankings

def transform_prefs(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})
            # Flip item and person
            result[item][person] = prefs[person][item]
    return result

# Create a dictionary of items showing which other items they
# are most similar to
def calculate_similar_items(prefs, n=10):
    result = {}
    # Invert the preference matrix to be item-centric
    item_prefs = transform_prefs(prefs)
    for item in item_prefs:
        # Find the most similar items to this one
        scores = top_matches(item_prefs, item, n=n, similarity=sim_distance)
        result[item] = scores
    return result

def get_recommended_items(prefs, item_match, person):
    user_ratings = prefs[person]
    scores = {}
    total_sim = {}

    # Loop over items rated by this person
    for (item, rating) in user_ratings.items():
        # Loop over items similar to this one
        for (similarity, item2) in item_match[item]:
            # Ignore if this person has already rated this item
            if item2 in user_ratings: continue

            # Weighted sum of rating times similarity
            scores.setdefault(item2, 0)
            scores[item2] += similarity * rating

            # Sum of all the similarities
            total_sim.setdefault(item2, 0)
            total_sim[item2] += similarity
        # end of inner for loop
    # end of outer for loop
    # Divide each total score by total weighting to get an average
    rankings = [(score / total_sim[item], item)
                for item, score in scores.items()]

    # Return the rankings from highest to lowest
    rankings.sort()
    rankings.reverse()
    return rankings