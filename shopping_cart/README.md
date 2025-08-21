🛒 Shopping Cart API (FastAPI)

A minimal e-commerce backend built with FastAPI.
Features include user registration/login with JWT, admin role, product management (admin), and per-user shopping carts stored in JSON files.

✨ Features

Register / Login (JWT issued on login)

Auto-seed admin: the first registered user becomes admin; others become customer

Promote user to admin (admin-only)

Add products (admin-only) with auto-incrementing IDs

List products (public)

Add to cart (authenticated users; cart saved per user)

📁 File Storage (JSON)

All data is stored locally:

user.json – { "<username>": { "email": "...", "role": "admin|customer" } }

product.json – { "<product_name_lower>": { "id": <int>, "selling_price": <float> } }

cart.json – { "<username>": [ { id, product_name, selling_price, quantity, total } ] }

Files are auto-created if missing.

🧱 Project Structure (as used in snippets)
.
├─ main.py                 # FastAPI routes
├─ auth.py                 # Models, helpers, OAuth2, role checks, id generator
├─ sec.py                  # SECRET_KEY, ALGORITHM
├─ user.json
├─ product.json
└─ cart.json