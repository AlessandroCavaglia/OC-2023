import re

def load_problem(problem_name):
    with open(problem_name, "r") as file:
        firstLine = file.readline()
        firstLine=re.split("[ ]{2,}",firstLine)
        num_comodities = int(firstLine[1])
        num_nodes = int(firstLine[3])
        num_arches = int(firstLine[2])
        arc_cost = dict()
        single_comodity_capacity = dict()
        supply = dict()
        mutual_capacities = dict()
        start_nodes = dict()
        end_nodes = dict()
        fixed_charge_cost=dict()
        for i in range(num_arches):
            values = getValues(file)
            end_nodes[i]=int(values[0])
            start_nodes[i]=int(values[1])
            fixed_charge_cost[i]=float(values[2])
            mutual_capacities[i]=float(values[3])
            pk=int(values[4])
            for j in range(pk):
                values = getValues(file)
                h=int(values[0])
                arc_cost[(h,i)]=float(values[1])
                single_comodity_capacity[(h,i)]=float(values[2])

        try:
            while True:
                values = getValues(file)
                h=int(values[0])
                i=int(values[1])
                supply[(i,h)]=float(values[2])
        except:
            print("")

        for k in range(1,num_comodities+1):
            for n in range(1, num_nodes + 1):
                if not ((k,n) in supply.keys()):
                    supply[(k,n)]=0
        summ = 0
        for key in supply.keys():
            if(key[0]==1):
                summ+=supply[key]
        print(summ)

        for k in range(1,num_comodities+1):
            summ = sum(supply[(k, i)] for i in range(1, num_nodes + 1))
            print("SUMM ",k,"  ",summ)
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
    values=re.split("[ ]{2,}",line)
    for idx, val in enumerate(values):
        if (val == ''):
            del values[idx]
        else:
            values[idx] = values[idx].replace("\n", "")
    return values

def getFirstElem(values,file):
    if (len(values) == 0):
        values=getValues(file)
    val=values[0]
    del values[0]
    return val