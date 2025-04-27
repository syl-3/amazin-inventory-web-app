import sqlite3

def init_db():
    conn = sqlite3.connect("inventory.db")
    c = conn.cursor()

    # Drop existing tables
    c.execute("DROP TABLE IF EXISTS users")
    c.execute("DROP TABLE IF EXISTS products")
    c.execute("DROP TABLE IF EXISTS likes")
    c.execute("DROP TABLE IF EXISTS orders")

    # Users table
    c.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    # Products table (includes image & description)
    c.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            category TEXT DEFAULT 'Grocery',
            image_url TEXT,
            description TEXT
        )
    """)

    # Likes table
    c.execute("""
        CREATE TABLE likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            UNIQUE(user_id, product_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    # Orders table
    c.execute("""
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Default users
    users = [
        ("ceo", "secret", "CEO"),
        ("manager1", "1234", "Manager"),
        ("emily", "pass", "Customer")
    ]
    c.executemany("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", users)

    # Products
    products = [
        # Grocery
        ("Apples", 0.99, 20, "Grocery", "https://upload.wikimedia.org/wikipedia/commons/1/15/Red_Apple.jpg", "Fresh, crisp apples perfect for a healthy snack."),
        ("Bananas", 0.59, 15, "Grocery", "https://upload.wikimedia.org/wikipedia/commons/8/8a/Banana-Single.jpg", "Sweet bananas loaded with potassium."),
        ("Chips", 2.49, 0, "Grocery", "https://upload.wikimedia.org/wikipedia/commons/6/69/Potato-Chips.jpg", "Classic salty snack — too bad we’re out 😞"),
        ("Orange Juice", 3.99, 12, "Grocery", "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fd/Orange_juice_1.jpg/640px-Orange_juice_1.jpg", "Freshly squeezed, no added sugar."),
        ("Canned Beans", 1.49, 25, "Grocery", "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/Food_-_Beans_%286133%29_--_Smart-Servier.png/640px-Food_-_Beans_%286133%29_--_Smart-Servier.png", "Protein-packed and shelf-stable."),
        ("Granola Bar", 0.99, 15, "Grocery", "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Quaker_Chewy_Granola_Bar_-_chocolate_chip.JPG/640px-Quaker_Chewy_Granola_Bar_-_chocolate_chip.JPG", "Chocolate chip, chewy, and portable."),

        # Apparel
        ("T-Shirt", 14.99, 10, "Apparel", "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/T-shirt_%28drawing%29.jpg/640px-T-shirt_%28drawing%29.jpg", "A classic short-sleeve cotton tee."),
        ("Hoodie", 29.99, 5, "Apparel", "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Sudadera_urban.jpg/640px-Sudadera_urban.jpg", "Urban-style hoodie with front pocket."),
        ("Baseball Cap", 12.99, 8, "Apparel", "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Baseball_cap.png/640px-Baseball_cap.png", "Stylish and adjustable for daily wear."),
        ("Socks (5-pack)", 9.99, 20, "Apparel", "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Custom_Socks.png/640px-Custom_Socks.png", "Soft, breathable, and built to last."),

        # Sports
        ("Soccer Ball", 19.99, 6, "Sports", "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Giant_Soccer_Ball.jpg/640px-Giant_Soccer_Ball.jpg", "Standard ball, great for casual or league play."),
        ("Basketball", 24.99, 6, "Sports", "https://upload.wikimedia.org/wikipedia/commons/7/7a/Basketball.png", "Indoor/outdoor durable grip."),
        ("Yoga Mat", 22.00, 7, "Sports", "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Yoga_mat.jpg/640px-Yoga_mat.jpg", "Non-slip surface, perfect for workouts."),
    ("Water Bottle", 10.00, 30, "Sports", "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Blue_Waters_bottle_no_label.jpg/640px-Blue_Waters_bottle_no_label.jpg", "Clear plastic bottle with blue cap.")
    ]

    c.executemany("INSERT INTO products (name, price, stock, category, image_url, description) VALUES (?, ?, ?, ?, ?, ?)", products)

    conn.commit()
    conn.close()
    print("Database initialized with users, products, likes, and orders.")

if __name__ == "__main__":
    init_db()
