import math

class Classifier:
    def __init__(self, get_features, filename=None):
        # counts of feature/category combinations
        self.fc = {}

        # counts of documents in each category
        self.cc = {}

        # feature extraction function
        self.get_features = get_features

    # increase the count of a feature/category pair
    def incf(self, feature, category):
        self.fc.setdefault(feature, {})
        self.fc[feature].setdefault(category, 0)
        self.fc[feature][category] += 1

    # increase the count of a category
    def incc(self, category):
        self.cc.setdefault(category, 0)
        self.cc[category] += 1

    # the number of times a feature has happened in a category
    def fcount(self, feature, category):
        if feature in self.fc and category in self.fc[feature]:
            return float(self.fc[feature][category])
        return 0.0

    # the number of items in a category
    def cat_count(self, category):
        if category in self.cc:
            return float(self.cc[category])
        return 0.0

    # the total number of items
    def total_count(self):
        return sum(self.cc.values())

    # the list of all categories
    def categories(self):
        return self.cc.keys()

    def train(self, item, category):
        # extract all features in given item
        features = self.get_features(item)

        # increment the count for every feature with this category
        for feature in features:
            self.incf(feature, category)

        # increment the count for this category
        self.incc(category)

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