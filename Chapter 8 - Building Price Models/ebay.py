import re
import urllib2
from urllib import quote_plus
from xml.dom import minidom

#app_id = 'alimatei-5d94-44d7-9c6d-9b7da0660a8a'

class FindingAPI:
    def __init__(self, app_id,
            endpoint='http://svcs.ebay.com/services/search/FindingService/v1'):
        self.app_id = app_id
        self.endpoint = endpoint

    def find_items_by_category(self, category_id,
                               operation='findItemsByCategory', page=1):
        # construct the query string
        query_string = '?OPERATION-NAME=%s&'\
                       'SECURITY-APPNAME=%s&'\
                       'RESPONSE-DATA-FORMAT=XML&'\
                       'categoryId=%d&'\
                       'paginationInput.pageNumber=%d' % (
                           operation, self.app_id, category_id, page
                           )
        # construct the url
        url = self.endpoint + query_string

        # send the request
        data = urllib2.urlopen(url)
        return data.read()

class ShoppingAPI:
    def __init__(self, app_id, endpoint='http://open.api.ebay.com/shopping'):
        self.app_id = app_id
        self.endpoint = endpoint

    def get_single_item(self, item_id, call_name='GetSingleItem',
                        version='515',include_selector='ItemSpecifics'):
        # construct the query string
        query_string = '?appid=%s&' \
                       'callname=%s&' \
                       'version=%s&' \
                       'IncludeSelector=%s&' \
                       'ItemId=%s' % (
            self.app_id, call_name, version, quote_plus(include_selector),
            str(item_id)
        )

        # construct the url
        url = self.endpoint + query_string

        # send the request
        data = urllib2.urlopen(url)
        return data.read()

def get_single_value(node, tag):
    dom = node.getElementsByTagName(tag)
    if len(dom) > 0:
        tagNode = dom[0]
        if tagNode.hasChildNodes():
            return tagNode.firstChild.nodeValue
    return '-1'

def extract_value(node, name):
    for item in node:
        if get_single_value(item, 'Name').startswith(name):
            return get_single_value(item, 'Value')
    raise Exception('Name Not Found')

def get_items(api, num_pages=10, category_id=177):
    # initialize the dataset
    dataset = {}

    # retrieve items
    for page in range(1, num_pages + 1):
        print "Retrieving page #%d" % page
        try:
            data = api.find_items_by_category(category_id, page=page)
            # parsing the returned xml
            dom = minidom.parseString(data)
            status = get_single_value(dom, 'ack')
            if status == 'Success':
                items = dom.getElementsByTagName('item')
                # loop over all items
                for item in items:
                    try:
                        item_id = get_single_value(item, 'itemId')
                        title = get_single_value(item, 'title')
                        price = get_single_value(item, 'currentPrice')
                        dataset[item_id] = (title, price)
                    except:
                        print '\tError in parsing, next item...'
                        continue
        except:
            print '\tSomething went wrong, continue...'
            continue
    return dataset

def get_details(api ,items):
    # initialize some variables
    details = {}
    iteration = 1

    # retrieve details for each item
    for item_id in items:
        print 'Retrieving item #%s in iteration #%d' % (item_id, iteration)
        try:
            data = api.get_single_item(item_id)
            # parsing the returned xml
            dom = minidom.parseString(data)
            status = get_single_value(dom, 'Ack')
            if status == 'Success':
                try:
                    specifics = dom.getElementsByTagName('NameValueList')
                    screen_size = extract_value(specifics, 'Screen Size')
                    ram = extract_value(specifics, 'Memory')
                    cpu = extract_value(specifics, 'Processor Speed')
                    hard = extract_value(specifics, 'Hard')
                    details[item_id] = (screen_size, ram, cpu, hard)
                except:
                    print '\tError in parsing, continue...'
        except:
            print '\tSomething went wrong, continue...'
        iteration += 1

    return details

def create_dataset(items, details):
    dataset = []
    regex = re.compile(r'((\d+(\.\d+)?).*)')
    for item_id in details:
        # try to remove any non-numeric character
        try:
            details[item_id] = [float(regex.sub('\g<2>', detail))
                                for detail in details[item_id]]
            dataset.append({
                'input':details[item_id],
                'output':float(items[item_id][1])
            })
        except:
            print 'Error in Converting item #%s, continue...' % item_id

    return dataset