#!/usr/bin/env python3
"""Collective Intelligence MCP Server - Hardened FastAPI + FastMCP"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from fastmcp import FastMCP
from pydantic import BaseModel
import os
import secrets
from datetime import datetime
from typing import List

app = FastAPI(title="Collective Intelligence MCP Server")

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
MCP_API_KEY = os.getenv("MCP_API_KEY", secrets.token_urlsafe(32))

def verify_api_key(api_key: str = Depends(api_key_header)):
    if not api_key or api_key != MCP_API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
    return api_key

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat(), "service": "ci-mcp-server"}

mcp = FastMCP("ci_server", app=app)

class CICalcRequest(BaseModel):
    n_h: int
    diversity: float
    info_density: float
    current_ci: float = 1.0

class DiversityRequest(BaseModel):
    tags: List[str]

class InfoDensityRequest(BaseModel):
    texts: List[str]

class RelayRequest(BaseModel):
    c_n: float
    r_n: float
    s_n: float
    alpha: float = 1.0
    p_n: float = 0.0

@mcp.tool(dependencies=[Depends(verify_api_key)])
async def calculate_ci(request: CICalcRequest):
    """CI_{n+1} = CI_n + 0.15 * (N_h * D * I_d)"""
    eta = 0.15
    new_ci = request.current_ci + eta * (request.n_h * request.diversity * request.info_density)
    return {"new_ci": round(new_ci, 4), "delta": round(new_ci - request.current_ci, 4), "eta": eta}

@mcp.tool(dependencies=[Depends(verify_api_key)])
async def compute_diversity(request: DiversityRequest):
    """Normalized Shannon entropy diversity over categorical tags."""
    from metrics.diversity import normalized_diversity
    d = normalized_diversity(request.tags)
    return {"diversity": round(d, 4)}

@mcp.tool(dependencies=[Depends(verify_api_key)])
async def compute_info_density(request: InfoDensityRequest):
    """Average unique n-gram ratio information density."""
    from metrics.info_density import info_density_score
    i_d = info_density_score(request.texts)
    return {"info_density": round(i_d, 4)}

@mcp.tool(dependencies=[Depends(verify_api_key)])
async def relay_equation(request: RelayRequest):
    """C_{n+1} = alpha * C_n + R_n * (1 - S_n) * (1 + P_n)"""
    result = request.alpha * request.c_n + request.r_n * (1 - request.s_n) * (1 + request.p_n)
    return {"c_next": round(result, 4)}

print(f"MCP Server ready. API Key prefix: {MCP_API_KEY[:8]}...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
