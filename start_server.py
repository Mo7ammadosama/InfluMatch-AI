"""Standalone server starter — run with: python start_server.py"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "waslai.backend.main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
