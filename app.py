from flask import Flask, render_template, request, redirect, url_for, g, session
import mysql.connector

app = Flask(__name__)

app.secret_key = 'your_secret_key_here'

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
    return render_template('mainhub/index.html',title='home',log=session)

@app.route('/about')
def about():
    return render_template('mainhub/about.html',title='about',log=session)


@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute(f"SELECT `password`, `premisions` FROM `users` WHERE username = '{username}'")
        data = cursor.fetchall()
        cursor.close()
        if password == data[0]['password']:
            session['logged_in'] = True
            session['premisions'] = data[0]['premisions']
            return redirect(url_for('dev'))
    return render_template('mainhub/login.html',title='login',log=session)

#devplace
@app.route('/dev')
def dev():
    if 'logged_in' in session and session['logged_in']:
        return render_template('devhub/index.html',title='home',log=session)
    return redirect(url_for('login'))


#@app.route('/add', methods=['POST'])
#def add_data():
#    if request.method == 'POST':
#        data = request.form['data_to_add']
#        db = get_db()
#        cursor = db.cursor()
#        cursor.execute('INSERT INTO your_table_name (column_name) VALUES (%s)', (data,))
#        db.commit()
#        cursor.close()
#        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
