import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.endpoints import router

app = FastAPI(title="Unitree Gallery Service", description="A simple image gallery service")

# Include API routes
app.include_router(router, prefix="/api")

def main():
    print("Starting Unitree Gallery Service...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
