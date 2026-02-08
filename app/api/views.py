from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter(tags=["Views"])

# Setup templates
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page - redirects to billing"""
    return templates.TemplateResponse("billing.html", {"request": request})


@router.get("/billing", response_class=HTMLResponse)
async def billing_page(request: Request):
    """Billing form page (Page 1)"""
    return templates.TemplateResponse("billing.html", {"request": request})


@router.get("/invoice/{order_id}", response_class=HTMLResponse)
async def invoice_page(request: Request, order_id: int):
    """Invoice display page (Page 2)"""
    return templates.TemplateResponse("invoice.html", {"request": request})


@router.get("/orders", response_class=HTMLResponse)
async def orders_page(request: Request):
    """Order history page"""
    return templates.TemplateResponse("orders.html", {"request": request})


@router.get("/products", response_class=HTMLResponse)
async def products_page(request: Request):
    """Products management page"""
    return templates.TemplateResponse("products.html", {"request": request})


@router.get("/denominations", response_class=HTMLResponse)
async def denominations_page(request: Request):
    """Denominations management page"""
    return templates.TemplateResponse("denominations.html", {"request": request})
