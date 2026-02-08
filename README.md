# Billing System

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.128.3-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12%2B-blue)

A comprehensive web-based billing system built with FastAPI that handles product management, billing calculations, order history, and invoice generation with email notifications.

## Quick Start

```bash
# Clone and setup
cd billing-system
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r app/requirements.txt

# Configure database (create .env file in app directory)
# Run migrations
cd app
alembic upgrade head
python seed_data.py

# Start server (from project root)
cd ..
uvicorn app.main:app --reload
```

Visit `http://localhost:8000` to access the application.

## Table of Contents

- [Quick Start](#quick-start)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Usage Guide](#usage-guide)
  - [Web Interface Pages](#web-interface-pages)
  - [API Documentation](#api-documentation)
  - [API Endpoints](#api-endpoints)
  - [Example API Usage](#example-api-usage)
- [Database Schema](#database-schema)
- [Key Features Explained](#key-features-explained)
- [Troubleshooting](#troubleshooting)
- [Development Notes](#development-notes)
- [FAQ](#frequently-asked-questions-faq)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Production Deployment](#production-deployment)
- [Performance Tips](#performance-tips)
- [Security Best Practices](#security-best-practices)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
- [Support](#support)
- [License](#license)

## Features

- ✅ **Product Management**: Full CRUD operations for products with stock tracking and web interface
- ✅ **Billing System**: Create bills with multiple products, automatic tax calculation, and stock deduction
- ✅ **Denomination Management**: Track available cash denominations, calculate optimal change, and manage via web interface
- ✅ **Order History**: View all previous purchases by customer email with detailed order information
- ✅ **Email Invoices**: Automatic invoice generation and email delivery (asynchronous)
- ✅ **Web Interface**: User-friendly forms for billing, products, denominations, and order viewing
- ✅ **RESTful API**: Complete API with interactive Swagger documentation
- ✅ **Database Migrations**: Alembic integration for schema management

## Technology Stack

- **Backend**: FastAPI 0.128.3 (Python 3.8+)
- **Database**: PostgreSQL with SQLAlchemy 2.0.46 ORM
- **Email Service**: FastAPI-Mail 1.4.1
- **Frontend**: HTML/CSS/JavaScript with Jinja2 3.1.6 templates
- **Web Server**: Uvicorn 0.40.0 (ASGI server)
- **Database Migrations**: Alembic 1.18.3
- **Validation**: Pydantic 2.12.5
- **Database Driver**: psycopg2-binary 2.9.11

## Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)

## Installation & Setup

### 1. Clone/Extract the Project

```bash
cd billing-system
```

### 2. Create Virtual Environment

```bash
python -m venv .venv

# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r app/requirements.txt
```

**Note**: The requirements.txt is located in the `app` directory.

### 4. Configure Database

Create a PostgreSQL database:

```sql
CREATE DATABASE billing_db;
```

### 5. Configure Environment Variables

Create a `.env` file in the `app` directory:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=billing_db
DB_USER=postgres
DB_PASSWORD=your_password_here

# Email Configuration (Optional - for invoice emails)
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_FROM=your_email@gmail.com
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_STARTTLS=True
MAIL_SSL_TLS=False
```

**Note**: For Gmail, you need to use an [App Password](https://support.google.com/accounts/answer/185833). If you don't configure email settings, the system will still work but won't send invoice emails.

### 6. Run Database Migrations

```bash
# From the app directory
cd app
alembic upgrade head
```

This will create all necessary database tables (products, orders, order_items, denominations).

### 7. Seed Initial Data

```bash
# From the app directory
cd app
python seed_data.py
```

This will populate the database with:
- 10 sample products (P001 to P010) with names, prices, tax percentages, and stock
- 10 denominations (₹2000, ₹500, ₹200, ₹100, ₹50, ₹20, ₹10, ₹5, ₹2, ₹1)

### 8. Run the Application

**Important**: Always run the application from the project root directory (not from the `app` directory).

```bash
# Make sure you're in the project root directory
cd /path/to/billing-system

# Activate virtual environment if not already activated
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows

# Run the server
uvicorn app.main:app --reload
```

The application will start at: `http://localhost:8000`

**Alternative Port**: If port 8000 is in use:
```bash
uvicorn app.main:app --reload --port 8001
```

## Usage Guide

### Web Interface Pages

1. **Home/Billing Page** (`http://localhost:8000/` or `/billing`)
   - Enter customer email
   - Add products by Product ID and quantity (click "Add New Product" for multiple items)
   - Enter available denominations in the shop
   - Enter paid amount
   - Click "Generate Bill" to create order and send invoice

2. **Products Management** (`http://localhost:8000/products`)
   - View all products in a table format
   - Add new products with ID, name, price, tax percentage, and stock
   - Update existing product details
   - Delete products
   - Real-time stock tracking

3. **Denominations Management** (`http://localhost:8000/denominations`)
   - View all available denominations
   - Add new denominations
   - Update available count for each denomination
   - Delete denominations
   - Sorted by value (highest to lowest)

4. **Order History** (`http://localhost:8000/orders`)
   - Search orders by customer email
   - View order details including date, total, items
   - Access invoices for previous orders
   - Filter and track customer purchase history

5. **Invoice Page** (`http://localhost:8000/invoice/{order_id}`)
   - View detailed invoice with all items
   - See tax breakdown and totals
   - View denomination breakdown for change given
   - Print invoice
   - Invoice automatically sent to customer email

### API Documentation

Interactive API documentation available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### API Endpoints

#### Products
- `POST /api/products/` - Create new product
  - **Body**: `{ "product_id": "P011", "name": "Product Name", "price": 100.0, "tax_percentage": 18.0, "available_stock": 50 }`
- `GET /api/products/` - List all products (supports pagination with `skip` and `limit` query params)
- `GET /api/products/{product_id}` - Get product details by product ID
- `PUT /api/products/{product_id}` - Update product (partial updates supported)
- `DELETE /api/products/{product_id}` - Delete product

#### Billing
- `POST /api/billing/` - Create new bill/order
  - **Body**: `{ "customer_email": "user@example.com", "items": [{"product_id": "P001", "quantity": 1}], "paid_amount": 1000.0 }`

#### Orders
- `GET /api/orders/customer/{email}` - Get customer order history
- `GET /api/orders/{order_id}` - Get specific order details with items

#### Denominations
- `POST /api/denominations/` - Create denomination
  - **Body**: `{ "value": 10, "available_count": 100 }`
- `GET /api/denominations/` - List all denominations (sorted by value descending)
- `GET /api/denominations/{id}` - Get specific denomination by ID
- `PUT /api/denominations/{id}` - Update denomination count by ID
- `PUT /api/denominations/value/{value}` - Update denomination count by value
- `DELETE /api/denominations/{id}` - Delete denomination

### Example API Usage

**Create a Product:**

```bash
curl -X POST "http://localhost:8000/api/products/" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "P011",
    "name": "Wireless Mouse",
    "price": 599.00,
    "tax_percentage": 18.0,
    "available_stock": 100
  }'
```

**Get All Products:**

```bash
curl "http://localhost:8000/api/products/"
```

**Create a Bill:**

```bash
curl -X POST "http://localhost:8000/api/billing/" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_email": "customer@example.com",
    "items": [
      {"product_id": "P001", "quantity": 1},
      {"product_id": "P002", "quantity": 2}
    ],
    "paid_amount": 52000.00
  }'
```

**Get Order History:**

```bash
curl "http://localhost:8000/api/orders/customer/customer@example.com"
```

**Update Denomination Count:**

```bash
curl -X PUT "http://localhost:8000/api/denominations/value/100" \
  -H "Content-Type: application/json" \
  -d '{
    "available_count": 50
  }'
```

## Database Schema

### Products Table
| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Primary key (auto-increment) |
| `product_id` | String | Unique product identifier (e.g., "P001") |
| `name` | String | Product name |
| `price` | Float | Unit price |
| `tax_percentage` | Float | Tax percentage (e.g., 18.0 for 18% GST) |
| `available_stock` | Integer | Available quantity in inventory |
| `created_at` | DateTime | Timestamp of creation |

**Indexes**: `product_id` (unique)

### Orders Table
| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Primary key (auto-increment) |
| `customer_email` | String | Customer email address (indexed) |
| `total_without_tax` | Float | Subtotal before tax |
| `total_tax` | Float | Total tax amount |
| `total_amount` | Float | Grand total (subtotal + tax) |
| `paid_amount` | Float | Amount paid by customer |
| `balance_amount` | Float | Change returned to customer |
| `created_at` | DateTime | Timestamp of order creation |

**Indexes**: `customer_email`

### Order Items Table
| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Primary key (auto-increment) |
| `order_id` | Integer | Foreign key to orders table |
| `product_id` | Integer | Foreign key to products table |
| `quantity` | Integer | Quantity purchased |
| `unit_price` | Float | Price per unit at time of purchase |
| `tax_amount` | Float | Tax amount for this line item |
| `total_price` | Float | Total for this line item (quantity × unit_price + tax) |

**Foreign Keys**: `order_id` → orders.id, `product_id` → products.id

### Denominations Table
| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Primary key (auto-increment) |
| `value` | Integer | Denomination value (e.g., 100, 500, 2000) |
| `available_count` | Integer | Number of notes/coins available |

**Indexes**: `value` (unique)

### Entity Relationships
```
Orders (1) ←→ (Many) Order Items
Order Items (Many) → (1) Products
```

## Key Features Explained

### Denomination Calculation
The system uses a greedy algorithm to calculate optimal change based on available denominations. It prioritizes larger denominations first while respecting available counts. The calculation service ensures accurate change breakdown for customer transactions.

### Stock Management
- Product stock is automatically reduced when orders are created
- The system validates stock availability before processing orders
- Real-time stock updates via the Products Management page
- Prevents overselling with stock validation checks

### Email Invoices
- Invoices are sent asynchronously using FastAPI background tasks
- Order creation doesn't wait for email delivery (non-blocking)
- Includes detailed invoice with all order items, taxes, and totals
- Works with any SMTP-compatible email service

### Tax Calculation
Taxes are calculated per product based on their individual tax percentages, providing accurate GST calculations. Each order item maintains its tax amount separately for detailed invoice reporting.

### Async Operations
- Background email sending for better performance
- Non-blocking invoice generation
- Improved user experience with fast response times

## Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running: `psql --version` or check system services
- Check credentials in `.env` file match your PostgreSQL settings
- Ensure database exists: `psql -U postgres -c "\l"` to list databases
- Test connection: `psql -h localhost -U postgres -d billing_db`

### Email Not Sending
- Verify email credentials in `.env`
- For Gmail, use App Password, not regular password ([Create App Password](https://support.google.com/accounts/answer/185833))
- Check SMTP settings (port 587 for TLS, 465 for SSL)
- Enable "Less secure app access" if using older email providers
- Check spam/junk folder for test emails

### Import Errors or Module Not Found
- Ensure virtual environment is activated: `which python` should show `.venv` path
- Reinstall dependencies: `pip install -r app/requirements.txt`
- Verify you're running from project root, not from `app` directory
- Check Python version: `python --version` (requires 3.8+)

### Port Already in Use
```bash
# Find process using port 8000 (macOS/Linux)
lsof -i :8000

# Run on different port
uvicorn app.main:app --reload --port 8001
```

### Migration Errors
```bash
# Reset migrations (use with caution in development only)
cd app
alembic downgrade base
alembic upgrade head

# Create new migration after model changes
alembic revision --autogenerate -m "Description of changes"
```

### Static Files Not Loading
- Ensure `app/static` directory exists (created automatically on startup)
- Check file permissions
- Clear browser cache

## Development Notes

### Adding New Products
Use the seed script, web interface, or API to add products:

```bash
# Via seed script
cd app
python seed_data.py

# Via web interface
# Navigate to http://localhost:8000/products

# Via API
curl -X POST "http://localhost:8000/api/products/" \
  -H "Content-Type: application/json" \
  -d '{"product_id": "P011", "name": "New Product", "price": 100.0, "tax_percentage": 18.0, "available_stock": 50}'
```

### Running Migrations
After making changes to database models:

```bash
cd app
# Create migration
alembic revision --autogenerate -m "Description of changes"

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

### Project Structure Overview
- `api/` - API route handlers (endpoints)
- `core/` - Configuration and database setup
- `models/` - SQLAlchemy database models
- `schemas/` - Pydantic models for request/response validation
- `services/` - Business logic (billing, email, denominations)
- `templates/` - Jinja2 HTML templates
- `utils/` - Helper functions and calculations
- `alembic/` - Database migration scripts

## Frequently Asked Questions (FAQ)

### How do I add a new product?
You can add products through:
1. The web interface at `/products`
2. The REST API endpoint `POST /api/products/`
3. Directly via the seed script

### Can I customize tax rates per product?
Yes, each product has its own `tax_percentage` field which can be set individually during product creation or update.

### How does the change calculation work?
The system uses a greedy algorithm that prioritizes larger denominations first, while respecting the available count of each denomination type. If exact change cannot be provided, the system will inform you.

### Can I use this without email configuration?
Yes, the system will work without email configuration. Orders will be created successfully, but invoice emails won't be sent. The invoice is still accessible via the web interface.

### How do I reset the database?
```bash
cd app
alembic downgrade base  # Remove all tables
alembic upgrade head    # Recreate tables
python seed_data.py     # Reseed data
```

### Is there user authentication?
The current version doesn't include user authentication. For production use with multiple users, consider implementing JWT or session-based authentication.

### Can I export orders to CSV/Excel?
This feature is not built-in but can be easily added by creating a new endpoint that queries orders and formats them as CSV using Python's `csv` module or `pandas`.

### How do I change the currency?
Currency symbols are hardcoded as ₹ (Indian Rupee). To change, search for `₹` in the codebase and replace with your currency symbol.

## Testing

### Manual Testing
1. Start the application
2. Navigate to `/products` and add test products
3. Go to `/denominations` and set up cash denominations
4. Create a test order from the billing page (`/`)
5. View the generated invoice
6. Check order history at `/orders`

### API Testing via Swagger UI
1. Visit `http://localhost:8000/docs`
2. Use the interactive documentation to test endpoints
3. All endpoints include request/response examples

### Testing Email Functionality
1. Configure valid SMTP credentials in `.env`
2. Create a test order with your email address
3. Check your inbox for the invoice email
4. Verify invoice formatting and content

## Project Structure

```
billing-system/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Environment variables (create this)
│   ├── alembic.ini             # Alembic configuration
│   ├── seed_data.py            # Database seeding script
│   ├── api/
│   │   ├── __init__.py
│   │   ├── billing.py          # Billing endpoints
│   │   ├── order.py            # Order history endpoints
│   │   ├── product.py          # Product CRUD endpoints
│   │   ├── denomination.py     # Denomination endpoints
│   │   └── views.py            # HTML page routes
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration settings
│   │   └── database.py         # Database connection setup
│   ├── models/
│   │   ├── product.py          # Product database model
│   │   ├── order.py            # Order database model
│   │   ├── order_item.py       # Order item database model
│   │   └── denomination.py     # Denomination database model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── product.py          # Product Pydantic schemas
│   │   ├── order.py            # Order Pydantic schemas
│   │   ├── billing.py          # Billing request/response schemas
│   │   └── denomination.py     # Denomination Pydantic schemas
│   ├── services/
│   │   ├── billing_service.py  # Billing business logic
│   │   ├── denomination_service.py  # Denomination calculations
│   │   └── email_service.py    # Email sending service
│   ├── templates/
│   │   ├── base.html           # Base template with common layout
│   │   ├── billing.html        # Billing form page
│   │   ├── invoice.html        # Invoice display page
│   │   ├── orders.html         # Order history page
│   │   ├── products.html       # Product management page
│   │   └── denominations.html  # Denomination management page
│   ├── static/                 # Static files (CSS/JS/images)
│   ├── utils/
│   │   └── calculations.py     # Utility functions
│   └── alembic/                # Database migrations
│       ├── env.py
│       └── versions/
│           └── *.py            # Migration files
├── .venv/                      # Virtual environment (created by you)
├── .gitignore
└── README.md
```

## Production Deployment

For production deployment, consider these recommendations:

### 1. Environment Configuration
```bash
# Set production mode in .env
DEBUG=False
```

### 2. Use Production WSGI Server
Install and use Gunicorn with Uvicorn workers:

```bash
pip install gunicorn

# Run with multiple workers
gunicorn app.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### 3. Database Configuration
- Use strong PostgreSQL credentials
- Enable SSL connections
- Set up regular database backups
- Use connection pooling for better performance

### 4. Security Measures
- Enable HTTPS with SSL/TLS certificates (Let's Encrypt recommended)
- Configure CORS properly in FastAPI
- Use environment variables for all sensitive data (never commit `.env`)
- Implement rate limiting for API endpoints
- Set up firewall rules

### 5. Reverse Proxy (Nginx Example)
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/billing-system/app/static;
    }
}
```

### 6. Monitoring & Logging
- Set up application logging
- Monitor server resources (CPU, RAM, disk)
- Track API response times
- Set up error alerting

### 7. Process Management
Use systemd or supervisor to manage the application process:

```ini
# /etc/systemd/system/billing-system.service
[Unit]
Description=Billing System FastAPI Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/billing-system
Environment="PATH=/path/to/billing-system/.venv/bin"
ExecStart=/path/to/billing-system/.venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

**Important**: Always run the application from the project root directory, not from the `app` subdirectory.


## Security Best Practices

- Never commit `.env` file to version control
- Regularly update dependencies: `pip install --upgrade -r app/requirements.txt`
- Implement input validation (already handled by Pydantic)
- Use parameterized queries (already handled by SQLAlchemy)
- Set up HTTPS in production
- Implement authentication/authorization if exposing to public internet
- Regular security audits and penetration testing



### Development Guidelines
- Follow PEP 8 style guidelines for Python code
- Add docstrings to all functions and classes
- Update README if adding new features
- Test all changes before submitting PR
- Keep commits focused and atomic



## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Database management with [SQLAlchemy](https://www.sqlalchemy.org/)
- Email functionality via [FastAPI-Mail](https://sabuhish.github.io/fastapi-mail/)
- Migrations handled by [Alembic](https://alembic.sqlalchemy.org/)

---

**Version**: 1.0.0  
**Last Updated**: February 2026

For questions or support, please open an issue in the repository.

