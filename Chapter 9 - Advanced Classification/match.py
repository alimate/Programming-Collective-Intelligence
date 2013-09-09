import math
import urllib2
from urllib import quote_plus
from xml.dom import minidom
from matplotlib.pyplot import *

# a class that represent each row in the dataset
class Match:
    def __init__(self, row, all_numeric=False):
        if all_numeric:
            self.data = [float(row[i]) for i in range(len(row) - 1)]
        else:
            self.data = row[:len(row) - 1]
        self.match = int(row[len(row) - 1])

def load_match(filename, all_numeric=False):
    rows = []
    for line in open(filename):
        rows.append(Match(line.strip().split(','), all_numeric))
    return rows

def plot_age_matches(rows):
    # dm stands for do match
    xdm = [row.data[0] for row in rows if row.match == 1]
    ydm = [row.data[1] for row in rows if row.match == 1]

    # dn stands for don't match
    xdn = [row.data[0] for row in rows if row.match == 0]
    ydn = [row.data[1] for row in rows if row.match == 0]

    plot(xdm, ydm, 'ko')
    plot(xdn, ydn, 'kx')

    show()

def yes_no(value):
    value = value.lower()
    if value == 'yes': return 1
    elif value == 'no': return -1
    return 0

def common_interests(interest1, interest2):
    # convert lists to sets
    set1 = set(interest1.strip().split(':'))
    set2 = set(interest2.strip().split(':'))
    # calculate the intersection of two sets
    common = set1 & set2
    return len(common)

location_cache = {}
def geocode(address, trials=3):
    if address in location_cache: return location_cache[address]
    base = 'http://maps.googleapis.com/maps/api/geocode/xml'
    url = base + '?address=%s&sensor=false' % quote_plus(address)
    for trial in range(trials):
        try:
            data = urllib2.urlopen(url)
            result = minidom.parse(data)
            status = result.getElementsByTagName('status')[0]\
            .firstChild.nodeValue
            if status == 'OK':
                lat = result.getElementsByTagName('lat')[0]\
                .firstChild.nodeValue
                lng = result.getElementsByTagName('lng')[0]\
                .firstChild.nodeValue
                location_cache[address] = (float(lat), float(lng))
                return location_cache[address]
        except:
            print 'Something went wrong in trial #%d' % (trial + 1,)
    return 0, 0

def miles_distance(address1, address2):
    # get geo information for two addresses
    lat1, long1 = geocode(address1)
    lat2, long2 = geocode(address2)
    # calculate the difference
    lat_diff = 69.1 * (lat2 - lat1)
    long_diff = 53 * (long2 - long1)
    return math.sqrt(pow(lat_diff, 2) + pow(long_diff, 2))

def load_numerical():
    old_rows = load_match('matchmaker.csv')
    new_rows = []
    for row in old_rows:
        data = row.data
        new_row = [
            float(data[0]), # his age
            yes_no(data[1]), # does he smoke?
            yes_no(data[2]), # does he want children?
            float(data[5]), # her age
            yes_no(data[6]), # does she smoke?
            yes_no(data[7]), # does she want children?
            common_interests(data[3], data[8]), # number of common interests
            miles_distance(data[4], data[9]), # distance between them
            row.match # do they match?
        ]
        new_rows.append(Match(new_row))
    return new_rows

def scale_data(rows):
    lowest = [999999999.0] * len(rows[0].data)
    highest = [-999999999.0] * len(rows[0].data)

    # find the lowest and highest values
    for row in rows:
        data = row.data
        for i in range(len(data)):
            if data[i] < lowest[i]: lowest[i] = data[i]
            if data[i] > highest[i]: highest[i] = data[i]

    # create a function that scales the data
    def scale_input(data):
        scaled = []
        for i in range(len(data)):
            # to prevent division by zero exception!
            if lowest[i] == highest[i]:
                scaled.append(1)
            else:
                scaled.append(
                    (data[i] - lowest[i]) / (highest[i] - lowest[i])
                )
        return scaled

    # scale all the data
    scaled_data = [
        Match(scale_input(row.data) + [row.match])
        for row in rows
    ]

    return scaled_data, scale_input