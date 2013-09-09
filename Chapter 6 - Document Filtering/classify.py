import math
import sqlite3

class Classifier:
    def __init__(self, get_features, filename=None):
        # feature extraction function
        self.get_features = get_features

        # setup the database
        self.setup_db(filename)

    # open the database connection and create tables if necessary
    def setup_db(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.conn.execute(
            'CREATE TABLE IF NOT EXISTS fc(feature, category, count)'
        )
        self.conn.execute(
            'CREATE TABLE IF NOT EXISTS cc(category, count)'
        )

    # increase the count of a feature/category pair
    def incf(self, feature, category):
        count = self.fcount(feature, category)
        if count == 0:
            self.conn.execute(
                "INSERT INTO fc VALUES ('%s', '%s', 1)" %
                (feature, category)
            )
        else:
            self.conn.execute(
                "UPDATE fc SET count=%d WHERE feature='%s' AND category='%s'" %
                (count+1, feature, category)
            )

    # increase the count of a category
    def incc(self, category):
        count = self.cat_count(category)
        if count == 0:
            self.conn.execute(
                "INSERT INTO cc VALUES ('%s', 1)" % category
            )
        else:
            self.conn.execute(
                "UPDATE cc SET count=%d WHERE category='%s'" %
                (count+1, category)
            )

    # the number of times a feature has happened in a category
    def fcount(self, feature, category):
        result = self.conn.execute(
            "SELECT count FROM fc WHERE feature='%s' AND category='%s'" %
            (feature, category)
        ).fetchone()

        if not result: return 0
        return float(result[0])

    # the number of items in a category
    def cat_count(self, category):
        result = self.conn.execute(
            "SELECT count FROM cc WHERE category='%s'" % category
        ).fetchone()

        if not result: return 0
        return float(result[0])

    # the total number of items
    def total_count(self):
        result = self.conn.execute(
            "SELECT SUM(count) FROM cc"
        ).fetchone()

        if not result: return 0
        return float(result[0])

    # the list of all categories
    def categories(self):
        result = self.conn.execute(
            "SELECT DISTINCT category FROM cc"
        )
        return [row[0] for row in result]

    def train(self, item, category):
        # extract all features in given item
        features = self.get_features(item)

        # increment the count for every feature with this category
        for feature in features:
            self.incf(feature, category)

        # increment the count for this category
        self.incc(category)

        # commit the changes
        self.conn.commit()

    def fprob(self, feature, category):
        # if there isn't any items in this category, return zero
        if self.cat_count(category) == 0: return 0

        # otherwise, the probability calculates by dividing
        # the total number of times this feature appeared in
        # this category by the total number of items in this
        # category
        return self.fcount(feature, category) / self.cat_count(category)

    def weighted_probability(self, feature, category, prf, weight=1.0,
                             assumed=0.5):
        # prf stands for probability function
        # calculate the current probability
        basic_prob = prf(feature, category)

        # count the number of times this feature has appeared in
        # all categories
        total = sum([self.fcount(feature, cat)
        for cat in self.categories()])

        # calculate the weighted average
        prob = (weight * assumed + total * basic_prob) / (weight + total)
        return prob

class NaiveBayesian(Classifier):
    def __init__(self, get_features, filename=None):
        Classifier.__init__(self, get_features, filename)
        # thresholds for categories
        self.thresholds = {}

    def doc_prob(self, item, category):
        features = self.get_features(item)
        # multiply the probabilities of all the features together
        prob = 1
        for feature in features:
            prob *= self.weighted_probability(feature, category, self.fprob)
        return prob

    def prob(self, item, category):
        cat_prob = self.cat_count(category) / self.total_count()
        doc_prob = self.doc_prob(item, category)
        return cat_prob * doc_prob

    def set_threshold(self, category, threshold):
        self.thresholds[category] = threshold

    def get_threshold(self, category):
        if category not in self.thresholds: return 1.0
        return self.thresholds[category]

    def classify(self, item, default=None):
        probs = {}
        # find the category with the highest probability
        max = 0.0
        for category in self.categories():
            probs[category] = self.prob(item, category)
            if probs[category] > max:
                max = probs[category]
                best = category

        # make sure the probability exceeds threshold * next best
        for category in probs:
            if category == best: continue
            if probs[category] * self.get_threshold(best) > probs[best]:
                return default
        return best

class Fisher(Classifier):
    def __init__(self, get_features, filename=None):
        Classifier.__init__(self, get_features, filename)
        # lower bounds
        self.minimums = {}

    def set_minimum(self, category, value):
        self.minimums[category] = value

    def get_minimum(self, category):
        if category not in self.minimums: return 0
        return self.minimums[category]

    def cprob(self, feature, category):
        # the probability of this feature in this category
        prob = self.fprob(feature, category)
        if prob == 0: return 0

        # the frequency of this feature in all categories
        freq_sum = sum([self.fprob(feature, cat)
                        for cat in self.categories()])

        # the probability is the frequency in this category
        # divided by the overall frequency

        return prob / freq_sum

    def fisher_prob(self, item, category):
        # initialize probability
        prob = 1

        # extract all features
        features = self.get_features(item)

        # multiply all the probabilities together
        for feature in features:
            prob *= self.weighted_probability(feature, category, self.cprob)

        # take the natural log and multiply by -2
        fisher_score = -2 * math.log(prob)

        # use the inverse chi squared function to get a probability
        return self.chi_squared(fisher_score, 2 * len(features))

    def chi_squared(self, chi, dof):
        # dof stands for degree of freedom
        x = chi / 2.0
        summation = term = math.exp(-x)

        # calculate the summation
        for i in range(1, dof // 2):
            summation += pow(x, i) * term / math.factorial(i)

        # return 1.0 if the calculated probability is greater than one
        return min(summation, 1.0)

    def classify(self, item, default=None):
        best = default
        max = 0.0

        # loop through looking for the best result
        for category in self.categories():
            prob = self.fisher_prob(item, category)
            # make sure it exceeds its minimum and current maximum probability
            if prob > self.get_minimum(category) and prob > max:
                best = category
                max = prob
        return best