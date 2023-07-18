import os
from datetime import datetime

from pyomo.environ import *
import pyomo.environ as pyo
import fileReading_PPNR

'''
Node balances = [[value for each comodity] for each node]

edges = [[i,j] for each (i,j) in A ] (i,j) means that the edge goes from i to j
Edge costs = dictionary, edge_cost[[i,j]]=val
Edge capacities = dictionary, edge_capacities[[i,j]]=val
Weights = dictionary, weight[[i,j]]=weight
'''


def lagrangian_relaxation(nodes, edges, commodities, arc_cost, single_comodity_capacity, supply,mutual_capacities, start_nodes, end_nodes,weights):
    #print(nodes_balances)
    #print(edge_costs)
    #print(edge_capacities)

    # Parametri
    model = ConcreteModel()
    model.commodities = commodities
    model.nodes_balances = supply
    model.edges = edges
    model.nodes = nodes
    model.edge_costs = arc_cost
    model.start_nodes=start_nodes
    model.end_nodes=end_nodes
    model.edge_capacities = single_comodity_capacity
    model.mutual_capacities=mutual_capacities


    # Variabile
    model.x = Var(model.edges, model.commodities, within=pyo.PositiveReals)


    # Funzione obiettivo
    def obj_rule(model):
        return (sum(model.x[edge, k]*(model.edge_costs[(k,edge)]+weights[edge]) for edge in model.edges for k in commodities))

    model.obj = Objective(expr=obj_rule(model), sense=minimize)

    # Vincoli
    model.balances_constraint = ConstraintList()
    for k in model.commodities:
        for n in model.nodes:
            entering_edges = []
            exiting_edges = []
            for edge in model.edges:
                if start_nodes[edge] == n:
                    exiting_edges.append(edge)
                if end_nodes[edge] == n:
                    entering_edges.append(edge)
            model.balances_constraint.add(
                (sum(model.x[edge, k] for edge in entering_edges) - sum(
                    model.x[edge, k] for edge in exiting_edges)) == model.nodes_balances[(k, n)])

    opt = pyo.SolverFactory('cplex')
    opt.options['lpmethod'] = 1
    opt.options['preprocessing presolve'] ='n'
    path = os.path.join('log', str(datetime.today().strftime('Resolution_%d-%m-%y_%H-%M-%S.log')))
    opt.solve(model, logfile=path)
    return model


def print_solution(model):
    for k in model.commodities:
        print("--- ", k, "---")
        for edge in model.edges:
            print(edge[0], edge[1], k, "-", str(model.x[edge[0], edge[1], k].value))



if __name__ == '__main__':
    THETA=0.0001
    MAX_ITER=50

    (num_nodes, num_arches, num_comodities, arc_cost, single_comodity_capacity, supply,mutual_capacities, start_nodes, end_nodes) = fileReading_PPNR.load_problem("datasets/cinca2.dat")
    weights = dict()
    for edge in range(num_arches):
        weights[edge] = 0

    iter=0
    feasable=False
    while not feasable and iter<MAX_ITER:
        model = lagrangian_relaxation([node for node in range(1,num_nodes+1)], [arch for arch in range(num_arches)], [commodity for commodity in range(num_comodities)], arc_cost, single_comodity_capacity, supply,mutual_capacities, start_nodes, end_nodes, weights)
        # Check if solution is feasable
        feasable=True
        for edge in range(num_arches):
            summ = sum(model.x[edge, k].value for k in model.commodities)
            difference = summ - model.mutual_capacities[edge]
            if (difference > 0.00001):
                feasable=False
        #Weight adjustment
        for edge in  range(num_arches):
            weights[edge] = max(weights[edge] + THETA * (sum(model.x[edge, k].value for k in model.commodities) - mutual_capacities[edge]), 0)
        iter+=1

    print(feasable)
    if(not feasable):
        for edge in range(num_arches):
            summ = sum(model.x[edge, k].value for k in model.commodities)
            difference = summ - model.mutual_capacities[edge]
            if (difference > 0.00001):
                print("UNFEASABLE EDGE: ",edge," VALUE ",summ-mutual_capacities[edge])
