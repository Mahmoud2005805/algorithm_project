# Required libraries
import networkx as nx
import matplotlib.pyplot as plt
import imageio
import os
import random
import heapq
from collections import defaultdict

# Load graph from .edges file
def load_edges_from_file(filename):
    edges = []
    nodes = set()
    with open(filename, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                u, v = map(int, parts)
                w = 1.0
            elif len(parts) == 3:
                u, v, w = map(float, parts)
                u, v = int(u), int(v)
            else:
                continue
            edges.append((u, v, w))
            nodes.update([u, v])
    n = max(nodes) + 1
    return n, edges

# Draw graph frame
def draw_graph(n, edges, highlight_edges, step, algo_name, output_dir):
    G = nx.Graph()
    G.add_weighted_edges_from(edges)
    pos = nx.spring_layout(G, seed=42)

    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', alpha=0.5)
    if highlight_edges:
        nx.draw_networkx_edges(G, pos, edgelist=highlight_edges, edge_color='red', width=2)
    plt.title(f"{algo_name} - Step {step}")
    frame_path = os.path.join(output_dir, f"{algo_name}_frame_{step:03d}.png")
    plt.savefig(frame_path)
    plt.close()
    return frame_path

# Save video from frames
def create_video(image_paths, output_path, fps=2):
    with imageio.get_writer(output_path, mode='I', fps=fps) as writer:
        for path in image_paths:
            writer.append_data(imageio.imread(path))

# Union-Find structure for Kruskal and Karger
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
    def find(self, u):
        while self.parent[u] != u:
            self.parent[u] = self.parent[self.parent[u]]
            u = self.parent[u]
        return u
    def union(self, u, v):
        pu, pv = self.find(u), self.find(v)
        if pu != pv:
            self.parent[pu] = pv
            return True
        return False

# Kruskal's Algorithm
def kruskal_visual(n, edges, output_dir):
    uf = UnionFind(n)
    sorted_edges = sorted(edges, key=lambda x: x[2])
    mst = []
    frames = []
    for i, (u, v, w) in enumerate(sorted_edges):
        if uf.union(u, v):
            mst.append((u, v))
        frame = draw_graph(n, edges, mst, i, "Kruskal", output_dir)
        frames.append(frame)
    return frames

# Prim's Algorithm
def prim_visual(n, edges, output_dir):
    G = defaultdict(list)
    for u, v, w in edges:
        G[u].append((w, v))
        G[v].append((w, u))

    visited = [False] * n
    min_heap = [(0, 0, -1)]
    mst = []
    frames = []
    step = 0
    while min_heap:
        w, u, prev = heapq.heappop(min_heap)
        if visited[u]:
            continue
        visited[u] = True
        if prev != -1:
            mst.append((u, prev))
        frame = draw_graph(n, edges, mst, step, "Prim", output_dir)
        frames.append(frame)
        step += 1
        for weight, v in G[u]:
            if not visited[v]:
                heapq.heappush(min_heap, (weight, v, u))
    return frames

# Boruvka's Algorithm
def boruvka_visual(n, edges, output_dir):
    uf = UnionFind(n)
    mst = []
    frames = []
    num_components = n
    step = 0

    while num_components > 1:
        cheapest = [-1] * n
        for i, (u, v, w) in enumerate(edges):
            set_u = uf.find(u)
            set_v = uf.find(v)
            if set_u != set_v:
                if cheapest[set_u] == -1 or edges[cheapest[set_u]][2] > w:
                    cheapest[set_u] = i
                if cheapest[set_v] == -1 or edges[cheapest[set_v]][2] > w:
                    cheapest[set_v] = i

        for idx in cheapest:
            if idx != -1:
                u, v, w = edges[idx]
                if uf.union(u, v):
                    mst.append((u, v))
                    num_components -= 1
                    frame = draw_graph(n, edges, mst, step, "Boruvka", output_dir)
                    frames.append(frame)
                    step += 1
    return frames

# Reverse Delete Algorithm
def reverse_delete_visual(n, edges, output_dir):
    G = nx.Graph()
    G.add_weighted_edges_from(edges)
    sorted_edges = sorted(edges, key=lambda x: -x[2])
    frames = []
    step = 0

    for u, v, w in sorted_edges:
        G.remove_edge(u, v)
        if not nx.is_connected(G):
            G.add_edge(u, v, weight=w)
        mst_edges = list(G.edges())
        frame = draw_graph(n, edges, mst_edges, step, "ReverseDelete", output_dir)
        frames.append(frame)
        step += 1
    return frames

# Karger's Min Cut Algorithm (Visualized as Edge Contraction)
def karger_visual(n, edges, output_dir):
    G = nx.Graph()
    G.add_weighted_edges_from(edges)
    frames = []
    step = 0

    while len(G.nodes) > 2:
        u, v = random.choice(list(G.edges()))
        G = nx.contracted_nodes(G, u, v, self_loops=False)
        mst_edges = list(G.edges())
        frame = draw_graph(n, edges, mst_edges, step, "Karger", output_dir)
        frames.append(frame)
        step += 1
    return frames

# Main function
def main():
    filename = "ENZYMES_g55.edges"
    output_dir = "frames"
    os.makedirs(output_dir, exist_ok=True)

    n, edges = load_edges_from_file(filename)

    all_frames = []
    all_frames += kruskal_visual(n, edges, output_dir)
    all_frames += prim_visual(n, edges, output_dir)
    all_frames += boruvka_visual(n, edges, output_dir)
    all_frames += reverse_delete_visual(n, edges, output_dir)
    all_frames += karger_visual(n, edges, output_dir)

    create_video(all_frames, "all_mst_algorithms.mp4", fps=2)
    print("Video saved as all_mst_algorithms.mp4")

if __name__ == "__main__":
    main()
