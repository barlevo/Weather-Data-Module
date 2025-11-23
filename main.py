"""FastAPI application entry point."""

import uvicorn
from weather_module.http_api import app
from weather_module.logging_config import get_logger

logger = get_logger("main")

if __name__ == "__main__":
    logger.info("Starting FastAPI server via main.py")
    uvicorn.run(app, host="0.0.0.0", port=8000)

