import re
import feedparser
from numpy import *

feed_list = [
    'http://feeds.reuters.com/reuters/topNews',
    'http://feeds.reuters.com/Reuters/domesticNews',
    'http://feeds.reuters.com/Reuters/worldNews',
    'http://hosted2.ap.org/atom/APDEFAULT/3d281c11a96b4ad082fe88aa0db04305',
    'http://hosted2.ap.org/atom/APDEFAULT/386c25518f464186bf7a2ac026580ce7',
    'http://hosted2.ap.org/atom/APDEFAULT/cae69a7523db45408eeb2b3a98c0c9c5',
    'http://hosted2.ap.org/atom/APDEFAULT/89ae8247abe8493fae24405546e9a1aa',
    'http://www.nytimes.com/services/xml/rss/nyt/HomePage.xml',
    'http://www.nytimes.com/services/xml/rss/nyt/World.xml',
    'http://news.google.com/?output=rss',
    'http://www.salon.com/feed/',
    'http://feeds.foxnews.com/foxnews/most-popular?format=xml',
    'http://feeds.foxnews.com/foxnews/national?format=xml',
    'http://feeds.foxnews.com/foxnews/world?format=xml',
    'http://rss.cnn.com/rss/edition.rss',
    'http://rss.cnn.com/rss/edition_world.rss',
    'http://rss.cnn.com/rss/edition_us.rss']

def strip_tags(txt):
    regex = re.compile(r'<[^>]+?>')
    return regex.sub(' ', txt).strip()

def separate_words(txt, sep=r'\W*'):
    splitter = re.compile(sep)
    words = splitter.split(txt)
    return [word.lower() for word in words if len(word) > 3]

def get_article_words():
    # initialize some variables
    all_words = {}
    article_words = []
    article_titles = []
    entry_counter = 0

    # loop over all feeds
    for feed in feed_list:
        article = feedparser.parse(feed)

        # loop over every article
        for entry in article.entries:
            # ignore identical articles
            if entry.title in article_titles: continue

            # extract the words
            txt = entry.title.encode('utf8') + ' '
            txt += strip_tags(entry.description.encode('utf8'))
            words = separate_words(txt)
            article_words.append({})
            article_titles.append(entry.title)

            # increase the counts of each word
            for word in words:
                all_words.setdefault(word, 0)
                all_words[word] += 1
                article_words[entry_counter].setdefault(word, 0)
                article_words[entry_counter][word] += 1
            entry_counter += 1
    return all_words, article_words, article_titles

def make_matrix(all_words, article_words):
    word_vector = []

    # only take words that are common but too common
    for word, count in all_words.items():
        if 3 < count < 0.6 * len(article_words):
            word_vector.append(word)

    # create the word matrix
    matrix = [
        [
            # if current word appears in current article,
            # use its frequency, otherwise use 0
            (word in article and article[word] or 0)
            for word in word_vector
        ]
        for article in article_words]
    return matrix, word_vector

def show_features(w, h, titles, words, out='features.txt'):
    out_file = open(out, 'w')
    rows, cols = shape(h)
    top_patterns = [[] for i in range(len(titles))]
    pattern_names = []

    # loop over all the features
    for i in range(rows):
        # create a list of words and their weights
        top_words = []
        for j in range(cols):
            top_words.append((h[i, j], words[j]))

        # reverse sort the word list
        top_words.sort()
        top_words.reverse()

        # print the first five elements
        top_five_words = [word[1] for word in top_words[:5]]
        out_file.write(str(top_five_words) + '\n')
        pattern_names.append(top_five_words)

        # create a list of articles for this feature
        top_articles = []
        for j in range(len(titles)):
            # add the article with its weight
            top_articles.append((w[j, i], titles[j]))
            top_patterns[j].append((w[j, i], i, titles[j]))

        # reverse sort the list
        top_articles.sort()
        top_articles.reverse()

        # show the top 3 articles
        for article in top_articles[:3]:
            out_file.write(str(article) + '\n')
        out_file.write('\n')

    out_file.close()
    # return the pattern names for later use
    return top_patterns, pattern_names

def show_by_article(titles, top_patterns, pattern_names, out='articles.txt'):
    out_file = open(out, 'w')

    # loop over all the articles
    for j in range(len(titles)):
        out_file.write(titles[j].encode('utf8') + '\n')

        # get the top features for this article and
        # reverse sort them
        top_patterns[j].sort()
        top_patterns[j].reverse()

        # print the top three patterns
        for i in range(3):
            out_file.write(
                str(top_patterns[j][i][0]) + ' ' +
                str(pattern_names[top_patterns[j][i][1]]) + '\n'
            )
        out_file.write('\n')
    out_file.close()