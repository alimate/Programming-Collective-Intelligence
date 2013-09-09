import feedparser
import re

# takes a filename of URL of a blog and classifies the entries
def read(feed, classifier):
    # get feed entries and loop over them
    f = feedparser.parse(feed)
    for entry in f['entries']:
        print
        print '-----'
        # print the contents of the entry
        print 'Title:          ' + entry['title'].encode('utf-8')
        print 'Publisher:      ' + entry['publisher'].encode('utf-8')
        print
        print entry['summary'].encode('utf-8')

        # combine all the text to create one item for the classifier
        full_text = '%s\n%s\n%s' % (
            entry['title'], entry['publisher'], entry['summary'])

        # print the best guess at the current category
        print 'Guess:   ' + str(classifier.classify(entry))

        # ask the user to specify the correct category
        # and train on that
        cl = raw_input('Enter Category: ')
        classifier.train(entry, cl)

def entry_features(entry, sep=r'\W*', min_chars=2, max_chars=20,
                   shouting_ratio=0.3):
    splitter = re.compile(sep)
    features = {}

    # extract the title words and annotate them as features
    title_words = [word.lower() for word in splitter.split(entry['title'])
    if min_chars < len(word) < max_chars]
    for word in title_words: features['Title:' + word] = 1

    # extract the summary words
    # don't convert words to lowercase
    summary_words = [word for word in splitter.split(entry['summary'])
    if min_chars < len(word) < max_chars]

    # count uppercase words
    upper_count = 0
    for i in range(len(summary_words)):
        word = summary_words[i]
        features[word.lower()] = 1
        if word.isupper(): upper_count += 1

        # get word pairs in summary as features
        if i < len(summary_words) - 1:
            word_pair = ' '.join(summary_words[i:i+2])
            features[word_pair.lower()] = 1

    # keep creator and publisher whole
    features['Publisher:' + entry['publisher']] = 1

    # UPPERCASE is a virtual word flagging too much shouting
    if float(upper_count) / len(summary_words) > shouting_ratio:
        features['UPPERCASE'] = 1
    return features