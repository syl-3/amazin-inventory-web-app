# Amazin' Inventory Management Web Application

This project is a lightweight e-commerce storefront simulation built with Flask, SQLite, HTML, and CSS. It provides a full inventory management system, user authentication, shopping cart functionality, and administrative tools.

---

## Features

- Role-based access: Customer, Manager, and CEO
- Secure user registration and login with session handling
- Dynamic inventory management (add, edit, delete products)
- Customer shopping cart with quantity management
- Favorites system allowing users to like/unlike products
- Checkout process with inventory validation
- Personalized order history for customers
- CEO order reporting dashboard
- Product categorization and filtering
- Out-of-stock product visual handling
- Responsive front-end design
- Custom favicon and branding integration

---

## How to Explore (Log-in Credentials with Different Access Levels)

By default, users will not be logged in. Create a new customer account or login with these sample accounts to explore all functionality.

- **Sample Customer (emily / pass):**  
  Browse products, add items to the cart, favorite items, and view your order history.

- **Sample Manager (manager1 / 1234):**  
  Access the Admin Panel to add new products, edit existing products, and manage inventory.

- **Sample CEO (ceo / secret):**  
  Access the Admin Panel AND view ALL customer orders in the CEO Orders Report.

- **Visitors (not logged in):**  
  Can browse all available products but must sign up or log in to interact with the cart, favorites, or admin features.

---

## Technologies Used

- Flask (Python web framework)
- SQLite (relational database)
- HTML5 and CSS3
- Jinja2 (template rendering engine)

---

## Live Site

You can view the live app here:  
[amazin.fly.dev](https://amazin.fly.dev/)

> Note: First load may take a few seconds due to free hosting server spin-up time.

---

## Setup Instructions

To run the application locally:

1. Clone the repository:
    ```bash
    git clone https://github.com/syl-3/amazin-inventory-web-app.git
    cd amazin-inventory-web-app
    ```

2. Set up a virtual environment:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

4. Initialize the database:
    ```bash
    python init_db.py
    ```

5. Start the Flask development server:
    ```bash
    python app.py
    ```

6. Access the application at:
    ```
    http://localhost:5000
    ```

---

## Future Improvements

- Enhanced mobile responsiveness
- Customer product review system
- Administrative order management features

---

## License

This project is intended for educational and portfolio use only.
