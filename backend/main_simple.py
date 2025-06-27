from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Video Processor API (Simple)")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Video Processor API is running!", "status": "ok"}

@app.get("/api/v1/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/v1/jobs/batch")
async def create_batch_jobs(data: dict):
    return {"message": "Batch job endpoint working", "received": data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)