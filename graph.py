import networkx as nx
import matplotlib.pyplot as plt


def truncate(s):
    return (s[:9] + '.') if len(s) > 9 else s


def draw_graph(edges_dict: dict, nodes: list):
    # ------- DIRECTED

    # Build a dataframe with your connections
    # This time a pair can appear 2 times, in one side or in the other!
    edges = list()
    red_edges = list()
    for from_node in edges_dict.keys():
        for to_node in edges_dict[from_node]:
            if edges_dict[from_node][to_node]:
                edges.append((from_node, to_node))
            if edges_dict[from_node][to_node] and edges_dict[to_node][from_node]:
                red_edges.append((from_node, to_node))

    G = nx.DiGraph(directed=True)
    for n in nodes:
        G.add_node(n)
    G.add_edges_from(edges)
    black_edges = [edge for edge in G.edges()]

    # Need to create a layout when doing
    # separate calls to draw nodes and edges
    pos = nx.circular_layout(G)
    # pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos, cmap=plt.get_cmap('jet'), node_color='#73F4EA', node_size=5000, node_shape="o")
    nx.draw_networkx_labels(G, pos, font_size=8, font_weight="bold")
    nx.draw_networkx_edges(G, pos, edgelist=red_edges, edge_color="r", arrows=True, width=4, alpha=0.5)
    nx.draw_networkx_edges(G, pos, edgelist=black_edges, arrows=True, alpha=0.9)
    plt.margins(0.15, 0.15)
    return plt
