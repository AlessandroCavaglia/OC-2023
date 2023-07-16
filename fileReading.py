
def load_problem(problem_name):
    with open(problem_name, "r") as file:
        firstLine=file.readline()
        firstLine =firstLine.split("	")
        num_nodes = int(firstLine[1])
        num_arches = int(firstLine[2])
        num_comodities = int(firstLine[3])
        arc_cost = dict()
        single_comodity_capacity = dict()
        supply = dict()
        mutual_capacities = dict()
        start_node = dict()
        end_node = dict()

        values = getValues(file)
        for h in range(num_comodities):
            for i in range(num_arches):
                if (len(values) == 0):
                    values = getValues(file)
                arc_cost[(h, i)] = float(values[0])
                del values[0]
        for h in range(num_comodities):
            for i in range(num_arches):
                if (len(values) == 0):
                    values = getValues(file)
                single_comodity_capacity[(h, i)] = float(values[0])
                del values[0]
        for h in range(num_comodities):
            for i in range(1,num_nodes+1):
                if (len(values) == 0):
                    values = getValues(file)
                supply[(h, i)] = float(values[0])
                del values[0]
        for i in range(num_arches):
            if (len(values) == 0):
                values = getValues(file)
            mutual_capacities[i] = float(values[0])
            del values[0]
        for i in range(num_arches):
            if (len(values) == 0):
                values = getValues(file)
            start_node[i] = int(values[0])
            del values[0]
            end_node[i] = int(values[0])
            del values[0]

        # Check for correct formulation con capacity
        for i in range(num_arches):
            for h in range(num_comodities):
                if (h >= 1):
                    if (single_comodity_capacity[(h, i)] != single_comodity_capacity[h - 1, i]):
                        print("Error, multiple capacities for edge ", i)
        # Check for correct formulation con costs
        for i in range(num_arches):
            for h in range(num_comodities):
                if (h >= 1):
                    if (arc_cost[(h, i)] != arc_cost[h - 1, i]):
                        print("Error, multiple costs for edge ", i)

        for k in range(num_comodities):
            summ=sum(supply[(k, i)] for i in range(1, num_nodes + 1))
            print("SUMM ",k,"  ",summ)
            if(summ!=0):
                print(supply[(k, 1)])
                supply[(k, 1)] = supply[(k, 1)] - summ
                print(supply[(k, 1)])
                new_summ = sum(supply[(k, i)] for i in range(1, num_nodes + 1))
                print("FIXED SUMM", new_summ)



        return convert_problem(num_nodes, num_arches, num_comodities, arc_cost, single_comodity_capacity, supply,
                        mutual_capacities, start_node, end_node)



def convert_problem(num_nodes, num_arches, num_comodities, arc_cost, single_comodity_capacity, supply,
                    mutual_capacities, start_node, end_node):

    nodes_balances = [[None]] #First element skipped since nodes are calculated from 1 to N
    edges = []
    edge_costs = dict()
    edge_capacities = dict()

    node_count = num_nodes
    commodites_count = num_comodities
    for i in range(1, num_nodes + 1):
        print(supply[(0, i)])


    for i in range(1,num_nodes+1):
        balances = []
        for j in range(num_comodities):
            balances.append(-supply[(j, i)])
        nodes_balances.append(balances)

    for i in range(num_arches):
        edge=(start_node[i],end_node[i])
        edges.append(edge)
        edge_costs[edge]=arc_cost[(1,i)]
        edge_capacities[edge]=single_comodity_capacity[(1,i)]

    return (node_count,commodites_count,nodes_balances,edges,edge_costs,edge_capacities)

def getValues(file):
    line = file.readline()
    if (line == '\n'):
        line = file.readline()
    values = line.split("	")
    for idx, val in enumerate(values):
        if (val == ''):
            del values[idx]
        else:
            values[idx] = values[idx].replace("\n", "")
    return values
