"""
Lewis Smith
Based loosely off the psuedo-code in:
    Enhanced nearest neighbour search on the R-tree (Cheung, Fu 1998)
    &
    R-Trees: A Dynamic Index Structure for Spatial Searching (Antonn Guttmann, 1984)
"""

from random import randint
from math import ceil, sqrt
import sys
import timeit


class Rtree:
    def __init__(self, root=None, b=6.0):
        self.root = root
        self.size = 0
        self.b = b
        self.seq_load = 0
        self.depth = 0

    def r_tree(self):
        self.root = self.create_root(True)

    def create_root(self, leaf_bool):
        init_coordinates = [float("inf"), float("inf"), float("inf"), float("inf")]

        return self.Node(leaf_bool, bounding_box=init_coordinates, children=[], root=True)

    def load_points(self, args):
        start_load = timeit.default_timer()
        with open(args[0]) as f:
            content = f.readlines()
            content = [x.strip() for x in content]
            content = [x.split() for x in content]
            self.r_tree()
            self.size = float(content[0][0])
            content.pop(0)
            if self.size > 10000:
                self.b = self.size*0.01
            [self.insert([int(x[1]), int(x[2])], x[0]) for x in content]
        stop_load = timeit.default_timer()
        self.seq_load = stop_load - start_load
        print("Load time: " + str(self.seq_load))

        start_query = timeit.default_timer()
        with open(args[1]) as f:
            content = f.readlines()
            content = [x.strip() for x in content]
            content = [x.split() for x in content]
            [self.range_query([int(x[0]), float(x[3]), float(x[1]), float(x[2])]) for x in content]
        stop_query = timeit.default_timer()
        f = open('query_results.txt', 'a')
        f.write('Total Time = ' + str(stop_query - start_query) + '\n' +
                'Average Time = ' + str((stop_query - start_query)/100))
        f.close()

        start_nn = timeit.default_timer()
        with open(args[2]) as f:
            content = f.readlines()
            content = [x.strip() for x in content]
            content = [x.split() for x in content]
            [self.nearest([float(x[0]), float(x[1])]) for x in content]
        stop_nn = timeit.default_timer()
        f = open('nn_results.txt', 'a')
        f.write('Total Time = ' + str(stop_nn - start_nn) + '\n' +
                'Average Time = ' + str((stop_query - start_query)/100))
        f.close()

    def insert(self, coordinates, id):
        entry = self.Node.Entry(id, coordinates, self.Node)
        leaf = self.find_leaf(self.root, entry)
        leaf.children.append(entry)
        self.size = self.size + 1
        entry.parent = leaf

        if len(leaf.children) > ceil(0.4*self.b):
            new_splits = self.split_node(leaf)
            self.adjust_tree(new_splits[0], new_splits[1])
        else:
            self.adjust_tree(leaf, None)

    def range_query(self, coordinates):
        results = []
        self.query(coordinates, self.root, results)
        f = open('query_results.txt', 'a')
        f.write(str(len(results)) + '\n')
        f.close()

    def query(self, coordinates, node, results):
        if node.leaf:
            for child in node.children:
                if self.overlap_leaf(coordinates, child.coordinates):
                    results.append(child.id)
        else:
            for child in node.children:
                if self.overlaps(coordinates, child.bounding_box):
                    self.query(coordinates, child, results)

    @staticmethod
    def overlap_leaf(coordinates, leaf_coordinates):
        if leaf_coordinates[0] < coordinates[0] or leaf_coordinates[0] > coordinates[3] or \
                        leaf_coordinates[1] < coordinates[3] or leaf_coordinates[1] > coordinates[1]:
            return False
        else:
            return True

    def nearest(self, coordinates):
        point_id = []
        distance = float("inf")
        self.nearest_neighbor(coordinates, self.root, point_id, distance)
        f = open('nn_results.txt', 'a')
        f.write(str(min(point_id, key=lambda x: x[1])[0]) + '\n')
        f.close()

    def nearest_neighbor(self, coordinates, node, point_id, dist):
        if node.leaf:
            distance = float("inf")
            for child in node.children:
                temp = sqrt((child.coordinates[0] - coordinates[0])**2
                            + (child.coordinates[1] - coordinates[1])**2)
                if temp < distance:
                    distance = temp
                    point_id.append([child.id, temp])
        else:
            list = []
            for child in node.children:
                if child.bounding_box[0] < coordinates[0]:
                    dx = coordinates[0] - child.bounding_box[0]
                elif child.bounding_box[0] > coordinates[0]:
                    dx = child.bounding_box[0] - coordinates[0]
                else:
                    dx = 0

                if child.bounding_box[3] < coordinates[1]:
                    dy = coordinates[1] - child.bounding_box[3]
                elif child.bounding_box[3] > coordinates[1]:
                    dy = child.bounding_box[3] - coordinates[1]
                else:
                    dy = 0

                min_distance = dx * dx + dy * dy
                list.append([child, min_distance])
            ABL = sorted(list, key=lambda x: x[1])
            for node in ABL:
                if node[1] < dist:
                    self.nearest_neighbor(coordinates, node[0], point_id, dist)

    @staticmethod
    def overlaps(coordinates, child_box):
        if coordinates[0] > child_box[2] or coordinates[1] < child_box[3] \
                or coordinates[2] < child_box[0] or coordinates[3] > child_box[1]:
            return False
        else:
            return True

    def find_leaf(self, node, entry):
        if node.leaf:
            return node

        min_increase = float("inf")

        for child in node.children:
            exp = self.get_expansion(child.bounding_box, entry)

            if exp < min_increase:
                min_increase = exp
                next_child = child
            elif exp == min_increase:
                current_area = self.get_area(next_child.bounding_box)
                new_area = self.get_area(node.bounding_box)

                if new_area < current_area:
                    next_child = child

        return self.find_leaf(next_child, entry)

    @staticmethod
    def get_area(bounding_box):
        return (bounding_box[2]-bounding_box[0])*(bounding_box[1]-bounding_box[3])

    def get_expansion(self, bounding_box, entry):
        area = self.get_area(bounding_box)
        new = list(bounding_box)
        if type(entry) is self.Node.Entry:
            if bounding_box[0] > entry.coordinates[0]:
                new[0] = entry.coordinates[0]
            if bounding_box[2] < entry.coordinates[0]:
                new[2] = entry.coordinates[0]
            if bounding_box[1] < entry.coordinates[1]:
                new[1] = entry.coordinates[1]
            if bounding_box[3] > entry.coordinates[1]:
                new[3] = entry.coordinates[1]

        else:
            if bounding_box[0] < entry.bounding_box[0]:
                new[0] = entry.bounding_box[0]

            if bounding_box[2] > entry.bounding_box[2]:
                new[2] = entry.bounding_box[2]

            if bounding_box[1] > entry.bounding_box[1]:
                new[1] = entry.bounding_box[1]

            if bounding_box[3] < entry.bounding_box[3]:
                new[3] = entry.bounding_box[3]

        return self.get_area(new) - area

    def adjust_tree(self, node_one, node_two):
        if node_one.root:
            if node_two is not None:
                node_one.root = False
                self.root = self.create_root(False)
                self.root.children.append(node_one)
                node_one.parent = self.root
                self.root.children.append(node_two)
                node_two.parent = self.root
            self.tighten([self.root])
            return

        self.tighten([node_one])

        if node_two is not None:
            self.tighten([node_two])
            if len(node_one.parent.children) > ceil(0.4*self.b):
                splits = self.split_node(node_one.parent)
                self.adjust_tree(splits[0], splits[1])

        if node_one.parent is not None:
            self.adjust_tree(node_one.parent, None)

    def split_node(self, node):
        nodes = [node, self.Node(node.leaf, bounding_box=node.bounding_box, parent=node.parent, children=[])]

        if nodes[1].parent is not None:
            nodes[1].parent.children.append(nodes[1])

        childs = list(node.children)
        node.children = []
        seed_one, seed_two = self.pick_seeds(childs)
        nodes[0].children.append(seed_one)
        nodes[1].children.append(seed_two)

        self.tighten(nodes)

        while len(childs) != 0:
            if len(nodes[0].children) >= 2 and len(nodes[1].children) + len(childs) == 2:
                nodes[1].children.extend(list(childs))
                childs = []
                self.tighten(nodes)

                return nodes
            elif len(nodes[1].children) >= 2 and len(nodes[0].children) + len(childs) == 2:
                nodes[0].children.extend(list(childs))
                childs = []
                self.tighten(nodes)

                return nodes

            seed = self.get_seed(childs)

            expansion_one = self.get_expansion(nodes[0].bounding_box, seed)
            expansion_two = self.get_expansion(nodes[1].bounding_box, seed)

            if expansion_one < expansion_two:
                ideal_node = nodes[0]
            elif expansion_one > expansion_two:
                ideal_node = nodes[1]
            else:
                area_one = self.get_area(nodes[0].bounding_box)
                area_two = self.get_area(nodes[1].bounding_box)
                if area_one < area_two:
                    ideal_node = nodes[0]
                elif area_one > area_two:
                    ideal_node = nodes[1]
                else:
                    if len(nodes[0].children) < len(nodes[1].children):
                        ideal_node = nodes[0]
                    elif len(nodes[0].children) > len(nodes[1].children):
                        ideal_node = nodes[1]
                    else:
                        ideal_node = nodes[randint(0, len(nodes) - 1)]
            ideal_node.children.append(seed)
            self.tighten([ideal_node])
        return list(nodes)

    @staticmethod
    def get_seed(children):
            return children.pop(0)

    def pick_seeds(self, children):
        found = False
        best_separation = 0.0

        for i in range(2):
            lower_bound = float("inf")
            upper_bound = -1*float("inf")
            min_upper_bound = float("inf")
            max_lower_bound = -1*float("inf")

            for node in iter(children):
                if type(node) is self.Node.Entry:
                    if node.coordinates[i] < lower_bound:
                        lower_bound = node.coordinates[i]

                    if node.coordinates[i] > upper_bound:
                        upper_bound = node.coordinates[i]

                    if node.coordinates[i] > max_lower_bound:
                        max_lower_bound = node.coordinates[i]
                        node_lower_bound = node

                    if node.coordinates[i] < min_upper_bound:
                        min_upper_bound = node.coordinates[i]
                        node_upper_bound = node
                else:
                    if i == 0:
                        if node.bounding_box[i+2] > upper_bound:
                            upper_bound = node.bounding_box[i+2]
                        if node.bounding_box[i] < lower_bound:
                            lower_bound = node.bounding_box[i]
                        if node.bounding_box[i+2] < min_upper_bound:
                            min_upper_bound = node.bounding_box[i+2]
                            node_upper_bound = node
                        if node.bounding_box[i] > max_lower_bound:
                            max_lower_bound = node.bounding_box[i]
                            node_lower_bound = node
                    else:
                        if node.bounding_box[i] > upper_bound:
                            upper_bound = node.bounding_box[i]
                        if node.bounding_box[i+2] < lower_bound:
                            lower_bound = node.bounding_box[i+2]
                        if node.bounding_box[i] < min_upper_bound:
                            min_upper_bound = node.bounding_box[i]
                            node_upper_bound = node
                        if node.bounding_box[i+2] > max_lower_bound:
                            max_lower_bound = node.bounding_box[i+2]
                            node_lower_bound = node

            if node_lower_bound == node_upper_bound:
                separation = -1.0
            else:
                if min_upper_bound == max_lower_bound or upper_bound == lower_bound:
                    separation = -1.0
                else:
                    separation = abs((max_lower_bound-min_upper_bound)/(upper_bound-lower_bound))

            if separation >= best_separation:
                seeds = [node_lower_bound, node_upper_bound]
                best_separation = separation
                found = True

        if not found:
            seeds = list([children[0], children[1]])

        children.remove(seeds[0])
        children.remove(seeds[1])

        return seeds[0], seeds[1]

    def tighten(self, nodes):
            for node in iter(nodes):
                min_coordinates = [float("inf"), -1*float("inf"), -1*float("inf"), float("inf")]
                for child in iter(node.children):
                    if type(child) is self.Node.Entry:
                        if child.coordinates[0] < min_coordinates[0]:
                            min_coordinates[0] = child.coordinates[0]

                        if child.coordinates[0] > min_coordinates[2]:
                            min_coordinates[2] = child.coordinates[0]

                        if child.coordinates[1] > min_coordinates[1]:
                            min_coordinates[1] = child.coordinates[1]

                        if child.coordinates[1] < min_coordinates[3]:
                            min_coordinates[3] = child.coordinates[1]

                    else:
                        if child.bounding_box[0] < min_coordinates[0]:
                            min_coordinates[0] = child.bounding_box[0]

                        if child.bounding_box[2] > min_coordinates[2]:
                            min_coordinates[2] = child.bounding_box[2]

                        if child.bounding_box[1] > min_coordinates[1]:
                            min_coordinates[1] = child.bounding_box[1]

                        if child.bounding_box[3] < min_coordinates[3]:
                            min_coordinates[3] = child.bounding_box[3]

                node.bounding_box = list(min_coordinates)

    class Node:
        def __init__(self, leaf, parent=None, children=None, bounding_box=None, root=False):
            self.leaf = leaf
            self.parent = parent
            self.children = children
            self.bounding_box = bounding_box
            self.root = root

        class Entry:
            def __init__(self, id, coordinates, node):
                self.id = id
                self.node = node
                self.leaf = True
                self.coordinates = coordinates


if __name__ == "__main__":
    r = Rtree()
    if (len(sys.argv[1:]) != 3):
        raise RuntimeError('Usage: Rtree.py dataset queryset nn_queryset') from error    
    r.load_points(sys.argv[1:])

