from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Database setup
def init_db():
    with sqlite3.connect('cart.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cart (
                product_id INTEGER PRIMARY KEY,
                quantity INTEGER NOT NULL
            )
        ''')
        conn.commit()

# Call the database initialization function
init_db()

# Sample product data
products = [
    {'id': 1, 'name': 'Product 1', 'price': 10.00},
    {'id': 2, 'name': 'Product 2', 'price': 15.00},
    {'id': 3, 'name': 'Product 3', 'price': 20.00},
]

@app.route('/')
def home():
    return render_template('home.html', products=products)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))  # Get quantity from form, default to 1
    with sqlite3.connect('cart.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO cart (product_id, quantity)
            VALUES (?, ?)
            ON CONFLICT(product_id) DO UPDATE SET quantity = quantity + excluded.quantity
        ''', (product_id, quantity))
        conn.commit()
    return redirect(url_for('home'))

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    with sqlite3.connect('cart.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM cart WHERE product_id = ?', (product_id,))
        conn.commit()
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    cart_items = []
    with sqlite3.connect('cart.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT product_id, quantity FROM cart')
        items = cursor.fetchall()
        for product in products:
            product_id = product['id']
            for item in items:
                if item[0] == product_id:
                    cart_items.append((product, item[1]))  # Append product and its quantity
    return render_template('cart.html', cart_items=cart_items)

@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

if __name__ == '__main__':
    app.run(debug=True)
