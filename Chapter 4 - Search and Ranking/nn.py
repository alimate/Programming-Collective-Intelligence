import sqlite3
from math import tanh

def dtanh(y):
    return 1.0 - y * y

class NeuralNetwork:
    def __init__(self, dbname):
        self.conn = sqlite3.connect(dbname)

    def __del__(self):
        self.conn.close()

    def create_tables(self):
        self.conn.execute('CREATE TABLE hiddennode(create_key)')
        self.conn.execute('CREATE TABLE wordhidden(fromid,toid,strength)')
        self.conn.execute('CREATE TABLE hiddenurl(fromid,toid,strength)')
        self.conn.commit()

    def get_strength(self, fromid, toid, layer):
        # determine which table should be used
        if layer == 0: table = 'wordhidden'
        else: table = 'hiddenurl'

        # retrieve the link's strength
        result = self.conn.execute(
            "SELECT strength FROM %s WHERE fromid=%d AND toid=%d" % (
                table, fromid, toid
            )
        ).fetchone()

        # if the link doesn't exist
        # return default values
        if not result:
            if layer == 0: return -0.2
            elif layer == 1 : return 0

        # otherwise, return the retrieved value
        return result[0]

    def set_strength(self, fromid, toid, layer, strength):
        # determine which table should be used
        if layer == 0: table = 'wordhidden'
        else: table = 'hiddenurl'

        # check for existence of link
        result = self.conn.execute(
            'SELECT rowid FROM %s WHERE fromid=%d AND toid=%d' % (
                table, fromid, toid
            )
        ).fetchone()

        # if so, update the link's strength
        # with the given strength
        if result:
            rowid = result[0]
            self.conn.execute(
                'UPDATE %s SET strength=%f WHERE rowid=%d' % (
                    table, strength, rowid)
            )

        # otherwise, create a link with
        # the given strength
        else:
            self.conn.execute(
                'INSERT INTO %s (fromid,toid,strength) VALUES (%d,%d,%f)' % (
                    table, fromid, toid, strength
                )
            )

    def generate_hidden_node(self, wordids, urls):
        if len(wordids) > 3: return None

        # check if we already created
        # a node for this set of words
        create_key = '_'.join(sorted([str(wordid) for wordid in wordids]))
        result = self.conn.execute(
            "SELECT rowid FROM hiddennode WHERE create_key='%s'" % create_key
        ).fetchone()

        # if not, create it
        if not result:
            cursor = self.conn.execute(
                "INSERT INTO hiddennode (create_key) VALUES ('%s')" %
                create_key
            )
            hidden_id = cursor.lastrowid

            # put in some default weights
            for wordid in wordids:
                self.set_strength(wordid, hidden_id, 0, 1.0 / len(wordids))
            for urlid in urls:
                self.set_strength(hidden_id, urlid, 1, 0.1)
            self.conn.commit()

    def get_all_hidden_ids(self, wordids, urlids):
        hidden_nodes = {}

        # find all hidden nodes connected
        # to each given word
        for wordid in wordids:
            cursor = self.conn.execute(
                "SELECT toid FROM wordhidden WHERE fromid=%d" % wordid
            )
            for row in cursor: hidden_nodes[row[0]] = 1

        # find all hidden nodes connected
        # to each given url
        for urlid in urlids:
            cursor = self.conn.execute(
                "SELECT fromid FROM hiddenurl WHERE toid=%d" % urlid
            )
            for row in cursor: hidden_nodes[row[0]] = 1
        return hidden_nodes.keys()

    def setup_network(self, wordids, urlids):
        # value lists
        self.wordids = wordids
        self.hiddenids = self.get_all_hidden_ids(wordids, urlids)
        self.urlids = urlids

        # initialize activation function values for all nodes
        self.ai = [1.0] * len(self.wordids)
        self.ah = [1.0] * len(self.hiddenids)
        self.ao = [1.0] * len(self.urlids)

        # create weights matrix
        self.wi = [
            [self.get_strength(wordid, hiddenid, 0)
            for hiddenid in self.hiddenids]
            for wordid in self.wordids]
        self.wo = [
            [self.get_strength(hiddenid, urlid, 1)
            for urlid in self.urlids]
            for hiddenid in self.hiddenids
        ]

    def feed_forward(self):
        # the only inputs are the query words
        for i in range(len(self.wordids)):
            self.ai[i] = 1.0

        # hidden activations
        for j in range(len(self.hiddenids)):
            sum = 0.0
            for i in range(len(self.wordids)):
                sum += self.ai[i] * self.wi[i][j]
            self.ah[j] = tanh(sum)

        # output activations
        for k in range(len(self.urlids)):
            sum = 0.0
            for j in range(len(self.hiddenids)):
                sum += self.ah[j] * self.wo[j][k]
            self.ao[k] = tanh(sum)

        # return a copy of output activations
        return self.ao[:]

    def get_result(self, wordids, urlids):
        self.setup_network(wordids, urlids)
        return self.feed_forward()

    def back_propagate(self, targets, rate=0.5):
        # i for output layer, j for hidden layer
        # k for input layer
        # calculate errors for output layer
        output_deltas = [0.0] * len(self.urlids)
        for i in range(len(self.urlids)):
            error = targets[i] - self.ao[i]
            output_deltas[i] = dtanh(self.ao[i]) * error

        # calculate errors for hidden layer
        hidden_deltas = [0.0] * len(self.hiddenids)
        for j in range(len(self.hiddenids)):
            error = 0.0
            for i in range(len(self.urlids)):
                error += output_deltas[i] * self.wo[j][i]
            hidden_deltas[j] = dtanh(self.ah[j]) * error

        # update the output weights
        for j in range(len(self.hiddenids)):
            for i in range(len(self.urlids)):
                self.wo[j][i] += rate * output_deltas[i] * self.ah[j]

        # update the input weights
        for k in range(len(self.wordids)):
            for j in range(len(self.hiddenids)):
                self.wi[k][j] += rate * hidden_deltas[j] * self.ai[k]

    def train_query(self, wordids, urlids, selected_url):
        # generate a hidden node if necessary
        self.generate_hidden_node(wordids, urlids)

        self.setup_network(wordids, urlids)
        self.feed_forward()

        targets = [0.0] * len(urlids)
        targets[urlids.index(selected_url)] = 1.0
        self.back_propagate(targets)
        self.update_database()

    def update_database(self):
        # again, i,j and k used for output layer,
        # hidden layer and input layer, respectively
        for k in range(len(self.wordids)):
            for j in range(len(self.hiddenids)):
                self.set_strength(self.wordids[k], self.hiddenids[j],
                    0, self.wi[k][j])

        for j in range(len(self.hiddenids)):
            for i in range(len(self.urlids)):
                self.set_strength(self.hiddenids[j], self.urlids[i],
                1, self.wo[j][i])

        # commit the changes
        self.conn.commit()