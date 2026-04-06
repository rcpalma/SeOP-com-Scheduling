import gurobipy as gp
from gurobipy import GRB

def solve_SaOP(P,L,J,T,dem,CapL,CapE,CapF,a,v,LTp,LTj,st,s,h,hf,c,ct,Io,Ij,ch,cf,cma,wl,b,M):


    model  = gp.Model("SaOP")

    x = model.addVars(P,L,T,lb = 0.0,vtype = GRB.CONTINUOUS,name = 'x')
    y = model.addVars(P,L,T,vtype = GRB.BINARY, name = 'y')
    f = model.addVars(P,J,T,lb = 0.0,vtype = GRB.CONTINUOUS, name = 'f')
    e_cd = model.addVars(P,J,T,lb = 0.0,vtype = GRB.CONTINUOUS, name = 'e_cd')
    e_f = model.addVars(P,T,lb = 0.0,vtype = GRB.CONTINUOUS, name = 'e_f')
    w = model.addVars(L,T,lb = 0.0, vtype = GRB.INTEGER, name = "w")
    H = model.addVars(L,T,lb = 0.0, vtype = GRB.INTEGER, name = "H")
    F = model.addVars(L,T,lb = 0.0, vtype = GRB.INTEGER, name = "F")

    model.addConstrs(
        (gp.quicksum(f[p,j,t] for j in range(J)) <= e_f[p,t] for p in range(P) for t in range(T)),
        name = "fluxo_fabrica_cd"
    )


    model.addConstrs(
        (e_f[p,t] == e_f[p,t-1] + gp.quicksum(x[p,l,t-LTp[p]] for l in range(L)) - gp.quicksum(f[p,j,t] for j in range(J)) for p in range(P) for t in range(LTp[p],T)),
        name = "conservacao_estoque_fab"
    )
    model.addConstrs(
        (e_f[p,t] == e_f[p,t-1] - gp.quicksum(f[p,j,t] for j in range(J)) for p in range(P) for t in range(1,LTp[p])),
        name = "conservacao_estoque_fab2"
    )

    model.addConstrs(   
        (e_cd[p,j,t] == e_cd[p,j,t-1] - dem[p,j,t] + f[p,j,t-LTj[j]] 
        for j in range(J) for p in range(P) for t in range(LTj[j], T)),
        name="conservacao_estoque_cd"
    )
    
    model.addConstrs(
        (e_cd[p,j,t] == e_cd[p,j,t-1] - dem[p,j,t] 
        for j in range(J) for p in range(P) for t in range(1,LTj[j])),
        name="conservacao_estoque_cd2"
    )

    model.addConstrs(
        (e_cd[p,j,0] == Ij[p,j] for j in range(J) for p in range(P)),
        name="estoque_inicial_cd2"
    )

    model.addConstrs(
        (e_f[p,0] == Io[p] for p in range(P)),
        name="estoque_inicial_fab2"
    )

    model.addConstrs(
        (gp.quicksum(a[p,l]*x[p,l,t] + st[p,l]*y[p,l,t] for p in range(P)) <= CapL[l,t] for l in range(L) for t in range(T)),
        name = "capac_fabrica_linha"
    )

    model.addConstrs(
        (gp.quicksum(v[p] * e_cd[p,j,t] for p in range(P)) <= CapE[j] for j in range(J) for t in range(T)),
        name = "capac_CD"
    )

    model.addConstrs(
        x[p,l,t] <= M[p,l,t] * y[p,l,t] for p in range(P) for l in range(L) for t in range(T)
    )

    model.addConstrs(
        (v[p] * e_f[p,t] <= CapF[p] for p in range(P) for t in range(T)),
        name = "capac_fabrica"
    )

    model.addConstrs(
        (w[l,t] == w[l,t-1] + H[l,t] - F[l,t] for l in range(L) for t in range(1,T)),
        name = "cons_func"
    )

    model.addConstrs(
        (w[l,0] == wl[l] for l in range(L) ),
        name = "esto_inicial_trabal"
    )

    model.addConstrs(
        (gp.quicksum(b[p,l] * x[p,l,t] for p in range(P) ) <= w[l,t] for l in range(L) for t in range(T)),
        name = "lim_trabalhadores"
    )

    total_cost = gp.quicksum(ct[p,j,t] * f[p,j,t] + c[p,l] * x[p,l,t] + s[p,l] * y[p,l,t] + 
    h[p,j] * e_cd[p,j,t] + hf[p] * e_f[p,t] + ch[l,t] * H[l,t] + cf[l,t] * F[l,t] + cma[l,t] * w[l,t] for p in range(P) for l in range(L) for j in range(J) for t in range(T))

    model.setObjective(total_cost, GRB.MINIMIZE)

    model.optimize()

    if model.status == GRB.OPTIMAL:
        print("Optimal solution found!")
        print("Objective value:", model.objVal)
    else:
        print("No optimal solution found.")

    return model, x, y, f, e_cd, e_f,w,F,H