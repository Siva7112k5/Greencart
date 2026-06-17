# ==============================================================================
# 1. IMPORTS
# ==============================================================================
import json
import os
import sys
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import logging

# Set up logging for detailed error visibility
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

app = Flask(__name__)

# ==============================================================================
# 2. CONFIGURATION (SECRET KEY & DATABASE)
# ==============================================================================
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a_very_secure_and_unique_secret_key_12345')

# Default local database uses SQLite, so the app does not require XAMPP.
database_url = os.environ.get('DATABASE_URL', 'sqlite:///flask_user_auth.db')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Connection pool improvements
app.config['SQLALCHEMY_POOL_RECYCLE'] = 2800
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True
}

db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 
login_manager.login_message = "Please log in to access this page." 

@login_manager.user_loader
def load_user(user_id):
    """Required by Flask-Login: loads user object from database."""
    # Using modern SQLAlchemy session method
    return db.session.get(User, int(user_id))


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, 'is_admin', False):
            flash('Admin access required.', 'error')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper


# ==============================================================================
# 3. USER MODEL + ADMIN AND ORDERS
# ==============================================================================
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<User {self.email}>'


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    payment_method = db.Column(db.String(100), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    order_status = db.Column(db.String(50), nullable=False, default='Processing')

    user = db.relationship('User', backref=db.backref('orders', lazy=True))

    def __repr__(self):
        return f'<Order {self.id} user={self.user_id} amount={self.total_amount}>'


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_order = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)

    order = db.relationship('Order', backref=db.backref('items', lazy=True))

    def __repr__(self):
        return f'<OrderItem {self.product_name} x{self.quantity}>'


# ==============================================================================
# 4. MOCK DATA & CART
# ==============================================================================
# Mock product data (replace with a database in production)
products_data = [
    {'id':1,'img':'potato_image_2.png','alt':'Potato','cat':'Vegetables','name':'Potato 500g','price':35,'old':40},
    {'id':2,'img':'tomato_image_2.png','alt':'Tomato','cat':'Vegetables','name':'Tomato 1 kg','price':28,'old':30},
    {'id':3,'img':'carrot_image.png','alt':'Carrot','cat':'Vegetables','name':'Carrot 500g','price':44,'old':50},
    {'id':4,'img':'spinach_image_1.png','alt':'Spinach','cat':'Vegetables','name':'Spinach 500g','price':15,'old':18},
    {'id':5,'img':'onion_image_1.png','alt':'Onion','cat':'Vegetables','name':'Onion 500g','price':45,'old':50},
    {'id':6,'img':'apple_image.png','alt':'Apple','cat':'Fruits','name':'Apple 1kg','price':90,'old':95},
    {'id':7,'img':'maggi_image.png','alt':'Maggi Noodles','cat':'Instant','name':'Maggi Noodles 280g','price':50,'old':55},
    {'id':8,'img':'orange_image.png','alt':'Orange','cat':'Fruits','name':'Orange 1kg','price':75,'old':80},
    {'id':9,'img':'banana_image_1.png','alt':'Banana','cat':'Fruits','name':'Banana 1kg','price':45,'old':50},
    {'id':10,'img':'mango_image_1.png','alt':'Mango','cat':'Fruits','name':'Mango 1kg','price':140,'old':150},
    {'id':11,'img':'grapes_image_1.png','alt':'Grapes','cat':'Fruits','name':'Grapes 500g','price':65,'old':70},
    {'id':12,'img':'amul_milk_image.png','alt':'Amul Milk','cat':'Dairy','name':'Amul Milk 1L','price':30,'old':35},
    {'id':13,'img':'paneer_image.png','alt':'Paneer','cat':'Dairy','name':'Paneer 200g','price':85,'old':90},
    {'id':14,'img':'eggs_image.png','alt':'Eggs','cat':'Dairy','name':'Eggs 12 pcs','price':85,'old':90},
    {'id':15,'img':'cheese_image.png','alt':'Cheese','cat':'Dairy','name':'Cheese 200g','price':130,'old':140},
    {'id':16,'img':'coca_cola_image.png','alt':'Coca-Cola','cat':'Drinks','name':'Coca-Cola 1.5L','price':60,'old':75},
    {'id':17,'img':'dairy_product_image.png','alt':'Sprite','cat':'Drinks','name':'Sprite 1.5L','price':60,'old':75},
    {'id':18,'img':'sprite_image_1.png','alt':'7 Up','cat':'Drinks','name':'7 Up 1.5L','price':70,'old':76},
    {'id':19,'img':'fanta_image_1.png','alt':'Fanta','cat':'Drinks','name':'Fanta 1.5L','price':65,'old':70},
    {'id':20,'img':'basmati_rice_image.png','alt':'Basmati Rice','cat':'Grains','name':'Basmati Rice 5kg','price':400,'old':450},
    {'id':21,'img':'wheat_flour_image.png','alt':'Wheat Flour','cat':'Grains','name':'Wheat Flour 5kg','price':230,'old':250},
    {'id':22,'img':'quinoa_image.png','alt':'Organic Quinoa','cat':'Grains','name':'Organic Quinoa 500g','price':420,'old':450},
    {'id':23,'img':'brown_rice_image.png','alt':'Brown Rice','cat':'Grains','name':'Brown Rice 1kg','price':110,'old':120},
    {'id':24,'img':'barley_image.png','alt':'Barley','cat':'Grains','name':'Barley 1kg','price':140,'old':150},
    {'id':25,'img':'brown_bread_image.png','alt':'Brown Bread','cat':'Bakery','name':'Brown Bread 400g','price':45,'old':50},
    {'id':26,'img':'butter_croissant_image.png','alt':'Butter Croissant','cat':'Bakery','name':'Butter Croissant 100g','price':45,'old':50},
    {'id':27,'img':'knorr_soup_image.png','alt':'Knorr Cup Soup','cat':'Instant','name':'Knorr Cup Soup 70g','price':30,'old':35},
    {'id':28,'img':'yippee_image.png','alt':'yippee Noodles','cat':'Instant','name':'Yippee Noodles 280g','price':50,'old':55},
    {'id':29,'img':'uppma_image.png','alt':'uppma','cat':'Instant','name':'Instant Uppma 300g','price':50,'old':55},
    {'id':30,'img':'darkfandasy_image.png','alt':'Dark Fantasy','cat':'Bakery','name':'Dark Fantasy','price':75,'old':80},
    
    {'id':31,'img':'bakery_image.png','alt':'white Bread','cat':'Bakery','name':'White Bread 400g','price':40,'old':50},
    {'id':32,'img':'cupcake_image.png','alt':'cupcake','cat':'Instant','name':'Cup Cake','price':35,'old':40}
]
cart_items = {}

# ==============================================================================
# 5. ROUTES
# ==============================================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/products')
def products_page():
    return render_template('Product.html', products=products_data)

@app.route('/cart')
@login_required 
def cart():
    # Pass the entire product data list to the cart template
    return render_template('cart.html', products=products_data)

@app.route('/search')
def search():
    """Handles product searches based on query string 'q'."""
    query = request.args.get('q', '').strip().lower()
    
    # Check if a query was provided
    if not query:
        # If no query, return an empty results page
        return render_template('search_results.html', query=query, results=[])
    
    # Filter products_data list for matches in name or category
    results = [
        p for p in products_data
        if query in p['name'].lower() or query in p['cat'].lower()
    ]
    
    # Render the results page
    return render_template('search_results.html', query=query, results=results)


@app.route('/organic_veggies')
def organic_veggies():
    """Renders a page for organic vegetables."""
    veggies = [p for p in products_data if p['cat'] == 'Vegetables']
    return render_template('organic_veggies.html', products=veggies)

@app.route('/fruits')
def fruits():
    """Renders a page for fruits."""
    fruits = [p for p in products_data if p['cat'] == 'Fruits']
    return render_template('fruits.html', products=fruits)

@app.route('/juices')
def juices():
    """Renders a page for juices and other beverages."""
    beverages = [p for p in products_data if p['cat'] == 'Drinks']
    return render_template('juices.html', products=beverages)

@app.route('/instant_food')
def instant_food():
    """Renders a page for instant food."""
    instant_products = [p for p in products_data if p['cat'].lower() == 'instant']
    return render_template('Product.html', products=instant_products)
    
@app.route('/dairy')
def dairy():
    """Renders a page for dairy products."""
    dairy_products = [p for p in products_data if p['cat'].lower() == 'dairy']
    return render_template('Product.html', products=dairy_products)

@app.route('/bakery')
def bakery():
    """Renders a page for bakery products."""
    bakery_products = [p for p in products_data if p['cat'].lower() == 'bakery']
    return render_template('Product.html', products=bakery_products)

# ------------------------------------------------------------------------------
# User Authentication Routes
# ------------------------------------------------------------------------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Ensure form fields have name='name', name='email', name='password'
        full_name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        # Basic form validation
        if not full_name or not email or not password:
             flash('All fields are required.', 'error')
             return redirect(url_for('register'))
             
        # Check if email is already registered
        existing_user = db.session.execute(
            db.select(User).filter_by(email=email)
        ).scalar_one_or_none()

        if existing_user:
            flash('Email already registered. Please login.', 'error')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(full_name=full_name, email=email, password_hash=hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login')) 
        
        except Exception as e:
            db.session.rollback()
            # Log error for server-side debugging
            app.logger.error(f"Database error during registration: {e}") 
            flash('An internal database error occurred during sign up.', 'error')
            return redirect(url_for('register'))
            
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = db.session.execute(
            db.select(User).filter_by(email=email)
        ).scalar_one_or_none()

        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=True) 
            next_page = request.args.get('next') 
            flash(f'Welcome back, {user.full_name or user.email}!', 'success')
            return redirect(next_page or url_for('index')) 
        else:
            flash('Invalid email or password.', 'error')
            # Use flash for all feedback; do not pass 'error' to render_template
            return render_template('login.html') 

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

# --- ADMIN PANEL ROUTES ---
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    users = User.query.order_by(User.id.desc()).all()
    orders = Order.query.order_by(Order.order_date.desc()).all()
    total_revenue = sum(order.total_amount for order in orders)
    return render_template('admin_dashboard.html', users=users, orders=orders, total_revenue=total_revenue)

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.order_by(User.id.desc()).all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/orders')
@login_required
@admin_required
def admin_orders():
    orders = Order.query.order_by(Order.order_date.desc()).all()
    return render_template('admin_orders.html', orders=orders)

# --- ORDER PLACEMENT ROUTE ---
@app.route('/place_order', methods=['POST'])
@login_required
def place_order():
    try:
        data = request.get_json()
    except Exception:
        app.logger.error("Received non-JSON data on /place_order")
        return jsonify({'status': 'error', 'message': 'Invalid data format.'}), 400

    required_fields = ['cart_items', 'total_amount', 'payment_method']
    if not all(field in data for field in required_fields):
        return jsonify({'status': 'error', 'message': 'Missing required fields in order data.'}), 400

    cart_items_data = data['cart_items']
    final_total = data['total_amount']
    payment_method = data['payment_method']
    
    if not cart_items_data:
        return jsonify({'status': 'error', 'message': 'Cart is empty.'}), 400
    
    try:
        # 3a. Create the main Order entry
        new_order = Order(
            user_id=current_user.id,
            payment_method=payment_method,
            total_amount=final_total,
            order_status='Processing'
        )
        db.session.add(new_order)
        db.session.flush() 

        # 3b. Create OrderItem entries and perform server-side re-calculation
        for item in cart_items_data:
            raw_product_id = item.get('product_id')
            quantity = item.get('quantity')
            
            # 🟢 FIX: Ensure product_id is successfully retrieved and converted to an integer
            if raw_product_id is None:
                # If product_id is explicitly missing (None), roll back and return error
                db.session.rollback()
                app.logger.error("Order item missing 'product_id'.")
                return jsonify({'status': 'error', 'message': 'Invalid product ID format received: None. (Product ID missing from cart data)'}), 400

            try:
                product_id = int(raw_product_id) 
            except (ValueError, TypeError):
                db.session.rollback()
                app.logger.error(f"Failed to convert product ID '{raw_product_id}' to integer.")
                return jsonify({'status': 'error', 'message': f'Invalid product ID format received: {raw_product_id}.'}), 400
            
            # Find the actual product details from the server's data source
            product = next((p for p in products_data if p['id'] == product_id), None)
            
            if not product or quantity <= 0:
                db.session.rollback()
                app.logger.error(f"Product ID {product_id} not found or quantity is zero.")
                return jsonify({'status': 'error', 'message': f'Invalid product ID or quantity for ID {product_id}.'}), 400

            price_at_order = product['price']
            item_subtotal = price_at_order * quantity

            new_order_item = OrderItem(
                order_id=new_order.id,
                product_id=product_id,
                product_name=product['name'],
                quantity=quantity,
                price_at_order=price_at_order,
                subtotal=item_subtotal
            )
            db.session.add(new_order_item)
            
        # 4. Commit the transaction
        db.session.commit()
        
        # 5. Success response
        return jsonify({
            'status': 'success',
            'order_id': new_order.id,
            'redirect_url': url_for('order_confirmation', order_id=new_order.id)
        }), 200

    except Exception as e:
        db.session.rollback()
        # Log the full traceback for better debugging
        app.logger.error(f"Order placement failed for user {current_user.id}: {e}", exc_info=sys.exc_info())
        return jsonify({
            'status': 'error', 
            'message': 'Failed to place order due to a server error. Please check server logs for details.'
        }), 500

@app.route('/order_confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    order = db.session.get(Order, order_id)
    if not order or order.user_id != current_user.id:
        flash('Order not found or access denied.', 'error')
        return redirect(url_for('index'))
    return render_template('order_confirmation.html', order=order) 


# ==============================================================================
# 6. RUN BLOCK
# ==============================================================================

def create_default_admin():
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
    existing_admin = User.query.filter_by(email=admin_email).first()
    if not existing_admin:
        admin = User(
            full_name='Administrator',
            email=admin_email,
            password_hash=generate_password_hash(admin_password),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        app.logger.info(f'Created default admin account: {admin_email}')


with app.app_context():
    db.create_all()
    create_default_admin()

if __name__ == '__main__':
    app.run(debug=True)

