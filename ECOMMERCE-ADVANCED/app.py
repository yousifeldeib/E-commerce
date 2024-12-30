from flask import Flask, request, jsonify, render_template ,  session, redirect, url_for
from werkzeug.security import check_password_hash , generate_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'


def get_db_connection():
    conn = sqlite3.connect('ecommerce.db')
    conn.row_factory = sqlite3.Row  
    return conn


@app.route('/')
def index():
    
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')  
    return render_template('index.html', user_id=user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            return jsonify({"status": "error", "message": "Email and password are required."}), 400

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM User WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):  
            session['user_id'] = user['id']  
            return jsonify({"status": "success", "redirect_url": url_for('index')})
        else:
            return jsonify({"status": "error", "message": "Invalid email or password."}), 401

    return render_template('Login.html')


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.form['product_id']
    user_id = session.get('user_id')  
    if not user_id:
        return jsonify({"status": "error", "message": "Please log in to add items to your cart."}), 401

    conn = get_db_connection()
    existing_product = conn.execute('SELECT * FROM Cart WHERE user_id = ? AND product_id = ?', (user_id, product_id)).fetchone()

    if existing_product:
       
        conn.execute('UPDATE Cart SET quantity = quantity + 1 WHERE user_id = ? AND product_id = ?', (user_id, product_id))
    else:
        
        conn.execute('INSERT INTO Cart (user_id, product_id, quantity) VALUES (?, ?, ?)', (user_id, product_id, 1))
    conn.commit()
    conn.close()

    return jsonify({"status": "success", "message": "Product added to cart!"})

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not username or not email or not password:
            
            return jsonify({"status": "error", "message": "All fields are required!"})

        conn = get_db_connection()
        try:
            
            hashed_password = generate_password_hash(password)

            
            conn.execute(
                'INSERT INTO User (username, email, password) VALUES (?, ?, ?)',
                (username, email, hashed_password)
            )
            conn.commit()
            message = {"status": "success", "message": "Signup successful! You can now log in."}
        except sqlite3.IntegrityError:
            message = {"status": "error", "message": "Email already exists. Please use a different email."}
        finally:
            conn.close()

        return jsonify(message)

    return render_template('signup.html')


@app.route('/products')
def products():
    conn = get_db_connection()
    products = conn.execute('SELECT p.name, c.name AS category, p.price, p.image_path FROM Products p JOIN Categories c ON p.category_id = c.id').fetchall()
    conn.close()
    return render_template('products.html', products=products)


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form['query'].strip()
        conn = get_db_connection()
        product = conn.execute('''
            SELECT p.name AS product_name, c.name AS category_name, c.id AS category_id
            FROM Products p
            JOIN Categories c ON p.category_id = c.id
            WHERE p.name LIKE ?
        ''', (f"%{query}%",)).fetchone()
        conn.close()

        if product:
            return jsonify({
                "status": "success",
                "message": f"Product found in category {product['category_name']}",
                "redirect_url": f"/category/{product['category_id']}"
            })
        else:
            return jsonify({"status": "error", "message": "No matching product found."}), 404

    return render_template('search.html')

@app.route('/category/<int:category_id>')
def category(category_id):
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM Products WHERE category_id = ?', (category_id,)).fetchall()
    category = conn.execute('SELECT name FROM Categories WHERE id = ?', (category_id,)).fetchone()
    conn.close()

    if not category:
        return "Category not found", 404

    return render_template('category.html', category=category, products=products)
@app.route('/aboutus', endpoint='aboutus')
def aboutus():
    return render_template('aboutus.html')
@app.route('/favorites', methods=['POST'])
def add_to_favorites():
    user_id = request.form['user_id']
    product_id = request.form['product_id']

    conn = get_db_connection()
    conn.execute('INSERT INTO Favorites (user_id, product_id) VALUES (?, ?)', (user_id, product_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Product added to favorites!"})



@app.route('/addtofavourite', endpoint='add_to_favorite')
def add_to_favorite():
    return render_template('addtofavorite.html')

@app.route('/home_and_kitchen')
def home_and_kitchen():
    conn = get_db_connection()
    products = conn.execute('''
        SELECT id, name, price, image_path
        FROM Products
        WHERE category_id = (SELECT id FROM Categories WHERE name = 'Home and Kitchen')
    ''').fetchall()
    conn.close()

    # Convert rows to dictionaries
    products = [dict(row) for row in products]

    return render_template('homeandkitchen.html', products=products)

@app.route('/electronics')
def electronics():
    conn = get_db_connection()
    products = conn.execute('''
        SELECT p.name, p.price, p.image_path, c.name AS category
        FROM Products p
        JOIN Categories c ON p.category_id = c.id
        WHERE c.name = 'Electronics'
    ''').fetchall()
    conn.close()

    if products:
        return render_template('electronics.html', products=products)
    else:
        return render_template('electronics.html', message="No products available in this category.")

@app.route('/toys_and_games')
def toys_and_games():
    conn = get_db_connection()
    products = conn.execute('''
        SELECT p.name, p.price, p.image_path, c.name AS category
        FROM Products p
        JOIN Categories c ON p.category_id = c.id
        WHERE c.name = 'Toys and Games'
    ''').fetchall()
    conn.close()

    if products:
        return render_template('toys_and_games.html', products=products)
    else:
        return render_template('toys_and_games.html', message="No products available in this category.")



@app.route('/fashion')
def fashion():
    conn = get_db_connection()
    products = conn.execute('''
        SELECT p.name, p.price, p.image_path, c.name AS category
        FROM Products p
        JOIN Categories c ON p.category_id = c.id
        WHERE c.name = 'Fashion'
    ''').fetchall()
    conn.close()

    if products:
        return render_template('fashion.html', products=products)
    else:
        return render_template('fashion.html', message="No products available in this category.")


@app.route('/sportsandoutdoor')
def sports_and_outdoor():
    conn = get_db_connection()
    products = conn.execute('''
        SELECT p.name, p.price, p.image_path, c.name AS category
        FROM Products p
        JOIN Categories c ON p.category_id = c.id
        WHERE c.name = 'Sports and Outdoor'
    ''').fetchall()
    conn.close()

    if products:
        return render_template('sportsandoutdoor.html', products=products)
    else:
        return render_template('sportsandoutdoor.html', message="No products available in this category.")

@app.route('/profile/<int:user_id>')
def profile(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM User WHERE id = ?', (user_id,)).fetchone()
    conn.close()

    if not user:
        return "User not found", 404

    return render_template('profile.html', user=user)


    
@app.route('/cart')
def cart():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    conn = get_db_connection()
    cart_items = conn.execute('''
        SELECT p.name, p.price, p.image_path
        FROM Cart c
        JOIN Products p ON c.product_id = p.id
        WHERE c.user_id = ?
    ''', (user_id,)).fetchall()
    conn.close()

   
    total_price = sum(item['price'] for item in cart_items)

    return render_template('cart.html', cart_items=cart_items, total_price=total_price)



if __name__ == '__main__':
    app.run(debug=True)

@app.route('/aboutus')
def about_us():
    return render_template('aboutus.html')