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
'''


def linear_programming_MCMCF(nodes, edges, commodities, arc_cost, single_comodity_capacity, supply,mutual_capacities, start_nodes, end_nodes):
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
        return (sum(model.x[edge, k]*model.edge_costs[(k,edge)] for edge in model.edges for k in commodities))

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

    model.bundle_constraint = ConstraintList()
    for edge in edges:
        model.balances_constraint.add(
            sum(model.x[edge, k] for k in commodities) <= model.mutual_capacities[edge]
        )

    opt = pyo.SolverFactory('cplex')
    opt.options['lpmethod'] = 1
    opt.options['preprocessing presolve'] ='n'
    path = os.path.join('log', str(datetime.today().strftime('Resolution_%d-%m-%y_%H-%M-%S.log')))
    opt.solve(model, logfile=path)
    print_solution(model)


def print_solution(model):
    for k in model.commodities:
        print("--- ", k, "---")
        for edge in model.edges:
            print(model.start_nodes[edge], model.end_nodes[edge], k, "-", str(model.x[edge, k].value))

    for edge in model.edges:
        summ = sum(model.x[edge, k].value for k in model.commodities)
        difference =summ - model.mutual_capacities[edge]
        if (difference > 0.00001):
            print("UNFEASABLE EDGE: ", edge, " VALUE ", summ - model.edge_capacities[0,edge])

    for k in model.commodities:
        for n in model.nodes:
            entering_edges = []
            exiting_edges = []
            for edge in model.edges:
                if start_nodes[edge] == n:
                    exiting_edges.append(edge)
                if end_nodes[edge] == n:
                    entering_edges.append(edge)
            difference = (sum(model.x[edge, k].value for edge in entering_edges) - sum(
                model.x[edge, k].value for edge in exiting_edges)) - model.nodes_balances[(k, n)]
            if (abs(difference) > 0.00001):
                print("BALANCES NOT HANDLED CORRECTLY FOR NODE ",n,"AND COMMODITY ",k," WITH ERROR OF: ",abs(difference))



if __name__ == '__main__':
    (num_nodes, num_arches, num_comodities, arc_cost, single_comodity_capacity, supply,mutual_capacities, start_nodes, end_nodes) = fileReading_PPNR.load_problem("datasets/minsil7.dat")
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
    linear_programming_MCMCF([node for node in range(1,num_nodes+1)], [arch for arch in range(num_arches)], [commodity for commodity in range(num_comodities)], arc_cost, single_comodity_capacity, supply,mutual_capacities, start_nodes, end_nodes)
