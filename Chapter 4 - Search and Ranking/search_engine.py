import urllib2
import urlparse
import sqlite3
import re
from BeautifulSoup import BeautifulSoup
import nn

ignore_words = set(['the', 'of', 'to', 'and', 'a', 'in', 'is', 'it'])
mynet = nn.NeuralNetwork('searchindex.db')

class Crawler:
    # Initialize the crawler with the name of database
    def __init__(self, dbname):
        self.conn = sqlite3.connect(dbname)

    # Destructor!
    def __del__(self):
        self.conn.close()

    def db_commit(self):
        self.conn.commit()

    # Auxiliary function for getting an entry id and adding
    # it if it's not present
    # sounds familiar for django lovers!
    def get_or_create(self, table, field, value, create_new=True):
        cursor = self.conn.execute(
            "SELECT rowid FROM %s WHERE %s='%s'" % (table, field, value)
        )
        result = cursor.fetchone()
        if not result:
            cursor = self.conn.execute(
                "INSERT INTO %s (%s) VALUES ('%s')" % (table, field, value)
            )
            return cursor.lastrowid
        else:
            return result[0]

    # Index an individual page
    def add_to_index(self, url, soup):
        if self.is_indexed(url): return
        print 'Indexing %s' % url

        # get the individual words
        text = self.get_text_only(soup)
        words = self.separate_words(text)

        # get the url id
        urlid = self.get_or_create('urllist', 'url', url)

        # link each word to this url
        for i in range(len(words)):
            word = words[i]
            if word in ignore_words: continue
            wordid = self.get_or_create('wordlist', 'word', word)
            self.conn.execute(
                'INSERT INTO wordlocation(urlid,wordid,location) \
                 VALUES(%d,%d,%d)' % (urlid, wordid, i)
            )

    # Extract the text from an HTML page (no tags)
    def get_text_only(self, soup):
        # If a tag doesn't contain any other tags,
        # 'string' attribute returns the text
        val = soup.string

        # otherwise, returns None
        if not val:
            # in such situations, we can use 'contents' attribute
            # tag's children are available in a list
            content = soup.contents
            result_text = ''
            for tag in content:
                subtext = self.get_text_only(tag)
                result_text += subtext + '\n'
            return result_text
        else:
            return val.strip()

    # Separate the words by any non-alphanumeric character
    def separate_words(self, text, sep=r'\W*'):
        words = re.compile(sep).split(text)
        return [word.lower() for word in words if word != '']

    # Return true if this url is already indexed
    def is_indexed(self, url):
        urlid = self.conn.execute(
            "SELECT rowid FROM urllist WHERE url='%s'" % url
        ).fetchone()
        if urlid:
            # Check if it has actually been crawled
            is_crawled = self.conn.execute(
                "SELECT * FROM wordlocation WHERE urlid=%d" % urlid[0]
            ).fetchone()
            if is_crawled: return True
        return False

    # Add a link between two pages
    def add_link_ref(self, url_from, url_to, link_text):
        # get url ids
        toid = self.get_or_create('urllist', 'url', url_to)
        fromid = self.get_or_create('urllist', 'url', url_from)

        # add this reference to link table
        ref = self.conn.execute(
            "SELECT rowid FROM link WHERE fromid=%d AND toid=%d"
            % (fromid, toid)
        ).fetchone()
        if ref:
            linkid = ref[0]
        else:
            ref = self.conn.execute(
                "INSERT INTO link (fromid,toid) VALUES (%d,%d)" % (fromid, toid)
            )
            linkid = ref.lastrowid

        # associate each word with this link
        words = self.separate_words(link_text)
        for word in words:
            if word in ignore_words: continue
            wordid = self.get_or_create('wordlist', 'word', word)
            ref = self.conn.execute(
                "SELECT rowid FROM linkwords WHERE linkid=%d AND wordid=%d"
                % (linkid, wordid)
            ).fetchone()
            if not ref:
                self.conn.execute(
                    "INSERT INTO linkwords (linkid, wordid) VALUES (%d,%d)"
                    % (linkid, wordid)
                )


    # Starting with a list of pages, do a breadth
    # first search to the given depth, indexing pages
    # as we go
    def crawl(self, pages, depth=2):
        for iteration in range(depth):
            new_pages = set()
            for page in pages:
                try:
                    content = urllib2.urlopen(page)
                except:
                    print 'Could not open %s' % page
                    continue
                soup = BeautifulSoup(content.read())
                self.add_to_index(page, soup)

                # follow all links
                links = soup('a')
                for link in links:
                    # if the link has href attribute
                    if 'href' in dict(link.attrs):
                        # href may be a relative address, if so
                        # we'll append that to the base address
                        url = urlparse.urljoin(page, link['href'])
                        if url.find("'") != -1: continue
                        # remove location portion
                        url = url.split('#')[0]
                        if url[:4] == 'http' and not self.is_indexed(url):
                            new_pages.add(url)
                        link_text = self.get_text_only(link)
                        self.add_link_ref(page, url, link_text)
                # end of most inner for loop
                self.db_commit()
            # end of second most inner for loop
            pages = new_pages

    # Create the database tables
    def create_index_tables(self):
        # creating tables
        self.conn.execute('CREATE TABLE urllist(url)')
        self.conn.execute('CREATE TABLE wordlist(word)')
        self.conn.execute('CREATE TABLE wordlocation(urlid, wordid, location)')
        self.conn.execute('CREATE TABLE link(fromid integer, toid integer)')
        self.conn.execute('CREATE TABLE linkwords(wordid, linkid)')
        # creating indices to speed up searching
        self.conn.execute('CREATE INDEX wordidx on wordlist(word)')
        self.conn.execute('CREATE INDEX urlidx on urllist(url)')
        self.conn.execute('CREATE INDEX wordurlidx on wordlocation(wordid)')
        self.conn.execute('CREATE INDEX urltoidx on link(toid)')
        self.conn.execute('CREATE INDEX urlfromidx on link(fromid)')
        # commit changes
        self.db_commit()

    def calculate_pagerank(self, iterations=20, minimum=0.15, damping=0.85):
        # clear out the current PageRank tables
        self.conn.execute('DROP TABLE IF EXISTS pagerank')
        self.conn.execute('CREATE TABLE pagerank(urlid PRIMARY KEY, score)')

        # initialize every url with a PageRank of 1.0
        self.conn.execute('INSERT INTO pagerank SELECT rowid, 1.0 FROM urllist')
        self.db_commit()

        for iteration in range(iterations):
            print 'Iteration %d' % iteration
            for (urlid,) in self.conn.execute('SELECT rowid FROM urllist'):
                pr = minimum

                # Loop through all the pages that link to this one
                for (linker,) in self.conn.execute(
                    'SELECT DISTINCT fromid FROM link WHERE toid=%d' % urlid
                ):
                    # Get the PageRank of the linker
                    linker_pr = self.conn.execute(
                        'SELECT score FROM pagerank WHERE urlid=%d' % linker
                    ).fetchone()[0]

                    # Get the total number of links from the linker
                    linker_links = self.conn.execute(
                        'SELECT count(*) FROM link WHERE fromid=%d' % linker
                    ).fetchone()[0]

                    pr += damping * (linker_pr / linker_links)
                # end of linkers for loop
                self.conn.execute(
                    'UPDATE pagerank SET score=%f WHERE urlid=%d' % (pr, urlid)
                )
            # end of inner for loop
            self.db_commit()

class Searcher:
    def __init__(self, dbname):
        self.conn = sqlite3.connect(dbname)

    def __del__(self):
        self.conn.close()

    def get_match_rows(self, q):
        # Strings to build the query
        field_list = 'w0.urlid'
        table_list = ''
        clause_list = ''
        wordids = []

        # Split the words by spaces
        words = q.split(' ')
        table_number = 0

        for word in words:
            # Get the word ID
            result = self.conn.execute(
                "SELECT rowid FROM wordlist WHERE word='%s'" % word
            ).fetchone()

            if result:
                wordid = result[0]
                wordids.append(wordid)

                if table_number > 0:
                    table_list += ','
                    clause_list += ' AND '
                    clause_list += 'w%d.urlid=w%d.urlid AND ' % (
                        table_number - 1, table_number)
                field_list += ',w%d.location' % table_number
                table_list += 'wordlocation w%d' % table_number
                clause_list += 'w%d.wordid=%d' % (table_number, wordid)
                table_number += 1
        # end of for loop
        # Create the query from the separate parts
        full_query = 'SELECT %s FROM %s WHERE %s' % (
            field_list, table_list, clause_list
        )
        cursor = self.conn.execute(full_query)
        rows = [row for row in cursor]

        return rows, wordids

    def get_scored_list(self, rows, wordids):
        total_scores = dict([(row[0], 0) for row in rows])

        # This is where you'll later put the scoring functions
        weights = [(1.0, self.pagerank_score(rows)),
                   (1.0, self.location_score(rows)),
                   (1.0, self.frequency_score(rows)),
                   (1.0, self.link_text_score(rows, wordids)),
                   (1.0, self.nn_score(rows, wordids))
                   ]

        for weight, scores in weights:
            for url in total_scores:
                total_scores[url] += weight * scores[url]
        return total_scores

    def get_url_name(self, id):
        return self.conn.execute(
            'SELECT url FROM urllist WHERE rowid=%d' % id
        ).fetchone()[0]

    def query(self, q, n=10):
        rows, wordids = self.get_match_rows(q)
        scores = self.get_scored_list(rows, wordids)
        ranked_scores = sorted(
            [(score, url) for (url, score) in scores.items()],
            reverse=True
        )
        for score, urlid in ranked_scores[:n]:
            print '%.2f\t%s' % (score, self.get_url_name(urlid))

        return wordids, [result[1] for result in ranked_scores[:10]]

    def normalize_scores(self, scores, small_is_better=False):
        # Avoid division by zero errors
        very_small = 0.00001

        if small_is_better:
            min_score = min(scores.values())
            return dict(
                [(item, float(min_score) / max(very_small, score))
                for item, score in scores.items()
                ]
            )
        else:
            max_score = max(scores.values())
            if max_score == 0: max_score = very_small
            return dict(
                [(item, float(score) / max_score)
                for item, score in scores.items()
                ]
            )

    def frequency_score(self, rows):
        counts = dict([(row[0], 0) for row in rows])
        for row in rows: counts[row[0]] += 1
        return self.normalize_scores(counts)

    def location_score(self, rows):
        locations = dict([(row[0], 1000000) for row in rows])
        for row in rows:
            loc = sum(row[1:])
            if loc < locations[row[0]]:
                locations[row[0]] = loc
        return self.normalize_scores(locations, small_is_better=True)

    def distance_score(self, rows):
        # If there's only one word, everyone wins!
        if len(rows[0]) <= 2: return dict([(row[0], 1.0) for row in rows])

        # Initialize the dictionary with large values
        min_distance = dict([(row[0], 1000000) for row in rows])

        for row in rows:
            dist = sum([abs(row[i] - row[i-1])
                        for i in range(2, len(row))])
            if dist < min_distance[row[0]]:
                min_distance[row[0]] = dist
        return self.normalize_scores(min_distance, small_is_better=True)

    def inbound_links_score(self, rows):
        unique_urls = set([row[0] for row in rows])
        inbound_counts = dict(
            [
            (url, self.conn.execute(
                "SELECT count(*) FROM link WHERE toid=%d" % url
            ).fetchone()[0]
            )
            for url in unique_urls
            ]
        )
        return self.normalize_scores(inbound_counts)

    def pagerank_score(self, rows):
        pageranks = dict(
            [(row[0], self.conn.execute(
                'SELECT score FROM pagerank WHERE urlid=%d' % row[0]
            ).fetchone()[0])
             for row in rows]
        )
        return self.normalize_scores(pageranks)

    def link_text_score(self, rows, wordids):
        scores = dict([(row[0], 0) for row in rows])
        # loop over each word in query
        for wordid in wordids:
            # find a link which used the word in its text
            # by joining link and linkwords tables
            cursor = self.conn.execute(
                'SELECT link.fromid,link.toid FROM link,linkwords \
                 WHERE wordid=%d AND link.rowid=linkwords.linkid' % wordid
            )
            for (fromid, toid) in cursor:
                if toid in scores:
                    # get the pagerank of source link
                    pr = self.conn.execute(
                        'SELECT score FROM pagerank WHERE urlid=%d' % fromid
                    ).fetchone()[0]
                    # adding the pagerank of source link
                    # to destination's final score
                    scores[toid] += pr
        return self.normalize_scores(scores)

    def nn_score(self, rows, wordids):
        # Get unique URL IDs as an ordered list
        urlids = [urlid for urlid in set([row[0] for row in rows])]
        nn_result = mynet.get_result(wordids, urlids)
        scores = dict([(urlids[i], nn_result[i]) for i in range(len(urlids))])
        return self.normalize_scores(scores)