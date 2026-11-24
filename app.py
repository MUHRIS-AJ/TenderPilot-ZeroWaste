"""Deployable FastAPI frontend for Vercel; localhost CLI remains dependency-free."""
import json
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from core import SERVICES, run
from dashboard import HTML
from transport import SourceError

app = FastAPI(
    title="MUHRIS AI LAB — "+", ".join(SERVICES),
    description="On-demand public data research, rule-based agent stages and source citations. Not autonomous decision-making.",
    version="0.1.0"
)

@app.get("/", response_class=HTMLResponse)
def home():
    """Interactive browser dashboard using the same core workflow as FastMCP."""
    return HTML.replace("__SERVICES__", json.dumps(SERVICES))

@app.get("/health")
def health():
    return {"status":"ok","projects":SERVICES,"data_access":"on-demand; public sources"}

@app.get("/api")
def api(query: str = Query(min_length=2,max_length=120), service: str = ""):
    if service and service not in SERVICES:
        raise HTTPException(status_code=400,detail="Unknown project")
    try:
        return run(query, service or SERVICES[0])
    except ValueError as exc:
        raise HTTPException(status_code=400,detail=str(exc)) from None
    except SourceError as exc:
        raise HTTPException(status_code=502,detail=str(exc)) from None
