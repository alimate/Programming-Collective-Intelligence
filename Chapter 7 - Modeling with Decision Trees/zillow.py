import urllib2
from urllib import quote_plus
from xml.dom import minidom

# put your api key here
zws_key = 'X1-ZWz1df0m7s26ff_1k6qj'
base = 'http://www.zillow.com/webservice/GetDeepSearchResults.htm'

def get_address_data(address, city):
    # construct the url
    url = base
    url += '?zws-id=%s&address=%s&citystatezip=%s' % (
        zws_key, quote_plus(address), quote_plus(city)
    )

    # request the resource
    try:
        data = urllib2.urlopen(url)
    except:
        print 'Unsuccessful Request'
        return None

    # parse retrieved XML
    doc = minidom.parseString(data.read())

    # extract error code
    code = doc.getElementsByTagName('code')[0].firstChild.data

    # code 0 means success; otherwise there was an error
    if code != '0':
        print 'Error in retrieval'
        return None

    # extract the results
    home_facts = []
    results = doc.getElementsByTagName('result')
    for result in results:
        # extract info about this property
        try:
            zip_code = result.getElementsByTagName(
                'zipcode')[0].firstChild.data
            use_code = result.getElementsByTagName(
                'useCode')[0].firstChild.data
            year = result.getElementsByTagName(
                'yearBuilt')[0].firstChild.data
            bath = result.getElementsByTagName(
                'bathrooms')[0].firstChild.data
            bed = result.getElementsByTagName(
                'bedrooms')[0].firstChild.data
            rooms = result.getElementsByTagName(
                'totalRooms')[0].firstChild.data
            area = result.getElementsByTagName(
                'finishedSqFt')[0].firstChild.data
            price = result.getElementsByTagName(
                'amount')[0].firstChild.data
            home_facts.append([
                zip_code, use_code, int(year), float(bath),
                int(bed), int(rooms),int(area), price
            ])
        except:
            print 'Next'

    return home_facts

def get_price_list(filename='addresslist.txt'):
    results = []
    for line in open(filename):
        print 'Retrieving "%s"' % line.strip()
        data = get_address_data(line.strip(), 'Cambridge,MA')
        if data:
            results += data
    return results