import json
from numpy import *

def dump_json(features, words, filename='news.json'):
    # find top words for each feature
    rows, cols = shape(features)
    top_feature_words = []
    for i in range(rows):
        top_words = []
        for j in range(cols):
            top_words.append((features[i, j], words[j]))
        top_words.sort()
        top_words.reverse()
        top_feature_words.append(top_words[:10])

    # convert dataset to required json format
    children = []
    for feature in top_feature_words:
        if feature:
            feature_dict = {'name':'', 'children':[]}
            for words in feature:
                feature_dict['children'].append(
                    {'name':words[1], 'size':round(500 * words[0])})
            children.append(feature_dict)
    result = {'name':'', 'children':children}
    with open(filename, 'w') as f:
        json.dump(result, f)