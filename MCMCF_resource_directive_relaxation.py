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


def resource_directive_decomposition(nodes, edges, commodities, arc_cost, single_comodity_capacity, supply, mutual_capacities, start_nodes, end_nodes, r):
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
        return (sum(model.x[edge, k]*(model.edge_costs[(k,edge)]) for edge in model.edges for k in commodities))

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

    model.resource_assignment_constraint=ConstraintList()
    for edge in model.edges:
        for k in model.commodities:
            model.resource_assignment_constraint.add(model.x[edge,k] <= r[edge,k])

    opt = pyo.SolverFactory('cplex')
    opt.options['lpmethod'] = 1
    opt.options['preprocessing presolve'] ='n'
    path = os.path.join('log', str(datetime.today().strftime('Resolution_%d-%m-%y_%H-%M-%S.log')))
    result=opt.solve(model, logfile=path)
    return (model,result)


def print_solution(model):
    for k in model.commodities:
        print("--- ", k, "---")
        for edge in model.edges:
            print(edge, k, "-", str(model.x[edge, k].value))



if __name__ == '__main__':
    THETA=0.1
    MAX_ITER=100

    (num_nodes, num_arches, num_comodities, arc_cost, single_comodity_capacity, supply,mutual_capacities, start_nodes, end_nodes) = fileReading_PPNR.load_problem("datasets/minsil7.dat")
    r = dict()
    for edge in range(num_arches):
        for k in range(num_comodities):
            r[edge,k] = mutual_capacities[edge]/num_comodities
    best_sol=None
    best_value=None
    iter=0
    feasable=False
    while iter<MAX_ITER:
        (model,result) = resource_directive_decomposition([node for node in range(1, num_nodes + 1)], [arch for arch in range(num_arches)], [commodity for commodity in range(num_comodities)], arc_cost, single_comodity_capacity, supply, mutual_capacities, start_nodes, end_nodes, r)
        # Check if solution is feasable
        if (result.solver.status == pyo.SolverStatus.ok) and (result.solver.termination_condition == pyo.TerminationCondition.infeasible):
            print("UNFESABLE")
        else:
            obj_value=pyo.value(model.obj)
            if(best_sol==None or best_value>obj_value):
                best_sol=model
                best_value=obj_value
            #R adjustment
            old_r=r
            for edge in model.edges:
                for k in model.commodities:
                    val=old_r[edge,k] - model.x[edge,k].value
                    if(val<0.0001 and val>=0):
                        decreasing_k=None
                        for dec_k in model.commodities:
                            if(dec_k!=k):
                                val = old_r[edge, dec_k] - model.x[edge, dec_k].value
                                if (val > 0.0001):
                                    decreasing_k=dec_k
                        if(decreasing_k!=None):
                            r[edge,k]+=THETA
                            r[edge,decreasing_k]-=THETA
                            old_r=r
        iter+=1
    print_solution(model)
    for edge in range(num_arches):
        summ = sum(model.x[edge, k].value for k in model.commodities)
        difference = summ - model.mutual_capacities[edge]
        if (difference > 0.00001):
            print("UNFEASABLE EDGE: ",edge," VALUE ",summ-mutual_capacities[edge])
