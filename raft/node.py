import random
import sched
import time
from argparse import ArgumentParser
from enum import Enum
from http.client import HTTPConnection
from threading import Thread
from xmlrpc.client import ServerProxy, Transport
from xmlrpc.server import SimpleXMLRPCServer

'''
I've changed the election timeout in my implementation because of waiting
for dead server issues, so please make client to wait 15 seconds before the start.
'''


PORT = 1234
CLUSTER = [1, 2, 3]
ELECTION_TIMEOUT = (12, 15)
HEARTBEAT_INTERVAL = 5


class NodeState(Enum):
    """Enumerates the three possible node states (follower, candidate, or leader)"""
    FOLLOWER = 1
    CANDIDATE = 2
    LEADER = 3


class Node:
    def __init__(self, node_id):
        """Non-blocking procedure to initialize all node parameters and start the first election timer"""
        self.node_id = node_id
        self.state = NodeState.FOLLOWER
        self.term = 0
        self.votes = {}
        self.log = []
        self.pending_entry = ''
        self.append_try = False
        self.voted_for = {}
        self.sched = sched.scheduler(time.time, time.sleep)
        self.reset_election_timer()
        print(f"Node started! State: {self.state}. Term: {self.term}")

        def run_scheduler():
            self.sched.run()

        Thread(target=run_scheduler).start()

    def is_leader(self):
        """Returns True if this node is the elected cluster leader and False otherwise"""
        return self.state == NodeState.LEADER

    def reset_election_timer(self):
        """Resets election timer for this (follower or candidate) node and returns it to the follower state"""
        for event in self.sched.queue:
            self.sched.cancel(event)
        self.sched.enter(random.uniform(*ELECTION_TIMEOUT), 2, self.hold_election)
        self.state = NodeState.FOLLOWER

    def reset_heartbeat_timer(self):
        """Resets heartbeat timer for this node and makes it the leader"""
        for event in self.sched.queue:
            self.sched.cancel(event)
        self.sched.enter(HEARTBEAT_INTERVAL, 1, self.append_entries)
        self.state = NodeState.LEADER

    def hold_election(self):
        """Called when this follower node is done waiting for a message from a leader (election timeout)
            The node increments term number, becomes a candidate and votes for itself.
            Then call request_vote over RPC for all other online nodes and collects their votes.
            If the node gets the majority of votes, it becomes a leader and starts the hearbeat timer
            If the node loses the election, it returns to the follower state and resets election timer.
        """
        self.term += 1
        self.votes = {self.node_id: True}
        self.voted_for[self.term] = self.node_id
        self.state = NodeState.CANDIDATE

        print(f"New election term {self.term}. State: {self.state}")
        time.sleep(0.1)

        def send_request(follower_id):
            try:
                with ServerProxy(f'http://node_{follower_id}:{PORT}', transport=TimeoutTransport()) as remote_node:
                    answer = remote_node.request_vote(self.term, self.node_id)
                    self.votes[follower_id] = answer
            except:
                print(f"Follower node {follower_id} is offline")
                self.votes[follower_id] = False

        threads = []
        for node_id in CLUSTER:
            if node_id != self.node_id:
                threads.append(Thread(target=send_request, args=(node_id,)))

        [t.start() for t in threads]
        [t.join() for t in threads]

        num_votes = sum(self.votes.values())
        if num_votes > len(CLUSTER) // 2:
            self.state = NodeState.LEADER
            print(f"Received {num_votes}. State: Leader")
            self.reset_heartbeat_timer()
        else:
            print(f"Received {num_votes}. State: Follower")
            self.reset_election_timer()

    def request_vote(self, term, candidate_id):
        """Called remotely when a node requests voting from other nodes.
            Updates the term number if the received one is greater than `self.term`
            A node rejects the vote request if it's a leader or it already voted in this term.
            Returns True and update `self.votes` if the vote is granted to the requester candidate and False otherwise.
        """
        print(f"Got a vote request from {candidate_id}")

        if term > self.term:
            self.term = term

        if self.state == NodeState.LEADER:
            print(f"Didn't vote for {candidate_id} (I'm a leader)")
            return False
        if self.voted_for.get(term) is not None and self.voted_for.get(term) != candidate_id:
            print(f"Didn't vote for {candidate_id} (already voted for {self.voted_for.get(term)})")
            return False

        self.voted_for[term] = candidate_id
        self.reset_election_timer()

        return True

    def append_entries(self):
        """Called by leader every HEARTBEAT_INTERVAL, sends a heartbeat message over RPC to all online followers.
            Accumulates ACKs from followers for a pending log entry (if any)
            If the majority of followers ACKed the entry, the entry is committed to the log and is no longer pending
        """
        print("Sending a heartbeat to followers")
        time.sleep(0.1)

        def send_heartbeat(follower_id):
            try:
                with ServerProxy(f'http://node_{follower_id}:{PORT}', transport=TimeoutTransport()) as remote_node:
                    answer = remote_node.heartbeat(self.pending_entry)
                    self.votes[follower_id] = answer
            except:
                print(f"Follower node {follower_id} is offline")
                self.votes[follower_id] = False

        self.votes = {self.node_id: True}
        threads = []
        for node_id in CLUSTER:
            if node_id != self.node_id:
                threads.append(Thread(target=send_heartbeat, args=(node_id,)))

        [t.start() for t in threads]
        [t.join() for t in threads]

        self.reset_heartbeat_timer()
        num_votes = sum(self.votes.values())
        if num_votes > len(CLUSTER) // 2:
            if self.pending_entry != '':
                self.log.append(self.pending_entry)
                print(f"Leader committed '{self.pending_entry}'")
                self.pending_entry = ''
            self.append_try = True
            return True
        else:
            self.append_try = True
            return False

    def heartbeat(self, leader_entry):
        """Called remotely from the leader to inform followers that it's alive and supply any pending log entry
            Followers would commit an entry if it was pending before, but is no longer now.
            Returns True to ACK the heartbeat and False on any problems.
        """
        print(f"Heartbeat received from leader (entry='{leader_entry}')")
        if self.state != NodeState.LEADER:
            self.reset_election_timer()
            if self.pending_entry != '':
                self.log.append(self.pending_entry)
                print(f"Follower committed '{self.pending_entry}'")
            self.pending_entry = leader_entry
            return True
        else:
            return False

    def leader_receive_log(self, log):
        """Called remotely from the client. Executed only by the leader upon receiving a new log entry
            Returns True after the entry is committed to the leader log and False on any problems
        """
        print(f"Leader received log '{log}' from client")

        if self.state == NodeState.LEADER:
            self.pending_entry = log
            self.append_try = False
            while not self.append_try:
                time.sleep(0.5)
            return self.pending_entry == ''
        else:
            return False


class TimeoutTransport(Transport):
    def _create_connection(self, host, timeout=1):
        # Set timeout on socket before creating connection
        if timeout is not None:
            self.timeout = timeout
        conn = HTTPConnection(host, timeout=self.timeout)
        return conn


if __name__ == '__main__':
    # Parse one integer argument (node_id), then create the node with that ID.
    parser = ArgumentParser(description='RAFT Node')
    parser.add_argument('node_id', type=int, help='Unique ID of the node')
    args = parser.parse_args()

    node = Node(args.node_id)

    server = SimpleXMLRPCServer(('0.0.0.0', PORT), logRequests=False, allow_none=True)
    server.register_instance(node)

    try:
        server_thread = Thread(target=server.serve_forever)
        server_thread.start()
    except KeyboardInterrupt:
        print("Interrupted! Exiting...")
