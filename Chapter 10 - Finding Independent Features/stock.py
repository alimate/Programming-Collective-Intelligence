import urllib2
from numpy import *

# list of ticker symbols
tickers = [
    'YHOO', # Yahoo!
    'AVP', # Avon Products
    'BIIB', # Biogen Idec Inc.
    'BP', # BP plc
    'CL', # Colgate Palmolive Co.
    'CVX', # Chevron Corporation
    'EXPE', # Expedia Inc.
    'GOOG', # Google Inc.
    'PG', # Procter & Gamble Co.
    'XOM', # Exxon Mobil Corporation
    'AMGN', # Amgen Inc.
]

def retrieve_data():
    shortest = 300
    dates = None
    prices = {}

    for ticker in tickers:
        # construct the url
        url = 'http://ichart.finance.yahoo.com/table.csv?' +\
              's=%s&d=11&e=26&f=2006&g=d&a=3&b=12&c=1996' \
              '&ignore=.csv' % ticker
        try:
            print 'Retrieving %s' % ticker
            rows = urllib2.urlopen(url).readlines()
        except:
            print '\tSomething went wrong, continue...'
            continue

        # extract the volume field from every line
        prices[ticker] = [float(row.split(',')[5])
                          for row in rows[1:] if row.strip() != '']
        if len(prices[ticker]) < shortest: shortest = len(prices[ticker])

        if not dates:
            dates = [row.split(',')[0]
                     for row in rows[1:] if row.strip() != '']
    return prices, dates, shortest

def make_matrix(prices, shortest):
    dataset = [[prices[tickers[i]][j] for i in range(len(tickers))]
        for j in range(shortest)]
    return dataset

def show_features(w, h, dates, shortest, out='financial.txt'):
    out_file = open(out, 'w')

    # Loop over all the features
    for i in range(shape(h)[0]):
        out_file.write("Feature %d \n" % i)

        # Get the top stocks for this feature
        top_stocks = [(h[i ,j], tickers[j]) for j in range(shape(h)[1])]
        top_stocks.sort()
        top_stocks.reverse()

        # write top stocks to output file
        out_file.write('\tTop Stocks:\n')
        for j in range(len(tickers)):
            out_file.write('\t\t' + str(top_stocks[j]) + '\n')
        out_file.write('\n')

        # Show the top dates for this feature
        top_dates = [(w[d, i], d) for d in range(shortest)]
        top_dates.sort()
        top_dates.reverse()

        # write top dates to output file
        out_file.write('\tTop Dates:\n')
        for date in top_dates[:3]:
            out_file.write('\t\t' + str((date[0], dates[date[1]])) + '\n')
        out_file.write('\n')