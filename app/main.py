from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .routers.receipts import (
    router as receipts_router,
)
from .routers.statistics import (
    router as statistics_router,
)


BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

STATIC_DIR = (
    BASE_DIR / "static"
)


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description=(
        "Приложение для сканирования чеков, "
        "распознавания данных и "
        "категоризации покупок"
    ),
)

app.include_router(
    receipts_router
)

app.include_router(
    statistics_router
)

if STATIC_DIR.exists():
    app.mount(
        "/static",
        StaticFiles(
            directory=str(
                STATIC_DIR
            )
        ),
        name="static",
    )


@app.get(
    "/",
    include_in_schema=False,
)
def home():
    index_file = (
        STATIC_DIR
        / "index.html"
    )

    if index_file.exists():
        return FileResponse(
            index_file
        )

    return {
        "message": settings.APP_NAME,
        "status": "running",
    }


@app.get(
    "/health",
    tags=["Состояние"],
)
def health():
    return {
        "status": "ok"
    }