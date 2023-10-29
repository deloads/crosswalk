from flask import Flask, render_template, request, redirect, url_for, g, session
import mysql.connector

app = Flask(__name__, static_url_path='/static')

app.secret_key = 'your_secret_key_here'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'crosswalk'

def sort_blog_array(blog):
    new_blog = []

    for b in blog:
        if b['status'] == 'started':
            new_blog.append(b)
    for b in blog:
        if b['status'] == 'not started':
            new_blog.append(b)
    for b in blog:
        if b['status'] == 'done':
            new_blog.append(b)

    return new_blog

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
            session['username'] = username
            return redirect(url_for('dev'))
    return render_template('mainhub/login.html',title='login',log=session)

#devplace
@app.route('/dev')
def dev():
    if 'logged_in' in session and session['logged_in']:
        status = request.args.get('status')
        id = request.args.get('id')
        if status:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(f"UPDATE `work` SET `status`='{status}' WHERE id ={id}")
            db.commit()
            cursor.close()
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM `work` WHERE user = '{session['username']}'")
        blogs = cursor.fetchall()
        cursor.close()
        blogs = sort_blog_array(blogs)
        return render_template('devhub/index.html',title='dev space',log=session,blogs=blogs)
    return redirect(url_for('login'))

@app.route('/dev_view')
def dev_view():
    if 'logged_in' in session and session['logged_in']:
        id = request.args.get('id')
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM `work` WHERE id = '{id}'")
        blogs = cursor.fetchall()
        cursor.close()
        blogs = blogs[0]
        return render_template('devhub/dev_view.html',title='dev space',log=session,blogs=blogs)
    return redirect(url_for('login'))

@app.route('/admin',methods=['GET','POST'])
def admin():
    if 'logged_in' in session and session['premisions'] == 'admin':
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT `username` FROM `users`")
        users = cursor.fetchall()
        cursor.close()
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM `work`")
        work = cursor.fetchall()
        cursor.close()
        work = sort_blog_array(work)
        return render_template('devhub/admin.html',title='admin',log=session,users=users,work=work)
    return redirect(url_for('login'))

@app.route('/view',methods=['GET'])
def view():
    if 'logged_in' in session and session['premisions'] == 'admin':
        id = request.args.get('id')
        d = request.args.get('d')
        if d:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(f"DELETE FROM `work` WHERE id ={id}")
            db.commit()
            cursor.close()
            return redirect(url_for('admin'))
        new_username = request.args.get('username')
        if new_username:
            new_status = request.args.get('status')
            new_titel = request.args.get('titel')
            new_content = request.args.get('content')

            db = get_db()
            cursor = db.cursor()
            cursor.execute(f"UPDATE `work` SET `user`='{new_username}',`titel`='{new_titel}',`content`='{new_content}',`status`='{new_status}' WHERE id = {id}")
            db.commit()
            cursor.close()
            return redirect(url_for('admin'))
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM `work` WHERE id = {id}")
        work = cursor.fetchall()
        cursor.close()
        work = work[0]

        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT `username` FROM `users`")
        users = cursor.fetchall()
        cursor.close()
        
        return render_template('devhub/view.html',title=f"view {work['user']}",log=session,work=work,users=users)
    return redirect(url_for('login'))

@app.route('/add')
def add():
    if 'logged_in' in session and session['premisions'] == 'admin':
        name = request.args.get('username')
        if name:
            titel = request.args.get('titel')
            text = request.args.get('content')
            db = get_db()
            cursor = db.cursor()
            cursor.execute(f"INSERT INTO `work`(`user`, `titel`, `content`, `status`) VALUES ('{name}','{titel}','{text}','not started')")
            db.commit()
            cursor.close()
            return redirect(url_for('admin'))
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT `username` FROM `users`")
        users = cursor.fetchall()
        cursor.close()
        
        return render_template('devhub/add.html',title='add',log=session,users=users)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
