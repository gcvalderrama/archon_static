import json
from pprint import pprint
import networkx as nx
from diagrams import Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB
from diagrams.programming.language import Python


def get_kind(item):
    kind = 'unknow'
    if '<module>' in item['name']:
        kind = 'module'
    else:
        kind = 'method'
    return kind


def register_node(G, current_key, item, kind):
    file = item['file'].replace(':', ' ')
    name = item['name'].replace(':', ' ')
    G.add_node(current_key, label=name,
               file=file, line=item['line'], kind=kind)


target_dir = 'E:/github/beagle-roe'
startup_file = 'wip/profile.speed'

target = '{}/{}'.format(target_dir, startup_file)

G = nx.DiGraph()
G.add_node('start', label='start', file='start', line='0', kind='module')

with open(target, 'r') as f:
    information = json.load(f)
    height = [len(y) for y in [x['samples'] for x in information['profiles']]]

    for profile in information['profiles']:
        pprint(profile['name'])
        profile['data'] = []
        for i in range(len(profile['samples'])):
            samples = profile['samples'][i]
            weight = profile['weights'][i]
            data = []
            for item in samples:
                s = information['shared']['frames'][item]
                if 'beagle-roe\\app' in s['file']:
                    data.append(s)

            if data:
                profile['data'].append(data)

    for profile in information['profiles']:
        for data in profile['data']:
            previous_key = 'start'
            for item in data:
                item['file'] = item['file'].replace(
                    'E:\\github\\beagle-roe\\app\\', '')
                current_key = '{} {}'.format(item['file'], item['name'])
                kind = get_kind(item)
                if kind == 'module':
                    continue

                if not G.nodes.get(current_key):
                    register_node(G, current_key, item, kind)

                if not G.has_edge(previous_key, current_key):
                    G.add_edge(previous_key, current_key, weight=0)

                G.edges[previous_key, current_key]['weight'] += 1

                previous_key = current_key

    nx.write_gml(G, "./wip/graph.gml")

    import matplotlib.pyplot as plt


    
    #pos = nx.nx_pydot.graphviz_layout(G, prog='dot')
    pos = nx.nx_pydot.graphviz_layout(G, prog='dot')
    #pos = nx.spring_layout(G,scale=4)
    #pos = nx.nx_agraph.graphviz_layout(G)
    x = G.nodes()
    edges = G.edges()

    weight = [G.edges[e]['weight'] if G.edges[e]
              ['weight'] < 100 else 100 for e in edges]
    weight = [w / 10 for w in weight]

    labels = {n: '{} {} {}'.format( lab['file'], lab['label'], lab['line'] ) for n, lab in G.nodes.items() if n in pos}

    plt.figure(figsize=(20,14))
    nx.draw_networkx_labels(G, pos, labels=labels)
    nx.draw_networkx_edge_labels(
        G, pos, edge_labels=nx.get_edge_attributes(G, 'weight'))
    nx.draw_networkx_nodes(G, pos, label="nodes")
    nx.draw_networkx_edges(G, pos=pos,
                           edgelist=edges,
                           width=weight,
                           alpha=0.5,
                           label='data',
                           edge_color='green',
                           style='dashed' )

    plt.savefig("./wip/graph.png", dpi=300)
    #plt.show()
    
    
# with Diagram("Web Service", './wip/output', show=True, direction="TB"):
#     pivot_node = Python("start")
#     pivot = 'start'
#     for edge in G.edges():
#         if edge[0] == pivot:
#             tt = '{} : {}'.format(G.nodes[edge[1]]['file'], G.nodes[edge[1]]['label'])
#             pivot_node >> Python(tt)            
