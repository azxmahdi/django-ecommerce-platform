# 🛒 E‑Commerce Platform (Django + Celery + Redis + Postgres)

A full‑featured e‑commerce platform built with **Django 4.2**, supporting product catalogs, categories, wishlists, orders, payments, blog posts, banners, static pages, and site information.  
The project is containerized with **Docker** and orchestrated via **docker‑compose** for both development and production environments.

---

## 🚀 Features

- **Shop**: Products, categories, attributes, variants, images, search logs, filters, caching.
- **Wishlist**: Add/remove products to personal wishlists.
- **Order**: Order management, shipping methods, order statuses.
- **Payment**: Payment gateways seeding and integration.
- **Blog**: Posts, categories, comments, popular posts.
- **Banner**: Configurable banners for homepage and categories.
- **Pages**: Static pages (About, Contact, Terms).
- **Website**: Site info (logo, contact, support hours), social links, licenses.
- **Admin Panel**: Rich Django admin with Summernote editor, MPTT tree categories, inline editing.
- **Caching**: Redis‑based caching for categories, site info, search logs, and resources.
- **Async Tasks**: Celery workers and beat scheduler for background jobs.
- **Database**: PostgreSQL with pgAdmin for management.
- **Deployment**: Gunicorn + Nginx in production, Dockerized services.

---

## 🛠 Tech Stack

- **Backend**: Django 4.2, Django REST Framework (optional), Celery 5.5
- **Database**: PostgreSQL 16
- **Cache/Broker**: Redis
- **Frontend**: Django templates (Summernote editor for admin)
- **Deployment**: Docker, docker‑compose, Gunicorn, Nginx
- **Other**: Django MPTT, Django Redis, Django Celery Beat, Pillow, Jdatetime (Persian calendar)

---

## 📦 Installation

### 1. Clone the repository
```bash
git clone https://github.com/azxmahdi/django-ecommerce-platform.git
cd django-ecommerce-platform
```

### 2. Environment variables
Create `.env` files under:
- `./envs/dev/django/.env`
- `./envs/prod/django/.env`

#### Example `.env` (Production)
```env
DEBUG=False
SECRET_KEY=your_secret_key_here
MERCHANT_ID=your_merchant_id_here
SANDBOX_MODE=False

ENGINE=django.db.backends.postgresql
NAME=name
USER=user
PASSWORD=password
HOST=db
PORT=5432

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

> ⚠️ For development, set `DEBUG=True` and `SANDBOX_MODE=True`.

---

### 3. Development setup
```bash
docker-compose up --build
```
Services:
- Backend: Django runserver (port 8000)
- Postgres: port 5432
- Redis: port 6379
- pgAdmin: port 5050
- Celery worker & beat

### 4. Production/Staging setup
```bash
docker-compose -f docker-compose-stage.yml up --build -d
```
Services:
- Backend: Gunicorn (exposed via Nginx on port 80)
- Postgres, Redis
- Celery worker & beat
- Nginx serving static/media files

---

## ⚙️ Management Commands

Each app provides seed/init commands for bootstrapping data:

- **banner**  
  - `python manage.py create_banners`

- **blog**  
  - `python manage.py fill_posts`  
  - `python manage.py init_post_categories`

- **order**  
  - `python manage.py seed_shipping_methods`

- **pages**  
  - `python manage.py create_static_pages`

- **payment**  
  - `python manage.py seed_gateways`

- **shop**  
  - `python manage.py create_category_attributes`  
  - `python manage.py fill_products`  
  - `python manage.py init_features`  
  - `python manage.py init_product_categories`

- **website**  
  - `python manage.py create_site_info`

---

## 🐳 Docker Overview

### Development
- **Backend**: Python 3.12 slim, Django runserver
- **Celery worker/beat**: background tasks
- **Postgres + pgAdmin**
- **Redis**

### Production
- **Backend**: Python 3.8 slim, Gunicorn entrypoint
- **Nginx**: reverse proxy, static/media serving
- **Volumes**: static, media, postgres data
- **Celery worker/beat**
- **Redis**

---

## 📂 Project Structure (simplified)

```
core/
  shop/
  wishlist/
  order/
  payment/
  blog/
  banner/
  pages/
  website/
dockerfiles/
  dev/django/Dockerfile
  prod/django/Dockerfile
envs/
  dev/django/.env
  prod/django/.env
docker-compose.yml
docker-compose-stage.yml
requirements.txt
```

---

## 🧪 Development Notes

- Use `django-debug-toolbar` for debugging queries.
- Redis caching is used for categories, site info, search logs, and resources.
- Celery Beat schedules tasks using `django_celery_beat`.
- Persian date support via `jdatetime` and `jalali_core`.

---

## 📜 License

This project is licensed under the MIT License.  
Feel free to use, modify, and distribute.

