"""Crypto Trading MVP - Main Application""" 
import os 
import sys 
import logging 
from pathlib import Path 
 
from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware 
import uvicorn 
 
# Configure logging 
logging.basicConfig( 
    level=logging.INFO, 
    format='[%(asctime)s] %(levelname)s: %(message)s' 
) 
 
logger = logging.getLogger(__name__) 
 
# Create FastAPI app 
app = FastAPI( 
    title="Crypto Trading MVP API", 
    description="API for cryptocurrency trading bot", 
    version="1.0.0" 
) 
 
# Add CORS middleware 
app.add_middleware( 
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"] 
) 
 
@app.get("/health") 
async def health_check(): 
    return {"status": "healthy", "service": "crypto-trading-api"} 
 
@app.get("/") 
async def root(): 
    return {"message": "Crypto Trading MVP API", "version": "1.0.0"} 
 
if __name__ == "__main__": 
    host = "0.0.0.0" 
    port = 8000 
    uvicorn.run(app, host=host, port=port) 
