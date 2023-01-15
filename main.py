#This script solves the task which ron showed me in a greedy manor or as baseline in random moves.
#Still i belive the more complex "dynamic programming" methode, which solves such probelms optimal is superior.
#For this variant we need a recursive approach.
from pathlib import Path
from helper import Node, Transporter, generate_links_from_txt, generate_txt_from_transitions

if __name__ == "__main__":
    #positions of the nodes
    nodes = [(5, 10, 1), (50, 5, 2), (40, 20, 3), (60, 35, 4), (30, 35, 5), (20, 30, 6)]
    #path to the transport demand
    path_to_demand = Path(Path.joinpath(Path(__file__).parent), "data/transport_demand.txt")
    path_to_result = Path(Path.joinpath(Path(__file__).parent), "data")
    #generate a dict with each node and it links
    node_dict: dict[int, Node] = generate_links_from_txt(nodes, path_to_demand)


    #----------------solving-----------------------
 
    #keep track of the visit nodes
    history = []
    methode = "greedy"
    number_of_transporter = 2
    transporter_list:list[Transporter] = []

    #spawn transporter
    for id in range(1,number_of_transporter+1):
        transporter_list.append(Transporter(id, node_dict[id], False))


    #go from node to node till there are no links left
    while(1):
        for transporter in transporter_list:
            node_dict, transition = transporter.evaluate_step(node_dict, methode)
            if transition is None:
                break
            else:
                print(transition)
                history.append(transition)
        if transition is None:
            break
    
    print("generate final txt")
    generate_txt_from_transitions(history, path_to_result, f"num_trans_{number_of_transporter}")
