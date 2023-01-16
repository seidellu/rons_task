#This script solves the task that Ron showed me in a greedy manner or as a baseline in random moves.
#Still I believe the more complex "dynamic programming" method, which solves such problems optimal is superior.
#For this variant we need a recursive approach.
from pathlib import Path
from helper import Node, Transporter, generate_links_from_txt, generate_txt_from_transitions

if __name__ == "__main__":
    print("Start script")
    #prerequisites
    #positions of the nodes with names
    #x,y,name
    nodes = [(5, 10, 1), (50, 5, 2), (40, 20, 3), (60, 35, 4), (30, 35, 5), (20, 30, 6)]
    #path to the transport demand and result path
    path_to_demand = Path(Path.joinpath(Path(__file__).parent), "data/transport_demand.txt")
    path_to_result = Path(Path.joinpath(Path(__file__).parent), "data")
    #generate a dict with each node and it links
    print("Generate the node link map")
    node_dict: dict[int, Node] = generate_links_from_txt(nodes, path_to_demand)


    #----------------solving-----------------------
    print("Init the algo")
    #keep track of the visit nodes
    history = []
    #methode
    methode = "greedy"
    #methode = "random"
    #number of transporter up to 6 possible
    number_of_transporter = 5
    #stores the transporter
    transporter_list:list[Transporter] = []
    #tracks the costs
    overall_costs = 0
    #flag to show transition
    show_transition = False

    #spawn transporter
    for id in range(1,number_of_transporter+1):
        transporter_list.append(Transporter(id, node_dict[id], False))

    print(f"Start moving the transporter in a {methode} manner")
    #let each transporter drive till there are no more links to work on
    while(1):
        for transporter in transporter_list:
            #transporter does a move
            node_dict, transition, step_cost = transporter.evaluate_step(node_dict, methode)
            overall_costs += step_cost
            #if transition is none there are no more links left
            if transition is None:
                break
            else:
                if show_transition:
                    print(transition)
                history.append(transition)
        if transition is None:
            break

    print("No more links are left to work on")
    print(f"""The "{methode}" methode with {number_of_transporter} transporter terminated with costs of: {round(overall_costs, 4)}""")
    print("Export the transitions as txt")
    generate_txt_from_transitions(history, path_to_result, f"num_trans_{number_of_transporter}_methode_{methode}")
    print("End script")
