# Smart Inventory & Stock Management System

![Django](https://img.shields.io/badge/Django-5.0-green)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple)

A modern, production-ready **Inventory & Stock Management System** built with Django. Manage products, suppliers, categories, stock movements, orders, and generate reports — all from a beautiful responsive dashboard.

---

## Features

- **Multi-Role Authentication** — Admin, Manager, Staff
- **Professional Dashboard** with Chart.js analytics
- **Complete CRUD** for Categories, Suppliers, Products
- **Stock Management** — Stock In/Out, Adjustments, Damage, Expired, History
- **Order Management** with Invoice PDF generation
- **Reports** — Inventory, Sales, Purchase, Low Stock; export CSV/Excel/PDF
- **Smart Notifications** — Low Stock, Out of Stock, New Orders (via Django Signals)
- **Dark / Light Mode** toggle
- **Glassmorphism** UI with smooth animations
- **Global Search** across all modules
- **Responsive** — mobile friendly Bootstrap 5

---

## Technology Stack

| Layer | Tech |
|---|---|
| Backend | Python 3.11, Django 5.0 |
| Frontend | HTML5, CSS3, Bootstrap 5.3, Chart.js, Bootstrap Icons |
| Database | MySQL 8.x |
| Images | Pillow |
| Forms | django-crispy-forms, crispy-bootstrap5 |
| Export | openpyxl (Excel), reportlab (PDF) |
| Config | python-decouple |

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/smart-inventory.git
cd smart-inventory
```

### 2. Create and activate virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env with your MySQL credentials and secret key
```

### 5. Create MySQL database

```sql
CREATE DATABASE smart_inventory CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 6. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create superuser

```bash
python manage.py createsuperuser
```

### 8. Run the development server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

---

## Folder Structure

```
Smart_Inventory_Stock_Management_System/
├── smartinventory/         Django project settings
├── apps/
│   ├── accounts/           Authentication & User Management
│   ├── dashboard/          Dashboard & Analytics
│   ├── categories/         Category CRUD
│   ├── suppliers/          Supplier CRUD
│   ├── products/           Product CRUD + Barcode
│   ├── stock/              Stock In/Out/History
│   ├── orders/             Orders & Invoices
│   ├── reports/            Reports & Exports
│   ├── notifications/      Notification System
│   └── core/               Shared utilities
├── templates/              All HTML templates
├── static/                 CSS, JS, Images
├── media/                  User uploaded files
├── requirements.txt
├── .env.example
└── README.md
```

---

## Default Login Credentials

After running `createsuperuser`, use those credentials. The superuser is automatically assigned the **Admin** role.

| Role | Access |
|---|---|
| Admin | Full access |
| Manager | Inventory, Reports, Orders |
| Staff | View, Add, Update (no Delete) |

---

## Future Enhancements

- REST API with Django REST Framework
- Mobile app integration
- WhatsApp/SMS notifications
- Multi-warehouse support
- Barcode scanner integration
- Advanced analytics with ML predictions

---

## License

MIT License — see LICENSE file for details.

---

## Developer

Built with ❤️ using Django 5.0 and Bootstrap 5.3
