from flask import Flask, render_template, request, redirect, url_for, g
import mysql.connector

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'crosswalk'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            cursor = db.cursor()
            cursor.execute(f.read(), multi=True)
            cursor.close()
            db.commit()

@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM `users` WHERE 1')
    data = cursor.fetchall()
    cursor.close()
    return render_template('index.html', data=data)

@app.route('/add', methods=['POST'])
def add_data():
    if request.method == 'POST':
        data = request.form['data_to_add']
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO your_table_name (column_name) VALUES (%s)', (data,))
        db.commit()
        cursor.close()
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
