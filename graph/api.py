from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from graph import app as forecast_graph

app = FastAPI()


class ForecastRequest(BaseModel):
    target_asset: str
    time_horizon_days: int


@app.get("/health")
def status():
    return {"Server Health": "Up and running"}


@app.post("/forecast")
def forecast(request: ForecastRequest):
    try:
        result = forecast_graph.invoke(request.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "forecast": result.get("forecast", {}),
        "eval_score": result.get("eval_score"),
        "eval_flags": result.get("eval_flags", []),
    }
