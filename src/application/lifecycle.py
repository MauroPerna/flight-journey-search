from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI


logger = logging.getLogger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")

    try:
        yield

    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise

    finally:
        logger.info("Shutting down application...")
        logger.info("Application shut down successfully")
