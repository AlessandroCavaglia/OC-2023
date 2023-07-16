from pyomo.environ import *
import pyomo.environ as pyo
import fileReading

'''
Node balances = [[value for each comodity] for each node]

edges = [[i,j] for each (i,j) in A ] (i,j) means that the edge goes from i to j
Edge costs = dictionary, edge_cost[[i,j]]=val
Edge capacities = dictionary, edge_capacities[[i,j]]=val
'''


def linear_programming_MCMCF(nodes_balances, edges, edge_costs, edge_capacities, nodes, commodities):
    #print(nodes_balances)
    #print(edge_costs)
    #print(edge_capacities)

    # Parametri
    model = ConcreteModel()
    model.commodities = commodities
    model.nodes_balances = nodes_balances
    model.edges = edges
    model.edge_costs = edge_costs
    model.edge_capacities = edge_capacities
    model.i = set([e[0] for e in edges])
    model.j = set([e[1] for e in edges])

    print(model.i)
    print(model.j)


    # Variabile
    model.x = Var(model.i, model.j, commodities, within=pyo.PositiveReals)

    # Funzione obiettivo
    def obj_rule(model):
        return (sum(model.x[i, j, k] for i in model.i for j in model.j for k in commodities))

    model.obj = Objective(expr=obj_rule(model), sense=minimize)

    # Vincoli
    model.balances_constraint = ConstraintList()
    for k in commodities:
        for n in nodes:
            entering_edges = []
            exiting_edges = []
            for edge in model.edges:
                if edge[0] == n:
                    exiting_edges.append(edge)
                if edge[1] == n:
                    entering_edges.append(edge)

            model.balances_constraint.add(
                (sum(model.x[arch[0], arch[1], k] for arch in entering_edges) - sum(
                    model.x[arch[0], arch[1], k] for arch in exiting_edges)) == (nodes_balances[n][k]))

    model.bundle_constraint = ConstraintList()
    for edge in edges:
        model.balances_constraint.add(
            sum(model.x[edge[0], edge[1], k] for k in commodities) <= model.edge_capacities[edge]
        )

    opt = pyo.SolverFactory('cplex')
    opt.solve(model)
    print_solution(model)


def print_solution(model):
    for k in model.commodities:
        print("--- ", k, "---")
        for edge in model.edges:
            print(edge[0], edge[1], k, "-", str(model.x[edge[0], edge[1], k].value))


    '''for k in model.commodities:
        print("--- ", k, "---")
        for edge in model.edges:
            print(edge[0], edge[1], model.edge_costs[edge],model.edge_capacities[edge])'''


if __name__ == '__main__':
    (node_count, commodites_count, nodes_balances, edges, edge_costs, edge_capacities) = fileReading.load_problem("datasets/minsil19.dat")
    '''
    nodes_balances=[[0 for j in range(COMMODITY_COUNT)] for i in range(NODE_COUNT)]
    nodes_balances[0][0]=-1
    nodes_balances[4][0] = 1

    nodes_balances[1][1] = -1
    nodes_balances[4][1] = 1

    edges=[(0,1),(0,2),(0,3),(3,4),(2,4),(1,4)]
    edge_costs=dict()
    for edge in edges:
        edge_costs[edge]=1
    edge_capacities=dict()
    for edge in edges:
        edge_capacities[edge]=1'''
    linear_programming_MCMCF(nodes_balances,edges,edge_costs,edge_capacities,range(1,node_count+1),range(commodites_count))
