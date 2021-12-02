
from fastapi import FastAPI, Body, Request

app = FastAPI(
    title="FastAPI Docs Test",
    description="FastAPI Application Params Test",
    version="1.1.1",
    docs_url="/docs"
)