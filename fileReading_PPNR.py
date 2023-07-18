import random


def load_problem(problem_name):
    with open(problem_name, "r") as file:
        firstLine = file.readline()
        firstLine = firstLine.split("	")
        num_nodes = int(firstLine[1])
        num_arches = int(firstLine[2])
        num_comodities = int(firstLine[3])
        arc_cost = dict()
        single_comodity_capacity = dict()
        supply = dict()
        mutual_capacities = dict()
        start_nodes = dict()
        end_nodes = dict()

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
            for i in range(1, num_nodes + 1):
                if (len(values) == 0):
                    values = getValues(file)
                supply[(h, i)] = -float(values[0])
                del values[0]
        for i in range(num_arches):
            if (len(values) == 0):
                values = getValues(file)
            mutual_capacities[i] = float(values[0])-1
            del values[0]
        for i in range(num_arches):
            if (len(values) == 0):
                values = getValues(file)
            start_nodes[i] = int(values[0])
            del values[0]
            end_nodes[i] = int(values[0])
            del values[0]

        ''' Check for correct formulation con capacity
        for i in range(num_arches):
            for h in range(num_comodities):
                if (h >= 1):
                    if (single_comodity_capacity[(h, i)] != single_comodity_capacity[h - 1, i]):
                        #print("Error, multiple capacities for edge ", i)'''
        ''' Check for correct formulation con costs
        for i in range(num_arches):
            for h in range(num_comodities):
                if (h >= 1):
                    if (arc_cost[(h, i)] != arc_cost[h - 1, i]):
                        print("Error, multiple costs for edge ", i)'''

        for k in range(num_comodities):
            summ = sum(supply[(k, i)] for i in range(1, num_nodes + 1))
            # print("SUMM ",k,"  ",summ)
            if (summ != 0):
                # print(supply[(k, 1)])
                supply[(k, 1)] = supply[(k, 1)] - summ
                # print(supply[(k, 1)])
                new_summ = sum(supply[(k, i)] for i in range(1, num_nodes + 1))
                # print("FIXED SUMM", new_summ)

        return (num_nodes, num_arches, num_comodities, arc_cost, single_comodity_capacity, supply, mutual_capacities,
                start_nodes, end_nodes)


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
