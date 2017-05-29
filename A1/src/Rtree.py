class Rtree:
    def __init__(self, root=None, size=0):
        self.root = root
        self.size = size

    def r_tree(self):
        self.root = self.create_root()

    def create_root(self):
        init_coordinates = [0.0, 0.0]
        init_coordinates[0] = float("inf")
        init_coordinates[1] = float("inf")
        root = self.Node(True, init_coordinates)

        return root

    def load_points(self, filename):
        return 1

    def insert(self, coordinates, entry):
        ent = self.Node.Entry(entry, coordinates)
        leaf = self.find_leaf(self.root, ent)
        leaf.children.insert(leaf)
        self.size = self.size + 1
        entry.parent = leaf

        if leaf.children.size > 3:
            new_splits = self.split_node(leaf)
            self.adjust_tree(new_splits[0], new_splits[1])

    def find_leaf(self, node, entry):
        if node.leaf:
            return node

        min_increase = float("inf")

        for child in node.children:
            exp = self.get_expansion(child.coordinates, child.bounding_box, entry)

            if exp < min_increase:
                min_increase = exp
                next_child = child
            elif exp == min_increase:
                current_area = next_child.bounding_box[0]*next_child.bounding_box[1]
                new_area = node.bounding_box[0]*node.bounding_box[1]

                if new_area < current_area:
                    next_child = child

        return self.find_leaf(next_child, entry)

    @staticmethod
    def get_expansion(coordinates, bounding_box, entry):
        area = bounding_box[0]*bounding_box[1]
        new = []

        for i in range(2):
            if coordinates[i] + bounding_box[i] < entry.coordinates[i] + entry.bounding_box[i]:
                new[i] = entry.coordinates[i] + entry.bounding_box[i] - coordinates[i] - bounding_box[i]
            elif coordinates[i] + bounding_box[i] > entry.coordinates[i] + entry.bounding_box[i]:
                new[i] = coordinates[i] - bounding_box[i]

        area = area*(bounding_box[0] + new[0])*(bounding_box[1] + new[1])

        return 1.0 - area

    def adjust_tree(self, param, param1):
        pass

    def split_node(self, leaf):
        m = leaf.children.size


    class Node:
        def __init__(self, leaf, coordinates, parent=None, children=LinkedList, bounding_box=None):
            self.leaf = leaf
            self.coordinates = coordinates
            self.parent = parent
            self.children = children
            self.boundingBox = bounding_box

        def __str__(self):
            return str(self.coordinates)

        class Entry:
            def __init__(self, entry=None, coordinates=None):
                self.entry = entry
                self.coordinates = coordinates


class Element:
    def __init__(self, cargo=None, next=None):
        self.cargo = cargo
        self.next = next

    def __str__(self):
        return str(self.cargo)

    def get_data(self):
        return self.cargo

    def get_next(self):
        return self.next

    def set_next(self, new_next):
        self.next = new_next


class LinkedList:
    def __init__(self):
        self.size = 0
        self.head = None

    def add_head(self, cargo):
        node = Element(cargo)
        node.next = self.head
        self.head = node
        self.size = self.size + 1

    def insert(self, data):
        if self.size == 0:
            self.add_head(data)
        else:
            self.size = self.size + 1
            node = Element(data)
            node.next = self.head
            self.head = node
