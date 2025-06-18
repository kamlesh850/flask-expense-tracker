from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = '12112'  # Used for session management

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Kamleshk@1'
app.config['MYSQL_DB'] = 'expense_tracker'

mysql = MySQL(app)

# Home Page
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

# Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        mysql.connection.commit()
        cur.close()
        
        return redirect(url_for('login'))
    return render_template('register.html')

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_input = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[2], password_input):
            session['username'] = username
            session['user_id'] = user[0]
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Dashboard Page
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()

    # Fetch all expenses for the user
    cur.execute("SELECT * FROM expenses WHERE user_id = %s", (user_id,))
    expenses = cur.fetchall()

    # Calculate total expenses
    cur.execute("SELECT SUM(amount) FROM expenses WHERE user_id = %s", (user_id,))
    total = cur.fetchone()[0]
    total = total if total else 0.0

    cur.close()
    return render_template('dashboard.html', expenses=expenses, total=total, username=session['username'])

# Add Expense
@app.route('/add_expense', methods=['POST'])
def add_expense():
    if 'username' not in session:
        return redirect(url_for('login'))

    title = request.form['title']
    amount = request.form['amount']
    user_id = session['user_id']

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO expenses (user_id, title, amount) VALUES (%s, %s, %s)", (user_id, title, amount))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('dashboard'))

# UPDATE Expense
@app.route('/update_expense/<int:expense_id>', methods=['GET', 'POST'])
def update_expense(expense_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        title = request.form['title']
        amount = request.form['amount']
        cur.execute("UPDATE expenses SET title = %s, amount = %s WHERE id = %s AND user_id = %s", (title, amount, expense_id, session['user_id']))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('dashboard'))
    else:
        cur.execute("SELECT * FROM expenses WHERE id = %s AND user_id = %s", (expense_id, session['user_id']))
        expense = cur.fetchone()
        cur.close()
        if expense:
            return render_template('update_expense.html', expense=expense)
        else:
            return "Expense not found", 404

# Delete Expense
@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM expenses WHERE id = %s AND user_id = %s", (expense_id, session['user_id']))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('dashboard'))



if __name__ == '__main__':
    app.run(debug=True)
