# Aura Bistro — Smart Restaurant Food Ordering & Kitchen Dashboard
**Capstone Project 2: Django Full-Stack Final Project**

A modern restaurant ordering portal and kitchen display system (KDS) built with Django, Bootstrap 5, Vanilla JavaScript (ES6+), SQLite, WhiteNoise, and Gunicorn, engineered for local execution and deployment on Render.

---

## 🍽️ Key Features

1. **Responsive Food Menu (`/`)**
   - Categorized browsing: Appetizers, Main Course, Desserts, Beverages.
   - Real-time client-side instant search filter.
   - Dietary badges (Vegetarian green leaf / Non-Vegetarian tags).
   - Category filtering pills with Bootstrap icons.
   - "Veg Only" toggle switch.

2. **Interactive Shopping Cart & Checkout (`/cart/`)**
   - Dynamic tray calculations: subtotal, 5% estimated tax, and grand total.
   - Client persistence with `localStorage` synchronized with Django sessions.
   - **Server-Side Security**: Totals and prices are strictly re-verified on the server before an order is committed to prevent client tampering.
   - Table selector (Table 1 through 6, Bar seats, or Takeout), customer contact details, and special preparation notes.

3. **Live Order Tracking (`/track/<order_number>/`)**
   - Real-time step progress tracker: `Received ➔ Preparing ➔ Ready ➔ Completed`.
   - Glowing progress bar and active state ring animations.
   - Real-time polling via `/api/order/<order_number>/status/` (updates live without page refresh as kitchen updates status).
   - Itemized digital receipt breakdown.

4. **Kitchen Display System (KDS) (`/kitchen/`)**
   - Line cook & expediter management terminal.
   - Color-coded tickets: Received (Blue), Preparing (Amber), Ready (Cyan), Completed (Emerald).
   - One-click status advances (`Start Cooking`, `Mark Ready`, `Serve & Complete`).
   - Filter tabs by status and table search.
   - Auto-refresh toggle (15s interval) and real-time KPI counters.

5. **Django Admin (`/admin/`)**
   - Category management with icons and display ordering.
   - MenuItem management with price, availability toggles, and vegetarian tags.
   - Order management with inline item tables and status filters.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.11+, Django 6.x, Django ORM
- **Database**: SQLite (`db.sqlite3` — default/built-in)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons
- **Static Assets & Production**: WhiteNoise 6.x, Gunicorn 26.x
- **Hosting / PaaS**: Render

---

## 🚀 Quickstart & Local Setup

### 1. Activate Virtual Environment
```bash
# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Migrations & Seed Sample Data
```bash
python manage.py migrate
python create_superuser.py
python manage.py seed_data
```

### 4. Start Local Development Server
```bash
python manage.py runserver
```
Visit:
- **Food Menu**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Order Tray & Checkout**: [http://127.0.0.1:8000/cart/](http://127.0.0.1:8000/cart/)
- **Order Tracking**: [http://127.0.0.1:8000/track/](http://127.0.0.1:8000/track/)
- **Kitchen Dashboard**: [http://127.0.0.1:8000/kitchen/](http://127.0.0.1:8000/kitchen/)
- **Django Admin**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
  - Username: `admin`
  - Password: `admin12345`

### 5. Run Automated Tests
```bash
python manage.py test
```

---

## ☁️ Render Deployment Guide

### Deployment Configuration Included
- **`requirements.txt`**: Pins Django, Gunicorn, and WhiteNoise.
- **`render.yaml`**: Pre-configured Blueprint service with Python 3.11, build command (`pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate && python create_superuser.py && python manage.py seed_data`), and Gunicorn start command.
- **`settings.py`**: Configured with `ALLOWED_HOSTS = ["localhost", "127.0.0.1", ".onrender.com"]`, `CSRF_TRUSTED_ORIGINS`, and WhiteNoise middleware.

### Steps to Deploy:
1. Initialize a git repository and commit all files:
   ```bash
   git init
   git add .
   git commit -m "Prepare Django project for Render"
   ```
2. Push your repository to your GitHub account:
   ```bash
   git remote add origin https://github.com/vuchulasowmya2007-cmyk/Dimpu_Restaurant-Ordering.git
   git branch -M main
   git push -u origin main
   ```
3. Go to [Render Dashboard](https://dashboard.render.com/) and click **New +** → **Blueprint** (or **Web Service**).
4. Select your GitHub repository.
5. If using **Blueprint**, Render will automatically detect `render.yaml` and configure:
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate && python create_superuser.py && python manage.py seed_data`
   - **Start Command**: `python manage.py migrate && python create_superuser.py && python manage.py seed_data && gunicorn dimpu.wsgi:application`
6. Under Environment Variables, add:
   - `SECRET_KEY`: (a long random string)
   - `RENDER`: `True`
7. Click **Apply / Deploy**.
8. Once built, open the generated `https://<service-name>.onrender.com` link.
