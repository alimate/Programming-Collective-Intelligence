import feedparser
import re

# Returns title and dictionary of word counts for an RSS feed
def get_word_counts(url):
    # parse the feed
    feed = feedparser.parse(url)

    # word counts
    word_counts = {}

    # Loop over all the entries
    for entry in feed.entries:
        if 'summary' in entry: summary = entry.summary
        else: summary = entry.description

        # Extract a list of words
        words = get_words(entry.title + ' ' + summary)
        for word in words:
            word_counts.setdefault(word, 0)
            word_counts[word] += 1
    return feed.feed.title, word_counts

def get_words(txt):
    # Remove all the HTML tags
    txt = re.compile(r'<[^>]+>').sub('', txt)

    # Split words by all non-alpha characters
    words = re.compile(r'[^A-Z^a-z]+').split(txt)

    # convert to lowercase
    return [word.lower() for word in words if word != '']

def do_requests(input='data/feedlist.txt'):
    # number of blogs each word appeared
    ap_count = {}

    # number of appearances of each word in each blog
    word_counts = {}

    # loop over all feeds in feedlist.txt
    for feed_url in open(input):
        print 'start fetching %s' % feed_url
        try:
            title, wc = get_word_counts(feed_url)
        except:
            print 'fetching failed!'
            continue
        word_counts[title] = wc
        for word, count in wc.items():
            ap_count.setdefault(word, 0)
            if count > 1:
                ap_count[word] += 1
    return word_counts, ap_count

# select the list of words that will actually be used
def select_words(word_counts, ap_count, minimum=0.1, maximum=0.5):
    blogs = len(word_counts)
    word_list = []
    for word, blog_count in ap_count.items():
        fraction = float(blog_count) / blogs
        if minimum < fraction < maximum:
            word_list.append(word)
    return word_list

# save the output file
def output_file(word_counts, word_list, output='blogdata.txt'):
    out = open(output, 'w')
    # populate the first line which is a header
    out.write('Blog')
    for word in word_list: out.write('\t%s' % word)
    out.write('\n')
    # populate data
    for blog, wc in word_counts.items():
        out.write(blog.encode('utf8'))
        for word in word_list:
            if word in wc: out.write('\t%s' % wc[word])
            else: out.write('\t0')
        out.write('\n')

def read_file(file_name='blogdata.txt'):
    lines = [line for line in open(file_name)]

    # First line is the column titles
    col_names = lines[0].strip().split('\t')[1:]
    row_names = []
    data = []
    for line in lines[1:]:
        blog = line.strip().split('\t')
        # first column in each row is the rowname
        row_names.append(blog[0])
        # the data for this row is the remainder of the row
        data.append([float(x) for x in blog[1:]])
    return row_names, col_names, data