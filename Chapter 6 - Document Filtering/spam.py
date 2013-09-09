import re

def get_words(doc, sep=r'\W*', min_chars=2, max_chars=20):
    splitter = re.compile(sep)
    # Split the words by non-alphanumeric characters
    words = [word.lower() for word in splitter.split(doc)
             if min_chars < len(word) < max_chars
    ]

    # Return the unique set of words only
    return dict([(word, 1) for word in words])

def sample_train(cl):
    cl.train('Nobody owns the water', 'good')
    cl.train('the quick rabbit jumps fences', 'good')
    cl.train('buy pharmaceuticals now', 'bad')
    cl.train('make quick money at the online casino', 'bad')
    cl.train('the quick brown fox jumps', 'good')