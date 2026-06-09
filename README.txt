SOLODECK — Python E-Commerce Store
=====================================
Built with Flask + SQLite. No paid services required.

HOW TO RUN
-----------
1. Make sure Python 3 is installed
2. Install Flask:  pip install flask
3. Run the app:    python app.py
4. Open browser:   http://localhost:5000

PAGES
------
/           Home page with featured products
/shop       Full product catalog with filters
/product/1  Individual product page
/cart       Shopping cart
/checkout   Checkout form
/admin      Admin dashboard

ADMIN DASHBOARD (/admin)
--------------------------
- Add new products
- Delete products
- View all orders
- Update order status (pending/confirmed/shipped/delivered)
- See subscriber count and revenue

TO ADD REAL PAYMENTS
---------------------
1. Sign up at stripe.com (free)
2. pip install stripe
3. Replace the demo payment section in checkout.html
4. Add: stripe.api_key = "your_key"
5. Create a payment intent in the /checkout POST route

TO DEPLOY ONLINE (free)
-------------------------
1. Railway.app or Render.com — free Python hosting
2. Upload this folder
3. Set start command: python app.py
4. Your store is live with a real URL

FILES
------
app.py              Main Flask application (all routes + database)
database/           SQLite database (auto-created on first run)
templates/
  base.html         Navigation, footer, shared styles
  home.html         Homepage
  shop.html         Product catalog
  product.html      Single product page
  cart.html         Shopping cart
  checkout.html     Checkout form
  confirm.html      Order confirmation
  admin.html        Admin dashboard

PRODUCTS INCLUDED (seeded automatically)
------------------------------------------
Digital: Brand Starter Kit $19, Social Media Pack $17,
         Freelance Proposal $12, Business Workbook $15, Bundle $49
Physical: Tee $35, Hoodie $58, Cap $32, Poster $22, Notebook $28

TO USE AS A FIVERR PORTFOLIO PIECE
-------------------------------------
Show clients this working store. Offer to build them one like it.
Charge $300-800 per store. I can customize it for any niche.
