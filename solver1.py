import gurobipy as gp
from gurobipy import GRB

def solve_scheduling(P, st):

    n = len(P)
    if n == 0:
        print("Nenhum produto para sequenciar.")
        return None
    if n == 1:
        print(f"Apenas um produto ({P}), sequenciamento trivial.")
        return [P]

    model = gp.Model("Scheduling")
    model.setParam('OutputFlag', 0) 

    # Variáveis de decisão para a sequência (índices locais 0..n-1)
    delta = model.addVars(P, P, vtype=GRB.BINARY, name="delta")
    d_in = model.addVars(P, vtype=GRB.BINARY, name="d_in")
    d_out = model.addVars(P, vtype=GRB.BINARY, name="d_out")
    v = model.addVars(P, lb=1, ub=n+1, vtype=GRB.INTEGER, name="v")


    model.addConstrs(
        (gp.quicksum(delta[p,p1]  for p in P if p!=p1) + d_in[p1] ==1 for p1 in P),
        name = "antecessor"
    )
    
    model.addConstrs(
        (gp.quicksum( delta[p1,p] for p in P if p!=p1 ) + d_out[p1] ==1    for p1 in P ),
        name = "sucessor"
    )    

    model.addConstr(
        (gp.quicksum(d_in[p] for p in P) == 1 ),
        name = "primeiro_prod"
    )

    model.addConstr(
        (gp.quicksum(d_out[p] for p in P) == 1 ),
        name = "ultimo_prod"
    )

    model.addConstrs(
        (v[p] >= v[p1] + 1 - n*(1- delta[p1,p]) for p in P for p1 in P if p!=p1),
        name = "MTZ subtour elimination"
    )

    # Função Objetivo: Minimizar custos de setup de transição
    obj = gp.quicksum(st[p, p1] * delta[p, p1] for p in P for p1 in P if p != p1)
    model.setObjective(obj, GRB.MINIMIZE)

    model.optimize()

    if model.status == GRB.OPTIMAL:
        # Extrair a sequência a partir das variáveis d_in e delta
        sequence = []
        # Achar o primeiro
        atual = -1
        for p in P:
            if d_in[p].X > 0.5:
                atual = p
                break
        
        while atual != -1:
            sequence.append(atual)
            # Achar o próximo
            proximo = -1
            for j in P:
                if atual != j and delta[atual, j].X > 0.5:
                    proximo = j
                    break
            atual = proximo
        

        print(f"Sequência Ótima: {sequence}")
        print(f"Custo de Setup: {model.objVal:.2f}")
        return sequence
    else:
        print("Não foi possível encontrar uma sequência ótima.")
        return None