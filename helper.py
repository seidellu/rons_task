from __future__ import annotations
from queue import PriorityQueue
from pathlib import Path
from os.path import exists
from os import strerror
from errno import ENOENT
from typing import Union, Tuple
import numpy as np
import pandas as pd
import random
from dataclasses import dataclass

@dataclass
class Transition():
    fzg_id: int
    node_id: int
    unloaded: int
    loaded: int

    def __init__(self, fzg_id: int, node_name: int, unloaded: bool, loaded: bool) -> None:
        self.fzg_id = fzg_id
        self.node_id = node_name
        self.unloaded = int(unloaded)
        self.loaded = int(loaded)

    def __str__(self):
        return f"{self.fzg_id},{self.node_id},{self.unloaded},{self.loaded}\n"

class WrongLink(Exception):
    def __init__(self, msg="Tried to add wrong link you idiot."):
        self.msg = msg
        super().__init__(self.msg)


class Node:
    def __init__(self, x_pos: int, y_pos: int, name: int) -> None:
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.name = name
        self.number_of_links = 0
        self.unfinshed_links_prio_queue = PriorityQueue()
        self.unfinshed_links_list = []
        self.finished_links = []
    
    def add_link(self, link: Link)->None:
        """Add a link the the link list of the node. 

        Args:
            link (link): link between two nodes
        """
        if(link.start_node.name != self.name):
            raise WrongLink
        self.unfinshed_links_prio_queue.put(link)
        self.unfinshed_links_list.append(link)
        self.number_of_links += 1

    def get_greedy_link(self) -> Union[Link, None]:
        """Pops the link with the lowest costs.

        Returns:
            link: link between two nodes
        """
        if self.number_of_links == 0:
            return None
        else:
            self.number_of_links -= 1
            return self.unfinshed_links_prio_queue.get()
    
    def get_random_link(self) -> Union[Link, None]:
        """Pops a random link.
        Returns:
            link: link between two nodes
        """
        if self.number_of_links == 0:
            return None
        else:
            self.number_of_links -= 1
            return self.unfinshed_links_list.pop(random.randint(0,len(self.unfinshed_links_list)-1))

class Link:
    def __init__(self, start_node: Node, end_node: Node) -> None:
        self.start_node = start_node
        self.end_node = end_node
        self.costs = self._compute_costs(start_node, end_node)

    def __str__(self) -> str:
        return f"Link from {self.start_node.name} to {self.end_node.name} with cost {self.costs}"

    def __lt__(self, link: Link) -> bool:
        return self.costs < link.costs

    def __eq__(self, link: Link) -> bool:
        return self.costs == link.costs

    def __gt__(self, link: Link) -> bool:
        return self.costs > link.costs

    def _compute_costs(self, node1: Node, node2: Node) -> float:
        """Computes the cost between two nodes. Costs are the euclidian distance between two nodes.

        Args:
            node1 (node): starting node
            node2 (node): ending node

        Returns:
            float: costs
        """
        return np.sqrt(np.power(node1.x_pos-node2.x_pos,2)+np.power(node1.y_pos-node2.y_pos, 2))

    @classmethod
    def compute_costs(cls, node1: Node, node2: Node) -> float:
        """Computes the cost between two nodes. Costs are the euclidian distance between two nodes.

        Args:
            node1 (node): starting node
            node2 (node): ending node

        Returns:
            float: costs
        """
        return np.sqrt(np.power(node1.x_pos-node2.x_pos,2)+np.power(node1.y_pos-node2.y_pos, 2))


class Transporter:

    def __init__(self, id: int, start_node: Node, loaded: bool) -> None:
        self.id = id
        self.current_node = start_node
        self.loaded = loaded

    def evaluate_step(self, node_dict: dict[int, Node], methode: str) -> Union[Tuple[dict, None], Tuple[dict, Transition]]:
        """Performs either one random or greedy step in his current position.

        Args:
            node_dict (dict[int, Node]): node dict which holds the nodes and thier attributes
            methode (str): used methode either "greedy" or "random"

        Returns:
            Union[Tuple[dict, None], Tuple[dict, Transition]]: return the manipulated nodes_dict and the made transition or if no transition is left nodes_dict and None
        """
        #if the transporter is currenty loaded it will unloade its package
        if self.loaded:
            unloaded = True
        else:
            unloaded = False
        #check if a package can be loaded
        if self.current_node.number_of_links != 0:
            self.loaded = True
            #get next node
            if methode == "greedy":
                next_link = self.current_node.get_greedy_link()
            else:
                next_link = self.current_node.get_random_link()
            next_node = node_dict[next_link.end_node.name]
        else:
            #current node has no remaining links
            #transporter could not be loaded
            self.loaded = False
            #get nodes which have links left
            nodes_with_links = [node for name, node in node_dict.items() if node.number_of_links > 0]
            #terminate if there are no nodes with links left
            if len(nodes_with_links) == 0:
                return node_dict, None
            #if greedy choose the nearest node which has links left
            if methode=="greedy":
                #get nearest node
                best_value = 999999
                for node_with_link in nodes_with_links:
                    current_cost = Link.compute_costs(self.current_node, node_with_link)
                    if current_cost < best_value:
                        next_node = node_dict[node_with_link.name]
                        best_value = current_cost
            else:
                #if random choose a random node to go to
                next_node = node_dict[nodes_with_links[random.randint(0, len(nodes_with_links)-1)].name]
        #generate transition
        trans = Transition(self.id, self.current_node.name, unloaded, self.loaded)
        #update node
        self.current_node = next_node
        return node_dict, trans

def generate_links_from_txt(nodes: list, path: Path) -> dict:
    """Generates for a given list of nodes and a path to a transport_demand.txt a dict of nodes 
    with their corresponding links.

    Args:
        nodes (list): list of nodes
        path (Path): path to the transport demand

    Raises:
        FileNotFoundError: raised if the transport demand file does not exists

    Returns:
        dict: dict containing nodes with link queues/lists
    """
    node_dict: dict[int, Node] = {}
    #generate nodes for the list of nodes based on thier position and name
    for node_def in nodes:
        node_dict.update({node_def[2]: Node(node_def[0], node_def[1], node_def[2])})
    #check if path is valid
    if exists(str(path)):
        transport_demand = pd.read_csv(path, header=0)
    else:
        raise FileNotFoundError(
            ENOENT, strerror(ENOENT), str(path))
    #generate the links for each nodes based on the transport_demand
    for _, row in transport_demand.iterrows():
        #number of packages per link
        for pkg in range(row[2]):
            node_dict[row[0]].add_link(Link(node_dict[row[0]], node_dict[row[1]]))
    return node_dict

def generate_txt_from_transitions(transitions: list[Transition], path: Path, name: str) -> None:
    """Generates for the given path a txt with the history of all transitions.

    Args:
        transitions (list[Transition]): hirstory of al transitions.
        path (Path): path to the txt
        name (str) : name of the file
    """
    with open(Path.joinpath(path, f"result_{name}.txt"), "w") as file:
        for transition in transitions:
            file.write(str(transition))
    


if __name__ == "__main__":
    #testing node and links definition
    n1 = Node(5, 10, 1)
    n2 = Node(50, 5, 2)
    n3 = Node(40, 20, 3)

    print("greedy link extraction")
    n1.add_link(Link(n1, n2))
    n1.add_link(Link(n1, n2))
    n1.add_link(Link(n1, n3))
    n1.add_link(Link(n1, n2))

    for i_l in range(0, 4):
        print(n1.get_greedy_link())

    print("random link extraction")
    n1.add_link(Link(n1, n2))
    n1.add_link(Link(n1, n2))
    n1.add_link(Link(n1, n3))
    n1.add_link(Link(n1, n2))

    for i_l in range(0, 4):
        print(n1.get_random_link())