import json

def dump_json(clusters, labels, filename='lastfm.json'):
    children = []
    for cluster in clusters:
        if cluster:
            cluster_dict = {'name':'', 'children':[]}
            for item in cluster:
                cluster_dict['children'].append({'name':labels[item]})
            children.append(cluster_dict)
    result = {'name':'', 'children':children}
    with open(filename, 'w') as f:
        json.dump(result, f)