from collections import deque, namedtuple
from random import randint, randrange, choice
from itertools import permutations
from time import time
from math import sqrt
import pygame

global MAX_NODES
global DEST_NODE

COMPLETE_GRAPH = False
INCLUDE_BRUTEFORCE_TRAVELLER = False
MAX_NODES = 8
MAX_NEIGHBOURS = 2
MIN_COST = 1
MAX_COST = 14

SOURCE_NODE = '1'
DEST_NODE = str(MAX_NODES)
APP_FONT = 'Comic Sans MS'
FONT_COLOR = (255,255,255)
SCREEN_SIZE = 1280, 600
BG_COLOR = (255,255,255)
NODE_COLOR = (0,0,0)
PNODE_COLOR = (80,220,100)
NODE_RADIUS = 16


inf = float('inf')
Edge = namedtuple('Edge', 'start, end, cost')
global gnodes
global selected
global path_dijkstra
global path_trav_brute
global path_trav_heur
gnodes = None
selected = 0


def timing(f):
    def wrap(*args):
        time1 = time()
        ret = f(*args)
        time2 = time()
        print('{:s} = {:.3f} ms'.format(f.__name__, (time2-time1)*1000.0))

        return ret
    return wrap


def make_edge(start, end, cost=1):
  return Edge(start, end, cost)


class Graph:
    def __init__(self, edges):
        wrong_edges = [i for i in edges if len(i) not in [2, 3]]
        if wrong_edges:
            raise ValueError('Wrong edges data: {}'.format(wrong_edges))

        self.edges = [make_edge(*edge) for edge in edges]

    @property
    def vertices(self):
        return set(
            sum(
                ([edge.start, edge.end] for edge in self.edges), []
            )
        )

    def get_node_pairs(self, n1, n2, both_ends=True):
        if both_ends:
            node_pairs = [[n1, n2], [n2, n1]]
        else:
            node_pairs = [[n1, n2]]
        return node_pairs

    def remove_edge(self, n1, n2, both_ends=True):
        node_pairs = self.get_node_pairs(n1, n2, both_ends)
        edges = self.edges[:]
        for edge in edges:
            if [edge.start, edge.end] in node_pairs:
                self.edges.remove(edge)

    def add_edge(self, n1, n2, cost=1, both_ends=True):
        node_pairs = self.get_node_pairs(n1, n2, both_ends)
        for edge in self.edges:
            if [edge.start, edge.end] in node_pairs:
                return ValueError('Edge {} {} already exists'.format(n1, n2))
            
        self.edges.append(Edge(start=n1, end=n2, cost=cost))
        if both_ends:
            self.edges.append(Edge(start=n2, end=n1, cost=cost))

    @property
    def neighbours(self):
        neighbours = {vertex: set() for vertex in self.vertices}
        for edge in self.edges:
            neighbours[edge.start].add((edge.end, edge.cost))

        return neighbours

    @timing
    def dijkstra(self, source, dest):
        # Verifica se aresta inicial existe no grafo
        assert source in self.vertices, 'Such source node doesn\'t exist'
        # Atribui uma distância infinita em cada vértice do grafo
        distances = {vertex: inf for vertex in self.vertices}
        previous_vertices = {
            vertex: None for vertex in self.vertices
        }
        distances[source] = 0
        vertices = self.vertices.copy()

        while vertices:
            current_vertex = min(
                vertices, key=lambda vertex: distances[vertex])
            vertices.remove(current_vertex)
            if distances[current_vertex] == inf:
                break
            for neighbour, cost in self.neighbours[current_vertex]:
                alternative_route = distances[current_vertex] + cost
                if alternative_route < distances[neighbour]:
                    distances[neighbour] = alternative_route
                    previous_vertices[neighbour] = current_vertex

        path, current_vertex = deque(), dest
        while previous_vertices[current_vertex] is not None:
            path.appendleft(current_vertex)
            current_vertex = previous_vertices[current_vertex]
        if path:
            path.appendleft(current_vertex)
        return path


def get_node_bypos(pos):
    for node in gnodes:
        if node.get_pos() == pos:
            return node
    return None


def translate_nodes_dijkstra(nodes):
    tnodes = list()
    for node in nodes:
        for neighbour in node.get_neighbours():
            tnodes.append((node.get_name(), neighbour.get_name(), neighbour.get_cost()))
    return tnodes


def draw():
    global selected
    SCREEN.fill(BG_COLOR)
    for node in gnodes:
        node.update()
        for neighbour in node.get_neighbours():
            pygame.draw.line(SCREEN, NODE_COLOR, node.get_pos(), neighbour.get_pos(), 2)
            if not selected:
                draw_pathlines(path_dijkstra)
            else:
                draw_pathlines(path_trav_heur)
            node.draw()
            neighbour.draw()


def draw_pathlines(path):
    pathlist = list(path)
    for i in range(len(pathlist)-1):
        node1 = get_node_by_name(pathlist[i])
        node2 = get_node_by_name(pathlist[i+1])
        pygame.draw.line(SCREEN, PNODE_COLOR, node1.get_pos(), node2.get_pos(), 2)


def get_node_by_name(name):
    for node in gnodes:
        if node.get_name() == name:
            return node
    return None


class Node:
    def __init__(self, name, cost, pos, color):
        self.name = name
        self.neighbours = set()
        self.cost = cost
        self.pos = pos
        self.color = color

    def update(self):
        global selected
        if not selected:
            self.color = PNODE_COLOR if self.name in path_dijkstra else NODE_COLOR
        else:
            self.color = PNODE_COLOR if self.name in path_trav_heur else NODE_COLOR

    def draw(self):
        title_text = app_font3.render('Dijkstra' if not selected else 'Traveller', False, NODE_COLOR)
        name_text = app_font.render(self.name, False, FONT_COLOR if self.color == NODE_COLOR else NODE_COLOR)
        cost_text = app_font2.render(str(self.cost), False, NODE_COLOR)
        pygame.draw.circle(SCREEN, self.color, self.pos, NODE_RADIUS)
        SCREEN.blit(name_text, (self.pos[0]-NODE_RADIUS/1.5, self.pos[1]-NODE_RADIUS/1.5))
        SCREEN.blit(cost_text, (self.pos[0]-NODE_RADIUS*1.75, self.pos[1]-NODE_RADIUS*1.5))
        SCREEN.blit(title_text, (SCREEN_SIZE[0]/2.25, NODE_RADIUS))

    def get_name(self):
        return self.name

    def get_cost(self):
        return self.cost

    def get_neighbours(self):
        return list(self.neighbours)

    def add_neighbour(self, node):
        self.neighbours.add(node)

    def get_pos(self):
        return self.pos

    def get_color(self):
        return self.color


def repair_nodelist(points, start=None):
    if start is None:
        start = points[0]
    must_visit = points
    path = [start]
    must_visit.remove(start)
    while must_visit:
        nearest = min(must_visit, key=lambda x: distance(path[-1], x))
        path.append(nearest)
        must_visit.remove(nearest)
    for i in range(len(path)-1):
        get_node_bypos(path[i]).add_neighbour(get_node_bypos(path[i+1]))


@timing
def random_graph(min_cost, max_cost):
    count = 1
    nodes = list()
    for i in range(MAX_NODES):
        rand_pos = (randrange(NODE_RADIUS, SCREEN_SIZE[0]-NODE_RADIUS, 2*NODE_RADIUS),
                        randrange(NODE_RADIUS, SCREEN_SIZE[1]-NODE_RADIUS, 2*NODE_RADIUS))
        rand_cost = randint(min_cost, max_cost)
        node = Node(str(count), rand_cost, rand_pos, NODE_COLOR)
        if nodes:
            if COMPLETE_GRAPH:
                for n in nodes:
                    neighbour = n
                    node.neighbours.add(neighbour)
                    neighbour.neighbours.add(node)
            else:
                for i in range(0, randrange(1, MAX_NEIGHBOURS)):
                    neighbour = choice(nodes)
                    node.neighbours.add(neighbour)
                    neighbour.neighbours.add(node)
        nodes.append(node)
        count += 1
    return nodes


def distance(point1, point2):
    return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2) ** 0.5


def total_distance(points):
    return sum([distance(point, points[index + 1]) for index, point in enumerate(points[:-1])])


@timing
def travelling_salesman_bruteforce(points, start=None):
    if start is None:
        start = points[0]
    return min([perm for perm in permutations(points) if perm[0] == start], key=total_distance)


@timing
def travelling_salesman(start, end):
    must_visit = [node.get_pos() for node in gnodes]
    path = [start.get_pos()]
    must_visit.remove(start.get_pos())
    while must_visit:
        nearest = min(must_visit, key=lambda x: distance(path[-1], x))
        path.append(nearest)
        must_visit.remove(nearest)
    return path

def fix_traveller_path(path):
    for neigh in get_node_bypos(path[-1]).get_neighbours():
        if neigh.get_pos() == gnodes[-1].get_pos():
            path.append(gnodes[-1].get_pos())
    return path

def init():
    global SCREEN
    global app_font
    global app_font2
    global app_font3
    pygame.init()
    #SCREEN = pygame.display.set_mode(SCREEN_SIZE, pygame.FULLSCREEN)
    SCREEN = pygame.display.set_mode(SCREEN_SIZE)
    pygame.font.init()
    app_font = pygame.font.SysFont(APP_FONT, NODE_RADIUS+2, False)
    app_font2 = pygame.font.SysFont(APP_FONT, NODE_RADIUS-2, False)
    app_font3 = pygame.font.SysFont(APP_FONT, 22, False)


def load():
    global gnodes
    global path_dijkstra
    global path_trav_brute
    global path_trav_heur

    print('')
    gnodes = random_graph(MIN_COST, MAX_COST)
    repair_nodelist([node.get_pos() for node in gnodes])
    graph = Graph(translate_nodes_dijkstra(gnodes))

    path_dijkstra = graph.dijkstra(SOURCE_NODE, DEST_NODE)
    #print('Dijkstra path from node {} to node {} = {}'.format(SOURCE_NODE, DEST_NODE, list(path_dijkstra)))

    print(gnodes[0].get_name(), gnodes[MAX_NODES-1].get_name())
    path_trav_heur = fix_traveller_path(travelling_salesman(gnodes[0], gnodes[MAX_NODES-1]))
    path_trav_heur = [get_node_bypos(node).get_name() for node in path_trav_heur]
    #print('Travelling Salesman (heuristic) path from node {} to node {} = {}'.format(SOURCE_NODE, DEST_NODE, path_trav_heur))

    if INCLUDE_BRUTEFORCE_TRAVELLER:
        path_trav_brute = travelling_salesman_bruteforce([node.get_pos() for node in gnodes])


def main():
    load()
    try:
        global selected
        global MAX_NODES
        global DEST_NODE
        init()
        while True:
            pygame.event.pump()

            if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                break
            
            if pygame.key.get_pressed()[pygame.K_SPACE]:
                load()

            if pygame.key.get_pressed()[pygame.K_LEFT]:
                selected -= 1

            if pygame.key.get_pressed()[pygame.K_RIGHT]:
                selected += 1
            
            if pygame.key.get_pressed()[pygame.K_DOWN]:
                MAX_NODES = int(MAX_NODES/2)
                DEST_NODE = str(MAX_NODES)
                load()

            if pygame.key.get_pressed()[pygame.K_UP]:
                MAX_NODES *= 2
                DEST_NODE = str(MAX_NODES)
                load()

            if selected < 0:
                selected = 1
            elif selected > 1:
                selected = 0

            draw()

            pygame.display.flip()
            pygame.time.delay(60)
    except Exception as ex:
        print(ex)
    finally:
        quit()

if __name__ == "__main__":
    main()
