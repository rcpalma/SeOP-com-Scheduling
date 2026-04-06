import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from solver import solve_SaOP
from solver1 import solve_scheduling
from data import generate_data
from gurobipy import GRB

app = FastAPI(title="SaOP Optimization API")

# Allow requests from our React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class OptimizationRequest(BaseModel):
    p: int = Field(3, title="Products (P)")
    l: int = Field(2, title="Lines (L)")
    j: int = Field(4, title="Distribution Centers (J)")
    t: int = Field(12, title="Periods (T)")

@app.post("/solve")
async def solve_model(req: OptimizationRequest):
    try:
        # Generate instance data using generate_data (more complete)
        data_res = generate_data(req.p, req.l, req.j, req.t)
        
        # P, L, J, T, dem, CapL, CapE, CapF, a, v, LTp, LTj, st, s, h, hf, c, ct, Io, Ij, M, st2, ch, cf, cma, wl, b
        P, L, J, T = data_res[0:4]
        dem, CapL, CapE, CapF, a, v, LTp, LTj, st, s, h, hf, c, ct, Io, Ij, M = data_res[4:21]
        st2 = data_res[21]
        ch, cf, cma, wl, b = data_res[22:27]
        
        # 1. Run main optimization (S&OP)
        model, x_vars, y_vars, f_vars, e_cd_vars, e_f_vars, w_vars, F_vars, H_vars = solve_SaOP(
            P, L, J, T, dem, CapL, CapE, CapF, a, v, LTp, LTj, st, s, h, hf, c, ct, Io, Ij, 
            ch, cf, cma, wl, b, M
        )
        
        if model.status == GRB.OPTIMAL:
            # 2. Sequencing (Scheduling) Calculation
            # We determine the sequence only for periods with active production on a line
            sequencing_res = []
            for l in range(L):
                for t in range(T):
                    # Find all products produced in this line and time
                    # Using a small epsilon (0.01) to capture any production
                    P_active = [p for p in range(P) if x_vars[p, l, t].X > 0.01]
                    
                    if len(P_active) == 0:
                        continue
                    elif len(P_active) == 1:
                        sequencing_res.append({"l": l, "t": t, "sequence": [P_active[0]]})
                    else:
                        # Multiple products: Solve TSP for optimal sequence based on st2
                        # Extract the setup cost sub-matrix for the active products in line 'l'
                        st_sub = {}
                        for p1 in P_active:
                            for p2 in P_active:
                                if p1 != p2:
                                    st_sub[p1, p2] = st2[p1, p2, l]
                        
                        seq = solve_scheduling(P_active, st_sub)
                        if seq:
                            sequencing_res.append({"l": l, "t": t, "sequence": seq})
                        else:
                            # Fallback if TSP fails
                            sequencing_res.append({"l": l, "t": t, "sequence": P_active})

            # 3. Extract standard values for frontend
            prod_out = []
            for p in range(P):
                for t in range(T):
                    val = sum(x_vars[p, l, t].X for l in range(L))
                    prod_out.append({"p": p, "t": t, "val": round(val, 2)})

            e_f_res = []
            for p in range(P):
                for t in range(T):
                    val = e_f_vars[p, t].X
                    e_f_res.append({"p": p, "t": t, "val": round(val, 2)})
            
            est_cd_agg = []
            for p in range(P):
                for t in range(T):
                    val = sum(e_cd_vars[p, j, t].X for j in range(J))
                    est_cd_agg.append({"p": p, "t": t, "val": round(val, 2)})
                    
            flux_cd_t = []
            for p in range(P):
                for j in range(J):
                    for t in range(T):
                        val = f_vars[p, j, t].X
                        flux_cd_t.append({"p": p, "j": j, "t": t, "val": round(val, 2)})

            return {
                "status": "OPTIMAL",
                "objective": model.objVal,
                "metadata": { "P": P, "L": L, "J": J, "T": T },
                "plots": {
                    "prod_t": prod_out,
                    "est_f_t": e_f_res,
                    "est_cd_agg_t": est_cd_agg,
                    "flux_cd_t": flux_cd_t,
                    "sequencing": sequencing_res
                }
            }
            
        elif model.status == GRB.INFEASIBLE:
            return { "status": "INFEASIBLE", "message": "Optimization resulted in INFEASIBLE." }
        else:
            return { "status": "OTHER", "message": f"Optimizer status: {model.status}" }
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
