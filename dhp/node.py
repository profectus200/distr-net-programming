from argparse import ArgumentParser
from threading import Thread
from xmlrpc.client import ServerProxy
from xmlrpc.server import SimpleXMLRPCServer

M = 5
PORT = 1234
RING = [2, 7, 11, 17, 22, 27]


class Node:
    """Represents the node in the network"""

    def __init__(self, node_id):
        """Initializes the node properties and constructs the finger table according to the Chord formula"""

        def successor(id):
            for element in RING:
                if element >= id:
                    return element
            return RING[0]

        self.id = node_id
        self.finger_table = [successor((node_id + 2 ** i) % (2 ** M)) for i in range(M)]
        self.successor = self.finger_table[0]
        self.data_store = {}
        print(f"Node created! Finger table = {self.finger_table}")

    def closest_preceding_node(self, id):
        """Returns node_id of the closest preceeding node (from n.finger_table) for a given id"""
        for i in range(M - 1, -1, -1):
            if self.finger_table[i] != self.id and self.finger_table[i] < id:
                return self.finger_table[i]
        return self.id

    def find_successor(self, id):
        """Recursive function returning the identifier of the node responsible for a given id"""
        if self.id == id:
            return self.id
        if self.id < id <= self.successor:
            return self.successor
        if self.id > self.successor and (self.id < id or id <= self.successor):
            return self.successor

        closest_node = self.closest_preceding_node(id)
        if closest_node == self.id:
            closest_node = self.successor
        print(f'Forwarding request (key={id}) to node {closest_node}')
        with ServerProxy(f'http://node_{closest_node}:{PORT}/') as node:
            return node.find_successor(id)

    def put(self, key, value):
        """Stores the given key-value pair in the node responsible for it"""
        print(f"put({key}, {value})")

        successor_id = self.find_successor(key)
        if successor_id == self.id:
            return self.store_item(key, value)
        else:
            print(f'Forwarding request (key={key}) to node {successor_id}')
            with ServerProxy(f'http://node_{successor_id}:{PORT}/') as node:
                node.store_item(key, value)

    def get(self, key):
        """Gets the value for a given key from the node responsible for it"""
        print(f"get({key})")
        successor_id = self.find_successor(key)
        if self.find_successor(key) == self.id:
            return self.retrieve_item(key)
        else:
            print(f'Forwarding request (key={key}) to node {successor_id}')
            with ServerProxy(f'http://node_{successor_id}:{PORT}/') as node:
                return node.retrieve_item(key)

    def store_item(self, key, value):
        """Stores a key-value pair into the data_store store of this node"""
        if key not in self.data_store:
            self.data_store[key] = value
            return True
        return False

    def retrieve_item(self, key):
        """Retrieves a value for a given key from the data_store store of this node"""
        if key in self.data_store:
            return self.data_store[key]
        return -1


if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument("node_id", help="the ID of the node", type=int)
    args = parser.parse_args()

    node = Node(args.node_id)

    server = SimpleXMLRPCServer(('0.0.0.0', PORT), logRequests=False, allow_none=True)
    server.register_instance(node)

    server_thread = Thread(target=server.serve_forever)
    server_thread.start()
