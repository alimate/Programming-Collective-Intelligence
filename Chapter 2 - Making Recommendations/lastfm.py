import urllib2
import urllib
import json

class API:
    def __init__(self, api_key, root='http://ws.audioscrobbler.com/2.0/'):
        self.api_key = api_key
        self.root = root

    def user_get_friends(self, user, method='user.getfriends',
                         page=1, limit=50, format=r'json'):
        url = self.root + \
              '?method=%s&user=%s&api_key=%s&page=%s&limit=%s&format=%s' % (
            method, urllib.quote_plus(user), self.api_key,
            page, limit, format
        )
        data = urllib2.urlopen(url)
        return json.load(data)

api_key = '9f60c79fa285c37cc349cd22ee2dcb99'
api = API(api_key=api_key)

def extract_names(json_data):
    names = []
    if type(json_data['friends']['user']) == type({}):
        data = [json_data['friends']['user']]
    else:
        data = json_data['friends']['user']
    for user in data:
        names.append(user['name'])
    return names

def get_friends(seed='freakymoji', depth=2):
    # initialize dataset
    users = {}

    # list of users for next search iteration,
    # it's a set not a dictionary
    queue = {seed}

    # breadth first search
    for iteration in range(depth):
        print 'Iteration %s, %s items in total' % (iteration + 1, len(queue))
        next_items = set()
        for user in queue:
            users.setdefault(user, {})
            print 'Start retrieving "%s"' % user
            try:
                data = api.user_get_friends(user, limit=1500)
                for friend in extract_names(data):
                    users[user][friend] = 1.0
                    if friend not in queue and friend not in users.keys():
                        next_items.add(friend)
            except:
                print 'Error, next user'
                continue
        queue = next_items.copy()

    # populate the list of all users
    all_users = set()
    for user in users.values():
        for friend in user.keys():
            all_users.add(friend)

    # set 1.0 for friendship, 0 otherwise
    for item in all_users:
        for user in users:
            if item not in users[user]:
                users[user][item] = 0.0
    return users