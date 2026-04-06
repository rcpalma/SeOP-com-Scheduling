import numpy as np
import random

def dados(P=2,L=2,J=4,T=30,a1 = 1):
    dem = np.random.randint(50,100,size = (P,J,T))
    CapL = np.random.randint(350000,380000,size=(L,T))
    CapE = np.random.randint(3000000,4000000,size=(J))
    CapF = np.random.randint(45000,50000,size=(P))
    a = np.random.randint(10,100,size=(P,L))
    v = np.random.randint(20,30,size=(P))  
    LTp = np.random.randint(2,4,size=(P))
    LTj = np.random.randint(2,4,size=(J))
    st = np.random.randint(10,100,size=(P,L))
    s = np.random.randint(10,100,size=(P,L))
    h = np.random.randint(30,50,size=(P,J))
    hf = np.random.randint(1000,2000,size=(P))
    c = np.random.randint(10,100,size=(P,L))
    ct = np.random.randint(20,40,size=(P,J,T))
    Io = np.random.randint(500,600,size=(P))
    Ij = np.zeros((P,J))
    
    st2 = np.random.randint(10,20,size=(P,P,L))



    for p in range(P):
        for j in range(J):
            aux = 0
            for t in range(1,LTj[j]):
                aux = aux + dem[p,j,t]
            Ij[p,j] = 4*aux


    M = np.zeros((P,L,T))
    for p in range(P):
        for l in range(L):
            for t in range(T):
                rem_dem = sum(dem[p, j, time] for j in range(J) for time in range(t, T))

                M[p,l,t] = min(rem_dem, CapL[l,t] / a[p,l])

    if a1 == 1:

        return P,L,J,T,dem,CapL,CapE,CapF,a,v,LTp,LTj,st,s,h,hf,c,ct,Io,Ij,M
    else:
        return P,L,J,T,dem,CapL,CapE,CapF,a,v,LTp,LTj,st,s,h,hf,c,ct,Io,Ij,M,st2





def generate_data(P=5, L=3, J=4, T=24, seed=42):
    rng = np.random.default_rng(seed)

    # ── demanda ─────────────────────────────────────────────────
    # escala pequena para não estressar capacidade
    base_demand = rng.integers(50, 150, size=(P, J))
    seasonality = 1 + 0.2 * np.sin(np.linspace(0, 2*np.pi, T))
    dem = np.round(
        base_demand[:, :, None] * seasonality[None, None, :]
        * rng.uniform(0.9, 1.1, size=(P, J, T))
    ).astype(int)
    # dem[p,j,t] — ordem de grandeza: 50-180 unidades por produto/CD/período
    
    # ── lead times ─────────────────────────────────────────────
    LTp = rng.integers(1, 2, size=P)   # 1 ou 2 períodos
    LTj = rng.integers(1, 3, size=J)   # 1 período na maioria

    # ── tempo de produção por unidade ──────────────────────────
    # unidade: minutos. valores pequenos para não estressar capacidade
    a = rng.integers(2, 8, size=(P, L))   # 2-8 min/unidade
    b = rng.uniform(0.1, 0.5, size=(P, L))   # 0.1-0.5 trabalhadores/unidade
    # ── setup ──────────────────────────────────────────────────
    st = rng.integers(20, 60, size=(P, L))   # 20-60 min por setup

    # ── capacidade de linha ─────────────────────────────────────
    # lógica: quanto preciso produzir por período em cada linha?
    # demanda total por período (somando todos os CDs)
    dem_total_pt = dem.sum(axis=1)           # (P, T)
    dem_total_t  = dem_total_pt.sum(axis=0)  # (T,) demanda agregada por período

    # produção necessária por linha assumindo balanceamento uniforme entre linhas
    # tempo necessário = a * quantidade + st * n_setups
    # assumindo 1 setup por produto por período no pior caso
    max_prod_time_needed = (
    a.mean(axis=1)[:, None] * dem_total_pt   # (P,1) * (P,T) → (P,T)
    ).sum(axis=0).max()  

    max_setup_time_needed = st.mean(axis=1).sum() * P   # todos os produtos fazem setup

    # capacidade por linha = (prod + setup) / n_linhas * fator de folga 1.6
    cap_per_line = int((max_prod_time_needed + max_setup_time_needed) / L * 1.6)
    CapL = rng.integers(
        int(cap_per_line * 0.95),
        int(cap_per_line * 1.05),
        size=(L, T)
    )
    # manutenção leve em 2 períodos — reduz só 10%
    maintenance = rng.choice(range(4, T), size=2, replace=False)
    CapL[:, maintenance] = (CapL[:, maintenance] * 0.90).astype(int)

    # ── volume e capacidade de armazém ──────────────────────────
    v = rng.integers(5, 15, size=P)

    # CapE[j]: cabe 4 períodos de demanda média do CD
    avg_dem_j = dem.mean(axis=2)             # (P, J)
    CapE = np.round(
        (avg_dem_j * v[:, None]).sum(axis=0) * 4.0
        * rng.uniform(0.95, 1.05, size=J)
    ).astype(int)

    aux = sum(
    dem[p, j, :LTj[j] + 1].sum() for p in range(P) for j in range(J))

    # CapF[p]: cabe 4 períodos de produção média
    avg_prod_p = dem_total_pt.mean(axis=1)   # (P,)
    CapF = np.round(avg_prod_p * 20 * aux * rng.uniform(0.95, 1.05, size=P)).astype(int)

    # ── estoques iniciais ───────────────────────────────────────
    # fábrica: cobre (max LTp) períodos de demanda total para cada produto
    max_LTp = LTp.max()
    Io = np.round(
        dem_total_pt[:, :max_LTp].sum(axis=1)     # demanda total nos primeiros LTp períodos
        * rng.uniform(1.2, 1.5, size=P)            # folga de 20-50%
    ).astype(int)

    # CDs: cobre (max LTj) períodos de demanda local
    max_LTj = LTj.max()
    Ij = np.round(
        dem[:, :, :max_LTj].sum(axis=2)           # (P, J) demanda nos primeiros LTj períodos
        * rng.uniform(1.2, 1.5, size=(P, J))
    ).astype(int)

    aux2 = sum( dem[p, j, 0].sum() for p in range(P) for j in range(J))

    wl = np.round(rng.uniform(0.75 * 0.5 * aux2 / L, 0.5 * aux2 / L, size=L)).astype(int)

    # ── custos ─────────────────────────────────────────────────
    complexity = rng.uniform(0.5, 2.0, size=P)

    c  = np.round(complexity[:, None] * rng.uniform(10, 50, size=(P, L))).astype(int)
    s  = np.round(st * rng.uniform(1, 3, size=(P, L))).astype(int)
    h  = np.round(c.min(axis=1)[:, None] * rng.uniform(1, 3, size=(P, J))).astype(int)
    hf = np.round(c.min(axis=1) * rng.uniform(10, 30, size=P)).astype(int)
    ct = np.round(rng.uniform(5, 20, size=(P, J, T))).astype(int)
    ch  = np.round(rng.uniform(50, 100, size=(L, T))).astype(int)
    cf  = np.round(rng.uniform(20, 60, size=(L, T))).astype(int)
    cma  = np.round(rng.uniform(10, 50, size=(L, T))).astype(int)



    # setup dependente de sequência
    family = rng.integers(0, 3, size=P)
    st2 = np.zeros((P, P, L), dtype=int)
    s2  = np.zeros((P, P, L), dtype=int)
    for p1 in range(P):
        for p2 in range(P):
            if p1 == p2:
                continue
            factor = 0.6 if family[p1] == family[p2] else 1.0
            st2[p1, p2, :] = np.round(
                rng.integers(15, 50) * factor * rng.uniform(0.9, 1.1, size=L)
            )
            s2[p1, p2, :] = np.round(st2[p1, p2, :] * rng.uniform(50, 100, size=L))

    M = np.zeros((P,L,T))
    for p in range(P):
        for l in range(L):
            for t in range(T):
                rem_dem = sum(dem[p, j, time] for j in range(J) for time in range(t, T))

                M[p,l,t] = min(rem_dem, CapL[l,t] / a[p,l])


    return P, L, J, T,dem, CapL, CapE, CapF,a, v, LTp, LTj,st, s,h, hf, c, ct,Io, Ij,M,st2,ch,cf,cma,wl,b