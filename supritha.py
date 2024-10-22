from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('chocolate_house.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flavors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            seasonal BOOLEAN NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            quantity INTEGER NOT NULL CHECK (quantity >= 0)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customer_suggestions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            flavor TEXT NOT NULL,
            allergies TEXT
        )
    ''')

    conn.commit()
    conn.close()


create_tables()



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add_flavor', methods=['POST'])
def add_flavor():
    data = request.get_json()

    if not data or 'name' not in data or 'seasonal' not in data:
        return jsonify({'error': 'Invalid data. "name" and "seasonal" fields are required.'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO flavors (name, seasonal) VALUES (?, ?)', (data['name'], data['seasonal']))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Flavor already exists'}), 409
    finally:
        conn.close()

    return jsonify({'message': 'Flavor added successfully'}), 20
@app.route('/view_flavors', methods=['GET'])
def view_flavors():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM flavors')
    flavors = cursor.fetchall()
    conn.close()

    return jsonify([{'id': f['id'], 'name': f['name'], 'seasonal': bool(f['seasonal'])} for f in flavors])



@app.route('/add_ingredient', methods=['POST'])
def add_ingredient():
    data = request.get_json()

    if not data or 'name' not in data or 'quantity' not in data:
        return jsonify({'error': 'Invalid data. "name" and "quantity" fields are required.'}), 400

    if not isinstance(data['quantity'], int) or data['quantity'] < 0:
        return jsonify({'error': 'Invalid quantity. It must be a non-negative integer.'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO ingredients (name, quantity) VALUES (?, ?)', (data['name'], data['quantity']))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Ingredient already exists'}), 409
    finally:
        conn.close()

    return jsonify({'message': 'Ingredient added successfully'}), 201



@app.route('/view_ingredients', methods=['GET'])
def view_ingredients():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ingredients')
    ingredients = cursor.fetchall()
    conn.close()

    return jsonify([{'id': i['id'], 'name': i['name'], 'quantity': i['quantity']} for i in ingredients])
@app.route('/add_customer_suggestion', methods=['POST'])
def add_customer_suggestion():
    data = request.get_json()

    if not data or 'flavor' not in data:
        return jsonify({'error': 'Invalid data. "flavor" field is required.'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('INSERT INTO customer_suggestions (flavor, allergies) VALUES (?, ?)',
                   (data['flavor'], data.get('allergies')))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Customer suggestion added successfully'}), 201



@app.route('/view_customer_suggestions', methods=['GET'])
def view_customer_suggestions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM customer_suggestions')
    suggestions = cursor.fetchall()
    conn.close()

    return jsonify([{'id': s['id'], 'flavor': s['flavor'], 'allergies': s['allergies']} for s in suggestions])


if __name__ == '__main__':
    app.run(debug=True)