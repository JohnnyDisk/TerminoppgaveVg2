from flask import Flask, session, render_template, request, redirect, url_for
import sqlite3
import hashlib
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management
app.permanent_session_lifetime = timedelta(days=7)  # Hold handlekurven i 7 dager

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
    {'id': 1, 'name': 'Laptop', 'price': 999.99},
    {'id': 2, 'name': 'Smartphone', 'price': 799.99},
    {'id': 3, 'name': 'Wireless Earbuds', 'price': 129.99},
    {'id': 4, 'name': 'Gaming Mouse', 'price': 59.99},
    {'id': 5, 'name': 'Mechanical Keyboard', 'price': 119.99},
    {'id': 6, 'name': '4K Monitor', 'price': 349.99},
    {'id': 7, 'name': 'External Hard Drive', 'price': 89.99},
    {'id': 8, 'name': 'Portable Charger', 'price': 29.99},
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
    session.permanent = True  # Gjestens sesjon vil leve i 7 dager
    if 'guest_cart' not in session:
        session['guest_cart'] = {}
    return render_template('home.html', products=products, guest_cart=session['guest_cart'])

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
    try:
        # Hent antall fra form, standard er 1, og sørg for at det er et heltall
        quantity = request.form.get('quantity', '1')  # Standard er '1' som streng
        quantity = int(quantity)  # Konverter til heltall
        if quantity < 1:  # Unngå negative tall og null
            quantity = 1
    except (ValueError, TypeError) as e:
        print(f"Feil med quantity: {e}")  # Debug-linje for å vise hva som gikk galt
        quantity = 1  # Hvis konverteringen mislykkes, sett den til 1

    user_id = session.get('user_id')  # Hent bruker-ID fra sesjonen
    
    if user_id is None:  # Brukeren er gjest
        # Initialiser gjestehandlekurv hvis den ikke eksisterer
        if 'guest_cart' not in session:
            session['guest_cart'] = {}

        product_id_str = str(product_id)  # Konverter produkt-ID til streng for å lagre i sesjonen
        
        # Legg til produkt i gjestehandlekurven
        if product_id_str in session['guest_cart']:
            session['guest_cart'][product_id_str] += quantity
        else:
            session['guest_cart'][product_id_str] = quantity
        
        session.modified = True  # Sørg for at endringer blir lagret i sesjonen
        print(f"Gjestekurv etter å ha lagt til: {session['guest_cart']}")  # Debug-linje for å vise handlekurven
        
        return render_template('home.html', products=products, guest_cart=session['guest_cart'])  # Tilbake til produktsiden
    else:
        # Bruker er innlogget, legg til i databasen
        try:
            with sqlite3.connect('cart.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO cart (product_id, user_id, quantity)
                    VALUES (?, ?, ?)
                    ON CONFLICT(product_id, user_id) DO UPDATE SET quantity = quantity + excluded.quantity
                ''', (product_id, user_id, quantity))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Databasefeil: {e}")  # Logg eventuelle databasefeil
        
        return render_template('home.html', products=products, guest_cart=session['guest_cart'])

@app.route('/remove_from_cart/<int:product_id>', methods=['GET', 'POST'])
def remove_from_cart(product_id):
    user_id = session.get('user_id')
    
    if user_id is None:  # Bruker er en gjest
        guest_cart = session.get('guest_cart', {})
        product_id_str = str(product_id)  # Konverter produkt-ID til streng for å matche nøkler i gjestekurven
        if product_id_str in guest_cart:
            del guest_cart[product_id_str]  # Fjern produktet fra gjestekurven
            session['guest_cart'] = guest_cart  # Oppdater sesjonen
            session.modified = True  # Sørg for at endringene lagres
            print(f"Oppdatert gjestekurv etter fjerning: {guest_cart}")  # Debug-linje for å sjekke oppdatert handlekurv
    else:  # Bruker er innlogget
        try:
            with sqlite3.connect('cart.db') as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM cart WHERE product_id = ? AND user_id = ?', (product_id, user_id))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Databasefeil: {e}")  # Logg eventuelle databasefeil
    
    return redirect(url_for('cart'))


@app.route('/cart')
def cart():
    user_id = session.get('user_id')
    cart_items = []
    total_price = 0  # Initialiser totalpris

    if user_id is None:  # Hent elementer fra gjestekurv
        guest_cart = session.get('guest_cart', {})
        print(f"Gjestekurv: {guest_cart}")  # Debug-linje for å sjekke innholdet i gjestekurven

        for product_id_str, quantity in guest_cart.items():
            try:
                product_id = int(product_id_str)  # Konverter produkt-ID til heltall
                quantity = int(quantity)  # Sørg for at antallet er et heltall
            except ValueError:
                print(f"Ugyldig product_id eller quantity: {product_id_str}, {quantity}")  # Debug-linje
                continue  # Hopp over hvis konvertering mislykkes

            # Finn produktet i produktlisten
            product = next((p for p in products if p['id'] == product_id), None)
            if product:
                try:
                    price = float(product['price'])  # Konverter prisen til float
                    print(f"Produkt funnet: {product}, Antall: {quantity}, Pris: {price}")  # Debug-linje
                    cart_items.append((product, quantity))
                    total_price += price * quantity  # Oppdater totalpris
                except (ValueError, TypeError) as e:
                    print(f"Feil ved priskonvertering for produkt {product}: {e}")
            else:
                print(f"Produkt med ID {product_id} ikke funnet.")  # Debug-linje
    else:  # Hent elementer fra brukerdatabasen
        try:
            with sqlite3.connect('cart.db') as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT product_id, quantity FROM cart WHERE user_id = ?', (user_id,))
                items = cursor.fetchall()

                for item in items:
                    try:
                        product_id = int(item[0])  # Sørg for at product_id er et heltall
                        quantity = int(item[1])  # Sørg for at quantity er et heltall
                    except ValueError:
                        print(f"Ugyldige data i databasen: {item}")  # Debug-linje
                        continue  # Hopp over hvis konvertering mislykkes

                    # Finn produktet i produktlisten
                    product = next((p for p in products if p['id'] == product_id), None)
                    if product:
                        try:
                            price = float(product['price'])  # Konverter prisen til float
                            print(f"Produkt funnet i DB: {product}, Antall: {quantity}, Pris: {price}")  # Debug-linje
                            cart_items.append((product, quantity))
                            total_price += price * quantity  # Oppdater totalpris
                        except (ValueError, TypeError) as e:
                            print(f"Feil ved priskonvertering for produkt {product}: {e}")
                    else:
                        print(f"Produkt med ID {product_id} ikke funnet i DB.")  # Debug-linje
        except sqlite3.Error as e:
            print(f"Databasefeil: {e}")  # Logg eventuelle databasefeil

    # Debugging for totalpris
    print(f"Totalpris beregnet: {total_price}")
    print(f"Handlekurv: {cart_items}, Totalpris: {total_price}")  # Debug-linje for å vise innholdet i handlekurven og totalpris
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)



@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    user_id = session.get('user_id')
    cart_items = []
    total_price = 0

    if user_id is None:  # Bruker er en gjest
        guest_cart = session.pop('guest_cart', {})  # Fjern og hent gjestekurven fra sesjonen
        for product_id_str, quantity in guest_cart.items():
            try:
                product_id = int(product_id_str)  # Konverter produkt-ID til heltall
            except ValueError:
                continue  # Hopp over hvis konvertering mislykkes
            product = next((p for p in products if p['id'] == product_id), None)
            if product:
                total_price += product['price'] * quantity
                cart_items.append((product, quantity))
        session.modified = True  # Sørg for at endringene lagres
        print("Gjestekurv er slettet etter utsjekking.")  # Debug-linje
    else:  # Bruker er innlogget
        try:
            with sqlite3.connect('cart.db') as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT product_id, quantity FROM cart WHERE user_id = ?', (user_id,))
                items = cursor.fetchall()
                for item in items:
                    product_id = int(item[0])
                    quantity = int(item[1])
                    product = next((p for p in products if p['id'] == product_id), None)
                    if product:
                        total_price += product['price'] * quantity
                        cart_items.append((product, quantity))
                cursor.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Databasefeil: {e}")  # Logg eventuelle databasefeil
    
    return render_template('checkout.html', cart_items=cart_items, total_price=total_price)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
