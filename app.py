from flask import Flask, render_template, request, url_for, flash, redirect, session
import sqlite3
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jRv8sL2pFwXhN5aG9zQ3bU7cY6dA1eR4'

def get_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def get_post(post_id):
    conn = get_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

def get_user_by_email(email):
    conn = get_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    return user

@app.route("/")
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template("index.html", posts=posts)

@app.route("/<int:post_id>")
def post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    post = get_post(post_id)
    return render_template("post.html", post=post)

@app.route("/create", methods=('GET', 'POST'))
def create():
    if 'user_id' not in session:
        flash('Please log in to create a post.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash("Title is required!")
        else:
            conn = get_connection()
            conn.execute("INSERT INTO posts (title, content) VALUES (?, ?)", (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template("create.html")

@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    if 'user_id' not in session:
        flash('Please log in to edit a post.')
        return redirect(url_for('login'))

    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_connection()
            conn.execute('UPDATE posts SET title = ?, content = ? WHERE id = ?', (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template("edit.html", post=post)

@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    if 'user_id' not in session:
        flash('Please log in to delete a post.')
        return redirect(url_for('login'))

    post = get_post(id)
    conn = get_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash(f'"{post["title"]}" was successfully deleted!')
    return redirect(url_for('index'))

@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        is_admin = 'is_admin' in request.form

        if not username or not email or not password:
            flash('All fields are required!')
        else:
            user = get_user_by_email(email)
            if user:
                flash('Email is already registered!')
            else:
                hashed_password = generate_password_hash(password)
                conn = get_connection()
                conn.execute("INSERT INTO users (username, email, password, is_admin) VALUES (?, ?, ?, ?)",
                             (username, email, hashed_password, is_admin))
                conn.commit()
                conn.close()
                return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = get_user_by_email(email)
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            if user['is_admin']:
                return redirect(url_for('admin'))
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password!')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('is_admin', None)
    return redirect(url_for('login'))

@app.route('/admin')
def admin():
    if 'user_id' not in session or not session.get('is_admin'):
        abort(403)

    conn = get_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return render_template('admin.html', users=users)

if __name__ == "__main__":
    app.run(debug=True)
