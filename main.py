from solver import solve_SaOP
from solver1 import solve_scheduling
from data import dados,generate_data
from gurobipy import GRB
from plot import plot_results

#P,L,J,T,dem,CapL,CapE,CapF,a,v,LTp,LTj,st,s,h,hf,c,ct,Io,Ij,M,st2 = dados(16,2,4,30,0) 
P, L, J, T,dem, CapL, CapE, CapF,a, v, LTp, LTj,st, s,h, hf, c, ct,Io, Ij,M,st2,ch,cf,cma,wl,b = generate_data(4, 3, 2, 24, 42)
print(f"Instância criada com {P} produtos e {T} períodos.")
    
print("\n=== Construindo o Modelo CLSP ===")
    
model, x, y, f, e_cd, e_f, w, F, H = solve_SaOP(P,L,J,T,dem,CapL,CapE,CapF,a,v,LTp,LTj,st,s,h,hf,c,ct,Io,Ij,ch,cf,cma,wl,b,M)

print("\n=== Resolvendo o Modelo CLSP ===")
model.optimize()

seq = {}

if model.status == GRB.OPTIMAL:
    print("Sucesso: Plano Mestre de Produção (CLSP) encontrado!")
    print(f"Custo Total CLSP: {model.objVal:.2f}")

    
    for l in range(L):
        for t in range(T):
            # Identifica quais produtos foram escalonados para esta linha/período
            produtos_ativos = [p for p in range(P) if y[p, l, t].X > 0.5]
            
            if len(produtos_ativos) > 1:
                print(f"\n=== Realizando Scheduling para Linha {l}, Período {t} ===")
                print(f"Produtos a sequenciar: {produtos_ativos}")
                
                
                sequencia = solve_scheduling(produtos_ativos, st2[:, :, l])
                seq[l,t] = [produtos_ativos, sequencia]
            elif len(produtos_ativos) == 1:
                print(f"\nApenas o produto {produtos_ativos[0]} escalonado na Linha {l}, Período {t}. Sem necessidade de sequenciamento.")
            else:
                print(f"\nNenhum produto escalonado na Linha {l}, Período {t}.")

    # Plotar resultados do CLSP
    plot_results(x, y, f, e_cd, e_f, P, L, J, T, w, F, H, seq )

elif model.status == GRB.INFEASIBLE:
    print("\nO Modelo CLSP resultou INFACTÍVEL. Capacidade pode ser insuficiente.")
    model.computeIIS()
    model.write("modelo_infactivel.ilp")
    print("Diagnóstico gravado no arquivo 'modelo_infactivel.ilp'.")
else:
    print(f"\nO Optimizador parou com status: {model.status}")