import os
from functools import wraps
from datetime import datetime, timedelta

from flask import (Flask, render_template, redirect, url_for, request, flash,
                   send_from_directory, jsonify, abort)
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import jwt

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# -----------------
# Models
# -----------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user")  # 'admin' or 'user'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, default=0.0)
    image = db.Column(db.String(300))  # filename
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# -----------------
# Login loader
# -----------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -----------------
# Helpers
# -----------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash("Admin access required.", "warning")
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth = request.headers.get('Authorization', None)
        if auth and auth.startswith('Bearer '):
            token = auth.split(' ')[1]
        if not token:
            return jsonify({"message": "Token is missing!"}), 401
        try:
            data = jwt.decode(token, app.config['JWT_SECRET'], algorithms=["HS256"])
            current = User.query.get(data['user_id'])
            if not current:
                raise Exception("Invalid user")
        except Exception as e:
            return jsonify({"message": "Token is invalid!", "error": str(e)}), 401
        return f(current, *args, **kwargs)
    return decorated

# -----------------
# Routes - Public
# -----------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        if not name or not email or not password:
            flash("Please fill all required fields.", "danger")
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "warning")
            return redirect(url_for('register'))
        user = User(name=name, email=email)
        user.set_password(password)
        # Make the first registered user an admin for convenience
        if User.query.count() == 0:
            user.role = 'admin'
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please login.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid credentials.", "danger")
            return redirect(url_for('login'))
        login_user(user)
        flash("Logged in successfully.", "success")
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for('index'))

# Serve uploaded images
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# -----------------
# Dashboard & Product CRUD (protected)
# -----------------
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/products')
@login_required
def products_list():
    # search & pagination
    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    query = Product.query
    if q:
        query = query.filter(Product.title.ilike(f'%{q}%'))
    pagination = query.order_by(Product.created_at.desc()).paginate(page=page, per_page=app.config['ITEMS_PER_PAGE'], error_out=False)
    items = pagination.items
    return render_template('products_list.html', products=items, pagination=pagination, q=q)

@app.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '')
        price = float(request.form.get('price') or 0)
        image_file = request.files.get('image', None)

        filename = None
        if image_file and image_file.filename != '':
            if allowed_file(image_file.filename):
                filename = secure_filename(f"{datetime.utcnow().timestamp()}_{image_file.filename}")
                save_path = os.path.join(app.config['UPLOAD_FOLDER'])
                os.makedirs(save_path, exist_ok=True)
                image_file.save(os.path.join(save_path, filename))
            else:
                flash("File type not allowed.", "warning")
                return redirect(url_for('add_product'))

        product = Product(title=title, description=description, price=price, image=filename)
        db.session.add(product)
        db.session.commit()
        flash("Product added.", "success")
        return redirect(url_for('products_list'))
    return render_template('product_form.html', action="Add", product=None)

@app.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        product.title = request.form.get('title', '').strip()
        product.description = request.form.get('description', '')
        product.price = float(request.form.get('price') or 0)
        image_file = request.files.get('image', None)
        if image_file and image_file.filename != '':
            if allowed_file(image_file.filename):
                filename = secure_filename(f"{datetime.utcnow().timestamp()}_{image_file.filename}")
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                # optional: remove old file
                if product.image:
                    try:
                        old = os.path.join(app.config['UPLOAD_FOLDER'], product.image)
                        if os.path.exists(old):
                            os.remove(old)
                    except Exception:
                        pass
                product.image = filename
            else:
                flash("File type not allowed.", "warning")
                return redirect(url_for('edit_product', product_id=product_id))
        db.session.commit()
        flash("Product updated.", "success")
        return redirect(url_for('products_list'))
    return render_template('product_form.html', action="Edit", product=product)

@app.route('/products/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    # optional: delete image file
    if product.image:
        try:
            path = os.path.join(app.config['UPLOAD_FOLDER'], product.image)
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted.", "info")
    return redirect(url_for('products_list'))

# -----------------
# Simple admin-only example page
# -----------------
@app.route('/admin')
@login_required
@admin_required
def admin_panel():
    users = User.query.all()
    return render_template('dashboard.html', users=users)

# -----------------
# REST API (JWT)
# -----------------
@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid credentials"}), 401
    payload = {
        "user_id": user.id,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(payload, app.config['JWT_SECRET'], algorithm="HS256")
    return jsonify({"token": token})

@app.route('/api/products', methods=['GET'])
@token_required
def api_get_products(current_user):
    # simple API with optional search & pagination
    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    query = Product.query
    if q:
        query = query.filter(Product.title.ilike(f'%{q}%'))
    pagination = query.order_by(Product.created_at.desc()).paginate(page=page, per_page=app.config['ITEMS_PER_PAGE'], error_out=False)
    items = []
    for p in pagination.items:
        items.append({
            "id": p.id,
            "title": p.title,
            "description": p.description,
            "price": p.price,
            "image_url": url_for('uploaded_file', filename=p.image) if p.image else None,
            "created_at": p.created_at.isoformat()
        })
    return jsonify({
        "products": items,
        "page": pagination.page,
        "pages": pagination.pages,
        "total": pagination.total
    })

# -----------------
# Initialize DB & run
# -----------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

