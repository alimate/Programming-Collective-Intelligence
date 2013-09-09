import urllib2
import urllib
import json
import pickle

class API:
    def __init__(self, api_key, root='http://ws.audioscrobbler.com/2.0/'):
        self.api_key = api_key
        self.root = root

    def chart_top_artists(self, method='chart.gettopartists', page=1,
                          limit=50, format=r'json'):
        url = self.root + '?method=%s&api_key=%s&page=%s&limit=%s&format=%s' % (
            method, self.api_key, page, limit, format
        )
        data = urllib2.urlopen(url)
        return json.load(data)

    def artist_top_tags(self, artist, method='artist.gettoptags', autocorrect=1,
                        format=r'json'):
        url = self.root + \
              '?method=%s&artist=%s&api_key=%s&autocorrect=%s&format=%s' % (
            method, urllib.quote_plus(artist), self.api_key,
            autocorrect, format
        )
        data = urllib2.urlopen(url)
        return json.load(data)


api = API(api_key='9f60c79fa285c37cc349cd22ee2dcb99')

def get_top_artists():
    artists = []
    try:
        data = api.chart_top_artists(limit=100)
        for artist in data['artists']['artist']:
            artists.append(artist['name'])
    except:
        print 'Sorry, something went wrong!'
        return
    return artists

def create_dataset():
    # initialize dataset
    dataset = {}
    iteration = 1

    # get top artists
    print 'Start getting top artists'
    for artist in get_top_artists():
        dataset.setdefault(artist, {})

    # loop over all artists and get their top tags
    for artist in dataset.keys():
        try:
            print "Iteration #%d, Retrieving tags for '%s'" % (
                iteration, artist.encode('utf8')
            )
            data = api.artist_top_tags(
                artist=artist.encode('utf8', 'ignore'))
            for tag in data['toptags']['tag']:
                dataset[artist][tag['name']] = float(tag['count'])
        except:
            print 'Error, continue'
        iteration += 1
    print 'Downloading process finished'

    # serializing the dataset object
    with open('lastfm_dataset.data', 'wb') as f:
        pickle.dump(dataset, f)
        print 'Data Saved'

def process_dataset(dataset):
    artists = []
    for artist in dataset.keys():
        if dataset[artist]:
            artists.append(artist)

    tags = set()
    for tag in dataset.values():
        for key in tag.keys():
            tags.add(key)

    tags = list(tags)

    rows = [
        [0.0 for i in range(len(tags))]
        for j in range(len(artists))
    ]

    for i in range(len(artists)):
        artist = artists[i]
        for j in range(len(tags)):
            tag = tags[j]
            if tag in dataset[artist]:
                rows[i][j] = dataset[artist][tag]

    return artists, tags, rows