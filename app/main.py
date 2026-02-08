from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import sys


if __name__ != "__main__":
    parent_dir = str(Path(__file__).parent.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

from app.api import billing, product, order, denomination, views

app = FastAPI(
    title="Billing System API",
    description="A comprehensive billing system with product management and order processing",
    version="1.0.0"
)


static_path = Path(__file__).parent / "static"
static_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


app.include_router(billing.router, prefix="/api")
app.include_router(product.router, prefix="/api")
app.include_router(order.router, prefix="/api")
app.include_router(denomination.router, prefix="/api")


app.include_router(views.router)