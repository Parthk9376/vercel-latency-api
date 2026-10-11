
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from starlette.responses import JSONResponse
import math

app = FastAPI()

# Enable CORS for all origins, including preflight requests.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class RequestData(BaseModel):
    regions: List[str]
    threshold_ms: float

# Dataset: latency_ms and uptime_pct for each region.
DATA = {
    "apac": [
        (185.4, 98.89), (112.41, 97.498),
        (183.29, 97.801), (117.96, 97.467),
        (193.12, 98.117), (151.01, 99.359),
        (206.88, 99.469), (146.43, 97.191),
        (133.88, 98.504), (198.52, 97.61),
        (212.06, 98.371), (173.87, 97.394)
    ],
    "emea": [
        (233.48, 99.345), (108.09, 98.325),
        (135.26, 99.176), (112.97, 98.143),
        (162.05, 98.427), (123.12, 97.835),
        (114.57, 97.415), (213.99, 97.294),
        (218.86, 98.356), (155.33, 98.22),
        (156.11, 98.545), (129.47, 98.18)
    ],
    "amer": [
        (134.1, 97.303), (159.3, 99.1),
        (202.39, 97.557), (229.47, 98.046),
        (151.73, 97.828), (163.08, 99.168),
        (147.02, 97.289), (101.61, 99.326),
        (122.22, 98.406), (173.09, 98.396),
        (209.54, 98.652), (167.31, 97.987)
    ]
}

@app.get("/")
def home():
    return {"message": "Latency analytics API is running"}

@app.options("/api/latency")
def latency_options():
    return JSONResponse(
        content={},
        headers={"Access-Control-Allow-Origin": "*",
                 "Access-Control-Allow-Methods": "POST, OPTIONS",
                 "Access-Control-Allow-Headers": "*"}
    )

@app.post("/api/latency")
def analyze(data: RequestData):
    result = {}

    for region in data.regions:
        rows = DATA.get(region, [])

        if not rows:
            result[region] = {
                "avg_latency": 0,
                "p95_latency": 0,
                "avg_uptime": 0,
                "breaches": 0
            }
            continue

        latencies = sorted(row[0] for row in rows)
        uptimes = [row[1] for row in rows]

        result[region] = {
            "avg_latency": sum(latencies) / len(latencies),
            "p95_latency": latencies[
                math.ceil(0.95 * len(latencies)) - 1
            ],
            "avg_uptime": sum(uptimes) / len(uptimes),
            "breaches": sum(
                latency > data.threshold_ms
                for latency in latencies
            )
        }

    return result
