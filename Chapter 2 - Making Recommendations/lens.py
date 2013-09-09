# load data from files
def load_movie_lens(path='movieLens/'):
    # get movie titles
    movies = {}
    for line in open(path + 'u.item'):
        (id, title) = line.split('|')[:2]
        movies[id] = title

    # load data
    prefs = {}
    for line in open(path + 'u.data'):
        (user, movie_id, rating, timestamp) = line.split('\t')
        prefs.setdefault(user, {})
        prefs[user][movies[movie_id]] = float(rating)
    return prefs