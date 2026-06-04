import os
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_HOST = os.getenv(
    "RABBITMQ_HOST",
    "localhost"
)

RABBITMQ_QUEUE = os.getenv(
    "RABBITMQ_QUEUE",
    "seo-audit-created"
)

POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

DATABASE_URL = (
    f"postgresql://"
    f"{POSTGRES_USER}:"
    f"{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:"
    f"{POSTGRES_PORT}/"
    f"{POSTGRES_DB}"
)