    # E-Commerce Web Application

A full-featured e-commerce web application built with Flask, featuring user authentication, product catalog, shopping cart functionality, and checkout system. The application supports both guest and authenticated user shopping experiences.

## Features

### User Authentication
- Secure user registration and login system
- Password hashing using SHA-256
- Session management with 7-day persistence
- Guest shopping capability

### Product Management
- Dynamic product catalog
- Detailed product pages with images
- Product information including name and price
- Product image integration

### Shopping Cart
- Add/remove products functionality
- Quantity management
- Persistent cart for both guests and authenticated users
- Real-time cart total calculation
- Database-backed cart for authenticated users
- Session-based cart for guest users

### Checkout System
- Secure checkout process
- Order summary
- Cart clearing after successful checkout
- Total price calculation

## Technical Stack

- **Backend**: Python Flask
- **Database**: SQLite3
- **Frontend**: HTML, CSS
- **Session Management**: Flask Session
- **Security**: SHA-256 password hashing

## Project Structure

```
TerminoppgaveVg2/
│
├── app.py                 # Main Flask application
├── cart.db               # SQLite database
│
├── static/               # Static files
│   ├── styles.css        # CSS styles
│   └── images/           # Product images
│       └── product_*.jpg # Product images
│
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── home.html         # Homepage
│   ├── login.html        # Login page
│   ├── signup.html       # Registration page
│   ├── product.html      # Product details
│   ├── cart.html         # Shopping cart
│   └── checkout.html     # Checkout page
│
└── README.md             # Project documentation
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
```

### Cart Table
```sql
CREATE TABLE cart (
    product_id INTEGER,
    user_id INTEGER,
    quantity INTEGER NOT NULL,
    PRIMARY KEY (product_id, user_id),
    FOREIGN KEY (user_id) REFERENCES users (id)
)
```

## Setup and Installation

1. Ensure Python is installed on your system
2. Clone the repository
3. Install required dependencies:
   ```bash
   pip install flask
   ```
4. Run the application:
   ```bash
   python app.py
   ```
5. Access the application at `http://localhost:5000`

## Security Features

- Password hashing using SHA-256
- Session-based authentication
- SQL injection prevention using parameterized queries
- CSRF protection through Flask's session management
- Input validation for user registration

## User Guide

### Registration
- Username must be at least 3 characters long
- Password must be more than 6 characters long
- Passwords must match during confirmation

### Shopping
1. Browse products on the homepage
2. Click on products to view details
3. Add products to cart with desired quantity
4. Review cart contents
5. Proceed to checkout

### Cart Management
- Add products with specific quantities
- Remove products from cart
- View real-time cart total
- Cart persists for 7 days

## Development Notes

- Debug mode is enabled in development
- Server runs on host '0.0.0.0' and port 5000
- Guest cart data is stored in session
- Authenticated user cart data is stored in SQLite database
