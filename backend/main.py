from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import traffic, simple_traffic, graph_traffic

app = FastAPI(
    title="AI Traffic Congestion Prediction & Action Simulator",
    description="Backend API for traffic simulation, prediction, and optimization",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(traffic.router, prefix="/api/traffic", tags=["traffic"])
app.include_router(simple_traffic.router, prefix="/api/simple", tags=["simple-traffic"])
app.include_router(graph_traffic.router, prefix="/api/graph", tags=["graph-traffic"])

@app.get("/")
async def root():
    return {
        "message": "AI Traffic Congestion Prediction & Action Simulator API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=12000)