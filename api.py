import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from solver import solve_SaOP
from data import dados
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
        # Generate instance data
        # Note: In real scenarios, these could be passed from the frontend.
        # Here we use the function provided.
        P,L,J,T,dem,CapL,CapE,CapF,a,v,LTp,LTj,st,s,h,hf,c,ct,Io,Ij,M = dados(req.p, req.l, req.j, req.t)
        
        # Run optimization
        model, x_vars, y_vars, f_vars, e_cd_vars, e_f_vars = solve_SaOP(
            P,L,J,T,dem,CapL,CapE,CapF,a,v,LTp,LTj,st,s,h,hf,c,ct,Io,Ij,M
        )
        
        if model.status == GRB.OPTIMAL:
            # Extract values from Gurobi tuples into dicts/lists for JSON serialization
            # x[p, l, t]
            x_res = []
            for p in range(P):
                for l in range(L):
                    for t in range(T):
                        val = x_vars[p, l, t].X
                        if val > 1e-5: # Keep it compact
                            x_res.append({"p": p, "l": l, "t": t, "val": val})

            # f[p, j, t]
            f_res = []
            for p in range(P):
                for j in range(J):
                    for t in range(T):
                        val = f_vars[p, j, t].X
                        if val > 1e-5:
                            f_res.append({"p": p, "j": j, "t": t, "val": val})
            
            # e_cd[p, j, t] - Accumulate per CD for charts
            e_cd_res = []
            for p in range(P):
                for j in range(J):
                    for t in range(T):
                        val = e_cd_vars[p, j, t].X
                        # We might need 0 values for plotting over time
                        e_cd_res.append({"p": p, "j": j, "t": t, "val": val})
                        
            # e_f[p, t]
            e_f_res = []
            for p in range(P):
                for t in range(T):
                    val = e_f_vars[p, t].X
                    e_f_res.append({"p": p, "t": t, "val": val})
                    
            # For charts we also need aggregate series directly to simplify frontend logic
            # 1. Total Production at factory per product over time (Sum over L)
            prod_out = []
            for p in range(P):
                for t in range(T):
                    val = sum(x_vars[p, l, t].X for l in range(L))
                    prod_out.append({"p": p, "t": t, "val": val})
            
            # 2. Accumulated CD inventory over time (Sum over J)
            est_cd_agg = []
            for p in range(P):
                for t in range(T):
                    val = sum(e_cd_vars[p, j, t].X for j in range(J))
                    est_cd_agg.append({"p": p, "t": t, "val": val})
                    
            # 3. Flux from factory to CD over time
            # Using f_res (already contains it, but might skip 0s, let's make a complete series for plotting)
            flux_cd = []
            for p in range(P):
                for j in range(J):
                    for t in range(T):
                        val = f_vars[p, j, t].X
                        flux_cd.append({"p": p, "j": j, "t": t, "val": val})

            return {
                "status": "OPTIMAL",
                "objective": model.objVal,
                "metadata": {
                    "P": P, "L": L, "J": J, "T": T
                },
                "results": {
                    "production": x_res,
                    "flux": f_res,
                    "est_cd": e_cd_res,
                    "est_f": e_f_res
                },
                "plots": {
                    "prod_t": prod_out,
                    "est_f_t": e_f_res, # Same as raw result since it's just (p, t)
                    "est_cd_agg_t": est_cd_agg,
                    "flux_cd_t": flux_cd
                }
            }
            
        elif model.status == GRB.INFEASIBLE:
            return {
                "status": "INFEASIBLE",
                "message": "Optimization resulted in INFEASIBLE. Capacity may be insufficient."
            }
        else:
            return {
                "status": "OTHER",
                "message": f"Optimizer stopped with status: {model.status}"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
