from flask import Flask, session, render_template, request, redirect, url_for
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

# Database setup
def init_db():
    with sqlite3.connect('cart.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cart (
                product_id INTEGER,
                user_id INTEGER,
                quantity INTEGER NOT NULL,
                PRIMARY KEY (product_id, user_id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        conn.commit()

# Drop the existing cart table if it exists
with sqlite3.connect('cart.db') as conn:
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS cart')
    conn.commit()

# Call the database initialization function
init_db()

# Sample product data
products = [
    {'id': 1, 'name': 'Sko', 'price': 10.00},
    {'id': 2, 'name': 'Jakke', 'price': 15.00},
    {'id': 3, 'name': 'Lue', 'price': 20.00},
]

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Server-side validation
        if len(username) < 3:
            return "Username must be at least 3 characters long", 400
        if len(password) < 7:
            return "Password must be more than 6 characters long", 400
        if password != confirm_password:
            return "Passwords do not match", 400

        # Hash password after validation
        hashed_password = hash_password(password)
        
        with sqlite3.connect('cart.db') as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
                conn.commit()
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                return "Username already exists", 400
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
        with sqlite3.connect('cart.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users WHERE username = ? AND password = ?', (username, password))
            user = cursor.fetchone()
            if user:
                session['user_id'] = user[0]
                return redirect(url_for('home'))
            else:
                return "Invalid credentials", 400
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/')
def home():
    return render_template('home.html', products=products)

@app.route('/product/<int:product_id>')
def product_page(product_id):
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        return "Product not found", 404  # Return 404 if product doesn't exist
    
    # Add the image path
    product['image'] = f'/static/images/product_{product_id}.jpg'
    return render_template('product.html', product=product)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    user_id = session.get('user_id')
    quantity = int(request.form.get('quantity', 1))  # Get quantity from form, default to 1

    if user_id is None:
        # Guest cart functionality
        if 'guest_cart' not in session:
            session['guest_cart'] = {}
        if product_id in session['guest_cart']:
            session['guest_cart'][product_id] += quantity
        else:
            session['guest_cart'][product_id] = quantity
        return redirect(url_for('home'))
    else:
        with sqlite3.connect('cart.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO cart (product_id, user_id, quantity)
                VALUES (?, ?, ?)
                ON CONFLICT(product_id, user_id) DO UPDATE SET quantity = quantity + excluded.quantity
            ''', (product_id, user_id, quantity))
            conn.commit()
    return redirect(url_for('home'))

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    user_id = session.get('user_id')
    if user_id is None:
        # Remove from guest cart
        if 'guest_cart' in session and product_id in session['guest_cart']:
            del session['guest_cart'][product_id]
            return redirect(url_for('cart'))
    else:
        with sqlite3.connect('cart.db') as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM cart WHERE product_id = ? AND user_id = ?', (product_id, user_id))
            conn.commit()
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    user_id = session.get('user_id')
    cart_items = []
    if user_id is None:
        # Retrieve items from guest cart
        guest_cart = session.get('guest_cart', {})
        for product_id, quantity in guest_cart.items():
            product = next((p for p in products if p['id'] == product_id), None)
            if product:
                cart_items.append((product, quantity))
    else:
        with sqlite3.connect('cart.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT product_id, quantity FROM cart WHERE user_id = ?', (user_id,))
            items = cursor.fetchall()
            for product in products:
                product_id = product['id']
                for item in items:
                    if item[0] == product_id:
                        cart_items.append((product, item[1]))  # Append product and its quantity
    return render_template('cart.html', cart_items=cart_items)

@app.route('/checkout')
def checkout():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login'))
    
    with sqlite3.connect('cart.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
        conn.commit()
    return render_template('checkout.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)