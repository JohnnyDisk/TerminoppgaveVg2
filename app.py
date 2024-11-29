from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

# Sample product data
products = [
    {'id': 1, 'name': 'Product 1', 'price': 10.00},
    {'id': 2, 'name': 'Product 2', 'price': 15.00},
    {'id': 3, 'name': 'Product 3', 'price': 20.00},.-,
]

@app.route('/')
def home():
    return render_template('home.html', products=products)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = []
    
    session['cart'].append(product_id)
    session.modified = True
    return redirect(url_for('home'))

@app.route('/cart')
def cart():
    cart_items = [product for product in products if product['id'] in session.get('cart', [])]
    return render_template('cart.html', cart_items=cart_items)

@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

if __name__ == '__main__':
    app.run(debug=True)